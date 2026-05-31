from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from fastapi import APIRouter, HTTPException, Query

from app.database import execute, to_float

router = APIRouter(prefix="/predictions", tags=["predictions"])

PRODUCTS = ["Arroz", "Azucar", "Maiz", "Papa", "Soya", "Trigo"]
BASE_MONTH = datetime(2024, 1, 1)


def get_month_idx(year: int, month: int) -> int:
    delta = (year - BASE_MONTH.year) * 12 + (month - BASE_MONTH.month)
    return delta + 1


def calculate_seasonal_factor(product: str, month: int) -> float:
    rows = execute(
        """
        SELECT MONTH(c.created_at) AS mes, SUM(c.kilos) AS total_kg
        FROM commitments c
        JOIN lots l ON l.id = c.lot_id
        WHERE l.product = %s
        GROUP BY MONTH(c.created_at)
        """,
        (product,),
    )
    if not rows or len(rows) < 3:
        return 1.0

    monthly_totals = {int(r["mes"]): to_float(r["total_kg"]) for r in rows}
    if month not in monthly_totals:
        return 1.0

    avg_total = sum(monthly_totals.values()) / len(monthly_totals)
    if avg_total == 0:
        return 1.0

    return monthly_totals[month] / avg_total


def get_product_metrics(product: str) -> dict:
    lots = execute(
        """
        SELECT id, target_kilos, current_kilos, base_price
        FROM lots
        WHERE product = %s AND status = 'active'
        """,
        (product,),
    )

    if not lots:
        return {
            "precio_promedio_bs_kg": 0.0,
            "n_lotes_activos": 0,
            "tasa_completado": 0.0,
            "demanda_total_kg": 0.0,
            "demanda_promedio_por_lote_kg": 0.0,
        }

    precios = [to_float(l["base_price"]) for l in lots]
    precio_promedio = sum(precios) / len(precios) if precios else 0.0

    tasas = []
    for l in lots:
        target = to_float(l["target_kilos"])
        current = to_float(l["current_kilos"])
        if target > 0:
            tasas.append(current / target)
    tasa_completado = sum(tasas) / len(tasas) if tasas else 0.0

    lot_ids = [l["id"] for l in lots]
    placeholders = ",".join(["%s"] * len(lot_ids))
    commitments = execute(
        f"""
        SELECT SUM(kilos) AS total_kg, COUNT(*) AS n_commitments
        FROM commitments
        WHERE lot_id IN ({placeholders})
        """,
        tuple(lot_ids),
        fetchone=True,
    )

    demanda_total = to_float(commitments["total_kg"]) if commitments and commitments["total_kg"] else 0.0
    n_lotes = len(lots)
    demanda_promedio = demanda_total / n_lotes if n_lotes > 0 else 0.0

    return {
        "precio_promedio_bs_kg": precio_promedio,
        "n_lotes_activos": n_lotes,
        "tasa_completado": tasa_completado,
        "demanda_total_kg": demanda_total,
        "demanda_promedio_por_lote_kg": demanda_promedio,
    }


def build_features(product: str, year: int, month: int, metrics: dict) -> np.ndarray:
    mes_idx = get_month_idx(year, month)
    semestre = 1 if month <= 6 else 2
    trimestre = ((month - 1) // 3) + 1
    factor_estacional = calculate_seasonal_factor(product, month)
    mes_sin = np.sin(2 * np.pi * month / 12)
    mes_cos = np.cos(2 * np.pi * month / 12)

    return np.array([[
        month,
        semestre,
        trimestre,
        mes_idx,
        metrics["precio_promedio_bs_kg"],
        metrics["n_lotes_activos"],
        metrics["tasa_completado"],
        factor_estacional,
        metrics["demanda_total_kg"],
        metrics["demanda_promedio_por_lote_kg"],
        mes_sin,
        mes_cos,
    ]])


def load_model(product: str):
    model_path = Path(__file__).parent.parent.parent / "saved_models" / product / "model.joblib"
    if not model_path.exists():
        raise HTTPException(status_code=404, detail=f"Modelo no encontrado para {product}")
    return joblib.load(model_path)


def predict_demand(product: str, year: int, month: int, current_demand: float | None = None) -> dict:
    metrics = get_product_metrics(product)
    if current_demand is not None:
        metrics["demanda_total_kg"] = current_demand
        metrics["demanda_promedio_por_lote_kg"] = current_demand / max(metrics["n_lotes_activos"], 1)

    features = build_features(product, year, month, metrics)
    model = load_model(product)
    prediction = float(model.predict(features)[0])

    current = metrics["demanda_total_kg"]
    if current > 0:
        variation = ((prediction - current) / current) * 100
    else:
        variation = 0.0

    if variation > 5:
        trend = "ALZA"
    elif variation < -5:
        trend = "BAJA"
    else:
        trend = "ESTABLE"

    return {
        "producto": product,
        "mes": month,
        "anio": year,
        "demanda_estimada_kg": round(prediction, 2),
        "demanda_actual_kg": round(current, 2),
        "variacion_porcentual": round(variation, 2),
        "tendencia": trend,
    }


@router.get("/{product}")
def get_prediction(
    product: str,
    months: int = Query(1, ge=1, le=12, description="Número de meses a predecir"),
):
    if product not in PRODUCTS:
        raise HTTPException(status_code=400, detail=f"Producto inválido. Use: {', '.join(PRODUCTS)}")

    now = datetime.now()
    predictions = []
    current_demand = None

    for i in range(months):
        target_month = now.month + i
        target_year = now.year
        while target_month > 12:
            target_month -= 12
            target_year += 1

        result = predict_demand(product, target_year, target_month, current_demand)
        predictions.append(result)
        current_demand = result["demanda_estimada_kg"]

    return {
        "producto": product,
        "predicciones": predictions,
    }
