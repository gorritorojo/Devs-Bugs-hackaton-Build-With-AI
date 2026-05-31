import os
import sys

import joblib
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(__file__), "saved_models")

PRODUCTOS = sorted(
    d for d in os.listdir(MODELS_DIR)
    if os.path.isdir(os.path.join(MODELS_DIR, d))
)


def solicitar_float(prompt: str, default: float | None = None) -> float:
    while True:
        if default is not None:
            val = input(f"{prompt} [{default}]: ").strip()
            if val == "":
                return default
        else:
            val = input(f"{prompt}: ").strip()
        try:
            return float(val)
        except ValueError:
            print("  Ingresa un numero valido.")


def solicitar_int(prompt: str, default: int | None = None) -> int:
    while True:
        if default is not None:
            val = input(f"{prompt} [{default}]: ").strip()
            if val == "":
                return default
        else:
            val = input(f"{prompt}: ").strip()
        try:
            return int(val)
        except ValueError:
            print("  Ingresa un numero entero valido.")


def main():
    print("=" * 50)
    print("  CrowdBu y — Prediccion de Demanda")
    print("=" * 50)

    if not PRODUCTOS:
        print(" No hay modelos entrenados en saved_models/")
        print("   Ejecuta primero: python train_model.py")
        sys.exit(1)

    # 1. Elegir producto
    print("\nProductos disponibles:")
    for i, p in enumerate(PRODUCTOS, 1):
        print(f"  {i}. {p}")
    while True:
        try:
            idx = int(input("\nElige producto (numero): ").strip())
            if 1 <= idx <= len(PRODUCTOS):
                producto = PRODUCTOS[idx - 1]
                break
        except ValueError:
            pass
        print(f"  Ingresa un numero entre 1 y {len(PRODUCTOS)}.")

    # 2. Cargar modelo
    pipeline_path = os.path.join(MODELS_DIR, producto, "model.joblib")
    pipeline = joblib.load(pipeline_path)
    print(f"\n Modelo '{producto}' cargado.")

    # 3. Pedir inputs
    print("\n── Ingresa los datos del mes a predecir ──")
    mes = solicitar_int("  Mes del año (1-12)")

    semestre = 1 if mes <= 6 else 2
    trimestre = int((mes - 1) / 3) + 1

    mes_idx = solicitar_int("  Indice acumulado del mes (mes_idx)")
    precio = solicitar_float("  Precio promedio (Bs/kg)")
    n_lotes = solicitar_int("  Numero de lotes activos")
    tasa = solicitar_float("  Tasa de completado (0-1)")
    factor = solicitar_float("  Factor estacional")
    demanda = solicitar_float("  Demanda total (kg)")
    demanda_prom = solicitar_float("  Demanda promedio por lote (kg)")

    mes_sin = np.sin(2 * np.pi * mes / 12)
    mes_cos = np.cos(2 * np.pi * mes / 12)

    # 4. Predecir
    X = np.array([[
        mes, semestre, trimestre, mes_idx,
        precio, n_lotes, tasa, factor,
        demanda, demanda_prom,
        mes_sin, mes_cos,
    ]])
    pred = pipeline.predict(X)[0]

    # 5. Mostrar resultado
    delta = (pred - demanda) / (demanda + 1e-9) * 100
    tendencia = "ALZA" if delta > 5 else ("BAJA" if delta < -5 else "ESTABLE")

    print("\n" + "=" * 50)
    print(f"  PREDICCION PARA {producto.upper()} — Mes {mes:02d}")
    print("=" * 50)
    print(f"  Demanda estimada: {pred:,.0f} kg")
    print(f"  Variacion:        {delta:+.1f}%  →  {tendencia}")
    if delta > 5:
        print("  \n  Recomendacion: Ampliar lotes, la demanda sube.")
    elif delta < -5:
        print("  \n  Recomendacion: Reducir lotes, posible baja.")
    else:
        print("  \n  Recomendacion: Mantener volumen, mercado estable.")


if __name__ == "__main__":
    main()
