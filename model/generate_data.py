import argparse
import math
import os
import random
import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

fake = Faker("es_ES")
random.seed(42)
np.random.seed(42)


def fake_phone() -> str:
    return f"+591 3 {random.randint(300, 399):03d} {random.randint(1000, 9999):04d}"

PRODUCTOS_CONFIG = {
    "Papa": {
        "descripcion": "El alimento base",
        "precio_base_min": 1.50,
        "precio_base_max": 4.50,
        "kilos_lote_min": 2000,
        "kilos_lote_max": 20000,
        "estacionalidad": [
            1.20,
            1.25,
            1.15,
            1.00,
            0.80,
            0.75,
            0.78,
            0.85,
            0.95,
            1.05,
            1.10,
            1.18,
        ],
        "tendencia_anual": 0.05,
    },
    "Maiz": {
        "descripcion": "El motor de la proteína",
        "precio_base_min": 1.20,
        "precio_base_max": 3.50,
        "kilos_lote_min": 3000,
        "kilos_lote_max": 30000,
        "estacionalidad": [
            1.10,
            1.05,
            0.85,
            0.78,
            0.80,
            0.90,
            1.00,
            1.10,
            1.15,
            1.12,
            1.08,
            1.10,
        ],
        "tendencia_anual": 0.06,
    },
    "Arroz": {
        "descripcion": "El cereal del día a día",
        "precio_base_min": 2.50,
        "precio_base_max": 5.00,
        "kilos_lote_min": 2000,
        "kilos_lote_max": 25000,
        "estacionalidad": [
            1.15,
            1.20,
            1.10,
            0.85,
            0.80,
            0.82,
            0.90,
            0.95,
            1.00,
            1.05,
            1.10,
            1.18,
        ],
        "tendencia_anual": 0.04,
    },
    "Soya": {
        "descripcion": "Harina y subproductos para ganadería",
        "precio_base_min": 2.80,
        "precio_base_max": 6.50,
        "kilos_lote_min": 5000,
        "kilos_lote_max": 50000,
        "estacionalidad": [
            1.05,
            1.00,
            0.95,
            0.90,
            0.82,
            0.80,
            0.85,
            1.05,
            1.15,
            1.20,
            1.15,
            1.08,
        ],
        "tendencia_anual": 0.07,
    },
    "Azucar": {
        "descripcion": "Derivado de la Caña",
        "precio_base_min": 2.20,
        "precio_base_max": 4.80,
        "kilos_lote_min": 3000,
        "kilos_lote_max": 40000,
        "estacionalidad": [
            1.20,
            1.18,
            1.15,
            1.10,
            0.90,
            0.82,
            0.80,
            0.82,
            0.88,
            0.92,
            1.00,
            1.12,
        ],
        "tendencia_anual": 0.04,
    },
    "Trigo": {
        "descripcion": "Harina, pan y fideos",
        "precio_base_min": 1.80,
        "precio_base_max": 4.20,
        "kilos_lote_min": 2000,
        "kilos_lote_max": 30000,
        "estacionalidad": [
            1.05,
            1.00,
            0.98,
            0.95,
            0.92,
            0.90,
            0.92,
            1.08,
            1.15,
            1.05,
            0.90,
            1.00,
        ],
        "tendencia_anual": 0.06,
    },
}

AREAS_BOLIVIA = [
    "Andrés Ibáñez",
    "Ángel Sandoval",
    "Chiquitos",
    "Cordillera",
    "Florida",
    "Germán Busch",
    "Guarayos",
    "Ichilo",
    "José Miguel de Velasco",
    "Manuel María Caballero",
    "Ñuflo de Chávez",
    "Obispo Santistevan",
    "Sara",
    "Vallegrande",
    "Warnes",
]

EMPRESAS_PYME = [
    "Mercado Campesino",
    "Distribuidora Los Andes",
    "Abastos del Sur",
    "La Colmena Ltda.",
    "Frescos Bolivia",
    "Comercial Andina",
    "Super Mercado Oriental",
    "Tiendas Campestre",
    "AlimAndes S.R.L.",
    "Bodega El Sol",
    "Minimarket Altiplano",
    "Almacén Don Pepe",
    "Distribuidora Yungas",
    "Comercial Santa Cruz",
    "Abastos Chapare",
]

EMPRESAS_AGRO = [
    "Agro Huanca",
    "Cooperativa Andina",
    "Finca Los Llanos",
    "Productores del Altiplano",
    "Agro Chiquitano",
    "Yungas Fresh",
    "Agro Chapare S.R.L.",
    "Productores del Beni",
    "Agro Valle Ltda.",
    "Cooperativa Agropecuaria Boliviana",
    "Agro Santa Cruz",
    "Productores del Chaco",
    "Granja Los Cedros",
    "Agro Tarija",
]


