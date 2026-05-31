import argparse
import json
import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_COLS = [
    "mes_del_año",  # estacionalidad cíclica (1-12)
    "semestre",  # agrupación semestral
    "trimestre",  # agrupación trimestral
    "mes_idx",  # tendencia lineal acumulada
    "precio_promedio_bs_kg",  # precio de mercado actual
    "n_lotes_activos",  # oferta activa
    "tasa_completado",  # qué tan bien se está llenando la demanda
    "factor_estacional",  # factor estacional del mes
    "demanda_total_kg",  # demanda histórica del mes actual
    "demanda_promedio_por_lote_kg",  # eficiencia por lote
]

TARGET_COL = "demanda_siguiente_mes_kg"


def cargar_datos(csv_path: str, producto: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    if "producto" in df.columns:
        df = df[df["producto"] == producto].copy()
    if df.empty:
        raise ValueError(
            f"No se encontraron datos para el producto '{producto}' en {csv_path}"
        )
    df = df.sort_values("mes_idx").reset_index(drop=True)
    print(f" Datos cargados: {len(df)} meses de historial para '{producto}'")
    return df


def agregar_features_ciclicas(df: pd.DataFrame) -> pd.DataFrame:
    """Codificación seno/coseno para capturar la ciclicidad del mes."""
    df = df.copy()
    df["mes_sin"] = np.sin(2 * np.pi * df["mes_del_año"] / 12)
    df["mes_cos"] = np.cos(2 * np.pi * df["mes_del_año"] / 12)
    return df


def entrenar_y_evaluar(df: pd.DataFrame, output_dir: str, producto: str):
    os.makedirs(output_dir, exist_ok=True)

    df = agregar_features_ciclicas(df)

    # Features finales (incluye las cíclicas)
    feature_cols_final = FEATURE_COLS + ["mes_sin", "mes_cos"]
    feature_cols_final = [c for c in feature_cols_final if c in df.columns]

    X = df[feature_cols_final].values
    y = df[TARGET_COL].values

    # División temporal (80% train / 20% test) — respeta el orden cronológico
    split_idx = int(len(X) * 0.80)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    print("\n División de datos:")
    print(f"   Train: {len(X_train)} meses | Test: {len(X_test)} meses")

    # ── Pipeline: scaler + Ridge (más estable que OLS puro con pocas filas) ──
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=1.0)),
        ]
    )

    pipeline.fit(X_train, y_train)

    # Predicciones
    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)

    # Métricas
    def metricas(y_true, y_pred, label):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-9))) * 100
        print(f"\n Métricas [{label}]:")
        print(f"   R²   : {r2:.4f}")
        print(f"   MAE  : {mae:,.1f} kg")
        print(f"   RMSE : {rmse:,.1f} kg")
        print(f"   MAPE : {mape:.2f}%")
        return {
            "r2": round(r2, 4),
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2),
        }

    m_train = metricas(y_train, y_pred_train, "TRAIN")
    m_test = metricas(y_test, y_pred_test, "TEST")

    # Cross-validation (leave-one-out implícito vía cv=5 en serie temporal)
    cv_scores = cross_val_score(
        pipeline, X_train, y_train, cv=min(5, len(X_train)), scoring="r2"
    )
    print(
        f"\nCross-Val R² (cv={len(cv_scores)}): "
        f"{cv_scores.mean():.4f} ± {cv_scores.std():.4f}"
    )

    # Coeficientes del modelo
    coef = pipeline.named_steps["model"].coef_
    intercept = pipeline.named_steps["model"].intercept_
    importancia = sorted(
        zip(feature_cols_final, coef), key=lambda x: abs(x[1]), reverse=True
    )
    print("\n Importancia de features (por coeficiente absoluto):")
    for feat, c in importancia:
        bar = "█" * int(abs(c) / max(abs(coef)) * 20)
        print(f"   {feat:<35} {c:+10.2f}  {bar}")

    # ── Guardar artefactos ────────────────────────────────────────────────────
    model_path = os.path.join(output_dir, "model.joblib")
    scaler_path = os.path.join(output_dir, "scaler.joblib")

    # Guardar pipeline completo (incluye scaler)
    joblib.dump(pipeline, model_path)
    # Guardar scaler por separado para conveniencia
    joblib.dump(pipeline.named_steps["scaler"], scaler_path)

    print(f"\n Modelo guardado: {model_path}")
    print(f"   Scaler guardado: {scaler_path}")

    # Metadata JSON
    metadata = {
        "producto": producto,
        "entrenado_en": datetime.now().isoformat(),
        "algoritmo": "Ridge Regression (alpha=1.0)",
        "features": feature_cols_final,
        "target": TARGET_COL,
        "n_meses_historial": len(df),
        "split_train_test": "80/20 cronológico",
        "metricas_train": m_train,
        "metricas_test": m_test,
        "cross_val_r2_mean": round(cv_scores.mean(), 4),
        "cross_val_r2_std": round(cv_scores.std(), 4),
        "intercept": round(float(intercept), 4),
        "coeficientes": {
            f: round(float(c), 4) for f, c in zip(feature_cols_final, coef)
        },
        "rango_datos": {
            "demanda_min_kg": round(float(y.min()), 2),
            "demanda_max_kg": round(float(y.max()), 2),
            "demanda_media_kg": round(float(y.mean()), 2),
            "precio_min_bs_kg": round(float(df["precio_promedio_bs_kg"].min()), 2),
            "precio_max_bs_kg": round(float(df["precio_promedio_bs_kg"].max()), 2),
        },
    }

    meta_path = os.path.join(output_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"   Metadata:        {meta_path}")

    # Reporte legible
    report_lines = [
        "=" * 60,
        f"  MODELO DE PREDICCIÓN DE DEMANDA — {producto.upper()}",
        "=" * 60,
        f"  Entrenado: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "  Algoritmo: Ridge Regression",
        f"  Historial: {len(df)} meses",
        "",
        "  MÉTRICAS DE EVALUACIÓN",
        "  ─────────────────────────────────────",
        f"  Train R²:  {m_train['r2']:.4f}",
        f"  Test  R²:  {m_test['r2']:.4f}",
        f"  Test  MAE: {m_test['mae']:,.0f} kg",
        f"  Test  MAPE:{m_test['mape']:.1f}%",
        f"  CV R²:     {cv_scores.mean():.4f} ± {cv_scores.std():.4f}",
        "",
        "  FEATURES MÁS INFLUYENTES",
        "  ─────────────────────────────────────",
    ]
    for feat, c in importancia[:6]:
        report_lines.append(f"  {feat:<35} {c:+.2f}")
    report_lines += [
        "",
        "  CÓMO USAR EL MODELO",
        "  ─────────────────────────────────────",
        "  import joblib, numpy as np",
        "  pipeline = joblib.load('saved_model/model.joblib')",
        "  X_nuevo  = np.array([[mes_del_año, semestre, trimestre,",
        "             mes_idx, precio, n_lotes, tasa, estacional,",
        "             demanda_actual, demanda_prom, mes_sin, mes_cos]])",
        "  prediccion_kg = pipeline.predict(X_nuevo)[0]",
        "",
        "  INTERPRETACIÓN PARA AGROS",
        "  ─────────────────────────────────────",
        "  Si prediccion_kg > demanda_actual * 1.10 → mercado en alza",
        "  → Recomendación: ampliar volumen de lotes el próximo mes",
        "  Si prediccion_kg < demanda_actual * 0.90 → mercado a la baja",
        "  → Recomendación: mantener o reducir lotes; diversificar producto",
        "=" * 60,
    ]

    report_path = os.path.join(output_dir, "report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"   Reporte:         {report_path}")

    # Demo de predicción
    print("\nDemo: predicción para el próximo mes")
    ultimo = df.iloc[-1]
    mes_prox = (int(ultimo["mes_del_año"]) % 12) + 1
    x_prox = np.array(
        [
            [
                mes_prox,
                1 if mes_prox <= 6 else 2,
                int((mes_prox - 1) / 3) + 1,
                int(ultimo["mes_idx"]) + 1,
                float(ultimo["precio_promedio_bs_kg"]) * 1.02,
                int(ultimo["n_lotes_activos"]),
                float(ultimo["tasa_completado"]),
                float(ultimo["factor_estacional"]),
                float(ultimo["demanda_total_kg"]),
                float(ultimo["demanda_promedio_por_lote_kg"]),
                np.sin(2 * np.pi * mes_prox / 12),
                np.cos(2 * np.pi * mes_prox / 12),
            ]
        ]
    )
    pred = pipeline.predict(x_prox)[0]
    delta = (
        (pred - float(ultimo["demanda_total_kg"]))
        / float(ultimo["demanda_total_kg"])
        * 100
    )
    tendencia = "ALZA" if delta > 5 else ("BAJA" if delta < -5 else "ESTABLE")
    print(
        f"   Mes actual  : {int(ultimo['mes_del_año']):02d} | Demanda: {float(ultimo['demanda_total_kg']):,.0f} kg"
    )
    print(
        f"   Mes próximo : {mes_prox:02d} | Predicción: {pred:,.0f} kg  ({delta:+.1f}%)  {tendencia}"
    )
    print(
        f"\n   {'→ Recomendación agro: ampliar lotes, la demanda sube.' if delta > 5 else '→ Recomendación agro: mantener volumen, mercado estable.' if abs(delta) <= 5 else '→ Recomendación agro: precaución, posible baja de demanda.'}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Entrenador de modelo de demanda CrowdBuy"
    )
    parser.add_argument("--input", default="data/crowdbuy_demo.csv")
    parser.add_argument(
        "--producto",
        default="Papa",
        choices=["Papa", "Maiz", "Arroz", "Soya", "Azucar", "Trigo", "TODOS"],
        help="Producto a entrenar. TODOS entrena los 6 de una vez.",
    )
    parser.add_argument(
        "--output",
        default="saved_models",
        help="Directorio raiz. Cada modelo se guarda en <output>/<Producto>/",
    )
    args = parser.parse_args()

    print("=" * 55)
    print("  CrowdBuy — Entrenamiento Modelo Predicción Demanda")
    print("=" * 55)

    productos = (
        ["Papa", "Maiz", "Arroz", "Soya", "Azucar", "Trigo"]
        if args.producto == "TODOS"
        else [args.producto]
    )

    for producto in productos:
        # Directorio propio: saved_models/Papa/, saved_models/Maiz/, etc.
        output_dir = os.path.join(args.output, producto)
        print(f"\n{'─' * 55}")
        df = cargar_datos(args.input, producto)
        entrenar_y_evaluar(df, output_dir, producto)

        print(f"\nGuardado en '{output_dir}/'")
        print("   Estructura:")
        for f in sorted(os.listdir(output_dir)):
            size = os.path.getsize(os.path.join(output_dir, f))
            print(f"   ├── {f}  ({size:,} bytes)")


if __name__ == "__main__":
    main()