def generar_usuarios(n_pymes=40, n_agros=25):
    usuarios = []
    for _ in range(n_pymes):
        usuarios.append(
            {
                "id": str(uuid.uuid4()),
                "role": "pyme",
                "contact_name": fake.name(),
                "email": fake.email(),
                "company_name": random.choice(EMPRESAS_PYME)
                + f" {fake.numerify('##')}",
                "phone": fake_phone(),
                "area": random.choice(AREAS_BOLIVIA),
                "products": None,
                "business_size": random.choice(["pequeña", "mediana"]),
            }
        )
    for _ in range(n_agros):
        productos_agro = random.sample(
            list(PRODUCTOS_CONFIG.keys()), k=random.randint(1, 3)
        )
        usuarios.append(
            {
                "id": str(uuid.uuid4()),
                "role": "agro",
                "contact_name": fake.name(),
                "email": fake.email(),
                "company_name": random.choice(EMPRESAS_AGRO)
                + f" {fake.numerify('##')}",
                "phone": fake_phone(),
                "area": random.choice(AREAS_BOLIVIA),
                "products": ", ".join(productos_agro),
                "business_size": random.choice(["pequeña", "mediana", "grande"]),
            }
        )
    return usuarios


def generar_lotes_y_compromisos(usuarios, producto, config, meses, fecha_inicio):
    pymes = [u for u in usuarios if u["role"] == "pyme"]
    agros = [u for u in usuarios if u["role"] == "agro"]
    agros_prod = [u for u in agros if u["products"] and producto in u["products"]]
    if not agros_prod:
        agros_prod = random.sample(agros, k=min(5, len(agros)))

    lotes, compromisos, feature_rows = [], [], []
    precio_base = (config["precio_base_min"] + config["precio_base_max"]) / 2
    lot_counter = 1
    fecha_actual = fecha_inicio

    for mes_idx in range(meses):
        año = fecha_actual.year
        mes = fecha_actual.month
        factor_estacional = config["estacionalidad"][mes - 1]
        factor_tendencia = (1 + config["tendencia_anual"]) ** (mes_idx / 12)
        n_lotes_mes = random.randint(4, 10)

        demanda_total = 0
        precio_sum = 0
        completados = 0

        for _ in range(n_lotes_mes):
            lot_id = f"LOT-{producto[:3].upper()}-{lot_counter:04d}"
            lot_counter += 1

            kilos_obj = random.uniform(
                config["kilos_lote_min"], config["kilos_lote_max"]
            )
            precio = (
                precio_base
                * factor_tendencia
                * factor_estacional
                * random.uniform(0.92, 1.08)
            )
            precio = round(precio, 2)

            dias_pasados = (meses - mes_idx) * 30
            if dias_pasados > 45:
                p_comp = min(0.85 * factor_estacional, 0.97)
                status = "completed" if random.random() < p_comp else "expired"
            else:
                status = random.choice(["active", "completed"])

            tasa_fill = (
                random.uniform(0.90, 1.00)
                if status == "completed"
                else random.uniform(0.20, 0.69)
                if status == "expired"
                else random.uniform(0.40, 0.95)
            )

            kilos_comp = round(kilos_obj * tasa_fill, 2)
            demanda_total += kilos_comp
            precio_sum += precio
            if status == "completed":
                completados += 1

            lotes.append(
                {
                    "id": lot_id,
                    "product": producto,
                    "producer": fake.company(),
                    "target_kilos": round(kilos_obj, 2),
                    "current_kilos": kilos_comp,
                    "base_price": precio,
                    "deadline": (
                        fecha_actual + timedelta(days=random.randint(15, 45))
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "status": status,
                    "created_by": random.choice(agros_prod)["id"],
                    "created_at": fecha_actual.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

            # Compromisos de compra
            n_comp = random.randint(2, min(10, len(pymes)))
            compradores = random.sample(pymes, k=n_comp)
            restantes = kilos_comp
            for i, pyme in enumerate(compradores):
                if restantes <= 0:
                    break
                if i == n_comp - 1:
                    kg = restantes
                else:
                    kg = min(
                        round(
                            random.uniform(0.1, 0.6)
                            * kilos_comp
                            / n_comp
                            * random.uniform(0.8, 1.2),
                            2,
                        ),
                        restantes,
                    )
                restantes -= kg
                compromisos.append(
                    {
                        "id": str(uuid.uuid4()),
                        "lot_id": lot_id,
                        "user_id": pyme["id"],
                        "kilos": max(round(kg, 2), 0.01),
                        "created_at": (
                            fecha_actual + timedelta(days=random.randint(0, 20))
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )

        # Feature row para regresión lineal
        precio_prom = precio_sum / n_lotes_mes
        tasa_comp = completados / n_lotes_mes
        mes_sig_idx = mes % 12
        factor_sig = config["estacionalidad"][mes_sig_idx]
        factor_tend_sig = (1 + config["tendencia_anual"]) ** ((mes_idx + 1) / 12)
        demanda_pred = (
            demanda_total
            * factor_sig
            * factor_tend_sig
            / factor_estacional
            * random.uniform(0.93, 1.07)
        )

        feature_rows.append(
            {
                "año": año,
                "mes": mes,
                "mes_del_año": mes,
                "semestre": 1 if mes <= 6 else 2,
                "trimestre": math.ceil(mes / 3),
                "mes_idx": mes_idx,
                "producto": producto,
                "descripcion_producto": config["descripcion"],
                "precio_promedio_bs_kg": round(precio_prom, 2),
                "n_lotes_activos": n_lotes_mes,
                "tasa_completado": round(tasa_comp, 4),
                "factor_estacional": round(factor_estacional, 4),
                "demanda_total_kg": round(demanda_total, 2),
                "demanda_promedio_por_lote_kg": round(demanda_total / n_lotes_mes, 2),
                "demanda_siguiente_mes_kg": round(demanda_pred, 2),
            }
        )

        fecha_actual += timedelta(days=30)

    return lotes, compromisos, pd.DataFrame(feature_rows)


def main():
    parser = argparse.ArgumentParser(
        description="Generador de datos CrowdBuy — mercado boliviano"
    )
    parser.add_argument(
        "--producto",
        default="TODOS",
        choices=list(PRODUCTOS_CONFIG.keys()) + ["TODOS"],
        help="Producto a generar. TODOS genera los 6 productos (default).",
    )
    parser.add_argument(
        "--meses", type=int, default=50, help="Meses por producto (default: 50)"
    )
    parser.add_argument("--output", default="data/crowdbuy_demo.csv")
    args = parser.parse_args()

    os.makedirs(
        os.path.dirname(args.output) if os.path.dirname(args.output) else ".",
        exist_ok=True,
    )

    productos = (
        list(PRODUCTOS_CONFIG.keys()) if args.producto == "TODOS" else [args.producto]
    )
    usuarios = generar_usuarios(n_pymes=40, n_agros=25)
    fecha_inicio = datetime.now() - timedelta(days=args.meses * 30)

    print("Generando datos CrowdBuy — Mercado Boliviano")
    print(f"   Productos : {len(productos)} ({', '.join(productos)})")
    print(
        f"   Meses c/u : {args.meses}  →  {len(productos) * args.meses} filas totales"
    )
    print(
        f"   Período   : {fecha_inicio.strftime('%Y-%m')} → {datetime.now().strftime('%Y-%m')}\n"
    )

    todos_features, todos_lotes, todos_compromisos = [], [], []

    for producto in productos:
        config = PRODUCTOS_CONFIG[producto]
        lotes, compromisos, df_feat = generar_lotes_y_compromisos(
            usuarios, producto, config, args.meses, fecha_inicio
        )
        todos_features.append(df_feat)
        todos_lotes.extend(lotes)
        todos_compromisos.extend(compromisos)
        precio_med = df_feat["precio_promedio_bs_kg"].mean()
        print(
            f"    {producto:<8} ({config['descripcion']:<35}) "
            f" {len(df_feat)} filas | {len(lotes):>4} lotes | precio med. Bs {precio_med:.2f}/kg"
        )

    df = pd.concat(todos_features, ignore_index=True)

    df.to_csv(args.output, index=False)

    base = os.path.splitext(args.output)[0]
    pd.DataFrame(usuarios).to_csv(f"{base}_usuarios.csv", index=False)
    pd.DataFrame(todos_lotes).to_csv(f"{base}_lotes.csv", index=False)
    pd.DataFrame(todos_compromisos).to_csv(f"{base}_compromisos.csv", index=False)

    print(f"\nCSV principal  : {args.output}")
    print(f"   Filas totales  : {len(df)} | Columnas: {len(df.columns)}")
    print(f"   Lotes          : {len(todos_lotes):,}")
    print(f"   Compromisos    : {len(todos_compromisos):,}")
    print(f"   Usuarios       : {len(usuarios)} (pymes + agros)")

    print("\n Vista previa:")
    print(
        df[
            [
                "año",
                "mes",
                "producto",
                "precio_promedio_bs_kg",
                "demanda_total_kg",
                "demanda_siguiente_mes_kg",
            ]
        ]
        .head(8)
        .to_string(index=False)
    )

    print("\n Precio promedio y demanda media por producto:")
    resumen = (
        df.groupby("producto")
        .agg(
            precio_med=("precio_promedio_bs_kg", "mean"),
            demanda_med=("demanda_total_kg", "mean"),
            filas=("mes_idx", "count"),
        )
        .round(2)
    )
    print(resumen.to_string())


if __name__ == "__main__":
    main()
