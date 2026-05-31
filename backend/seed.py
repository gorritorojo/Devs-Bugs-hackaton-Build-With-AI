import os
import uuid
import random
import json
from datetime import datetime, timedelta
from decimal import Decimal

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "crowdbuy"),
}

PRODUCTOS_CONFIG = {
    "Papa": {
        "descripcion": "El alimento base",
        "precio_base_min": 1.50,
        "precio_base_max": 4.50,
        "kilos_lote_min": 2000,
        "kilos_lote_max": 20000,
    },
    "Maiz": {
        "descripcion": "El motor de la proteína",
        "precio_base_min": 1.20,
        "precio_base_max": 3.50,
        "kilos_lote_min": 3000,
        "kilos_lote_max": 30000,
    },
    "Arroz": {
        "descripcion": "El cereal del día a día",
        "precio_base_min": 2.50,
        "precio_base_max": 5.00,
        "kilos_lote_min": 2000,
        "kilos_lote_max": 25000,
    },
    "Soya": {
        "descripcion": "Harina y subproductos para ganadería",
        "precio_base_min": 2.80,
        "precio_base_max": 6.50,
        "kilos_lote_min": 5000,
        "kilos_lote_max": 50000,
    },
    "Azucar": {
        "descripcion": "Derivado de la Caña",
        "precio_base_min": 2.20,
        "precio_base_max": 4.80,
        "kilos_lote_min": 3000,
        "kilos_lote_max": 40000,
    },
    "Trigo": {
        "descripcion": "Harina, pan y fideos",
        "precio_base_min": 1.80,
        "precio_base_max": 4.20,
        "kilos_lote_min": 2000,
        "kilos_lote_max": 30000,
    },
}

PRODUCTOS_LIST = list(PRODUCTOS_CONFIG.keys())

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

BUSINESS_SIZES_PYME = ["pequeña", "mediana"]
BUSINESS_SIZES_AGRO = ["pequeña", "mediana", "grande"]

SPANISH_FIRST_NAMES = [
    "Carlos", "María", "Juan", "Ana", "Luis", "Carmen", "José", "Isabel",
    "Pedro", "Sofía", "Diego", "Valentina", "Andrés", "Lucía", "Fernando",
    "Gabriela", "Ricardo", "Elena", "Miguel", "Paula",
]

SPANISH_LAST_NAMES = [
    "García", "Rodríguez", "López", "Martínez", "Hernández", "González",
    "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Morales",
    "Ortiz", "Cruz", "Reyes", "Vargas", "Castro", "Mendoza", "Ríos",
]

NOW = datetime.utcnow()


def fake_name() -> str:
    first = random.choice(SPANISH_FIRST_NAMES)
    last1 = random.choice(SPANISH_LAST_NAMES)
    last2 = random.choice(SPANISH_LAST_NAMES)
    return f"{first} {last1} {last2}"


def fake_email(name: str) -> str:
    clean = name.lower().replace(" ", ".").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    provider = random.choice(["gmail.com", "hotmail.com", "yahoo.com", "outlook.com"])
    return f"{clean}@{provider}"


def fake_phone() -> str:
    return f"+591 3 {random.randint(300, 399):03d} {random.randint(1000, 9999):04d}"


def fake_datetime(days_ago_min: int = 0, days_ago_max: int = 365) -> datetime:
    days = random.randint(days_ago_min, days_ago_max)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    return NOW - timedelta(days=days, hours=hours, minutes=minutes)


def future_date(days_ahead_min: int = 10, days_ahead_max: int = 90) -> datetime:
    days = random.randint(days_ahead_min, days_ahead_max)
    return NOW + timedelta(days=days)


def main() -> None:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    random.seed(42)

    try:
        # ── Clean existing data ───────────────────────────────────────────
        print("🧹 Limpiando datos existentes...")
        cursor.execute("DELETE FROM demand_predictions")
        cursor.execute("DELETE FROM commitments")
        cursor.execute("DELETE FROM lots")
        cursor.execute("DELETE FROM users")
        conn.commit()

        # ── Users ─────────────────────────────────────────────────────────
        print("👤 Insertando usuarios...")
        user_ids: list[str] = []
        pyme_ids: list[str] = []
        agro_ids: list[str] = []

        for i in range(40):
            uid = str(uuid.uuid4())
            name = fake_name()
            email = fake_email(name)
            phone = fake_phone()
            area = random.choice(AREAS_BOLIVIA)
            company = f"{random.choice(EMPRESAS_PYME)} {random.randint(10, 99)}"
            size = random.choice(BUSINESS_SIZES_PYME)
            created_at = fake_datetime(days_ago_max=400)

            cursor.execute(
                """INSERT INTO users (id, role, contact_name, email, company_name, phone, area, products, business_size, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (uid, "pyme", name, email, company, phone, area, None, size, created_at),
            )
            user_ids.append(uid)
            pyme_ids.append(uid)

        for i in range(25):
            uid = str(uuid.uuid4())
            name = fake_name()
            email = fake_email(name)
            phone = fake_phone()
            area = random.choice(AREAS_BOLIVIA)
            my_products = ", ".join(random.sample(PRODUCTOS_LIST, k=random.randint(1, 3)))
            company = f"{random.choice(EMPRESAS_AGRO)} {random.randint(10, 99)}"
            size = random.choice(BUSINESS_SIZES_AGRO)
            created_at = fake_datetime(days_ago_max=400)

            cursor.execute(
                """INSERT INTO users (id, role, contact_name, email, company_name, phone, area, products, business_size, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (uid, "agro", name, email, company, phone, area, my_products, size, created_at),
            )
            user_ids.append(uid)
            agro_ids.append(uid)

            if (i + 1) % 10 == 0:
                conn.commit()

        conn.commit()
        print(f"   ✅ {len(user_ids)} usuarios creados (40 pymes + 25 agros)")

        # ── Lots ──────────────────────────────────────────────────────────
        print("\n📦 Insertando lotes...")
        lot_ids: list[str] = []
        lot_creators: dict[str, str] = {}

        lot_counter = 1
        for producto, config in PRODUCTOS_CONFIG.items():
            precio_base = (config["precio_base_min"] + config["precio_base_max"]) / 2
            n_lotes = random.randint(6, 12)

            for _ in range(n_lotes):
                lid = f"LOT-{producto[:3].upper()}-{lot_counter:04d}"
                lot_counter += 1

                target_kilos = Decimal(str(round(random.uniform(
                    config["kilos_lote_min"], config["kilos_lote_max"]
                ), 2)))
                precio = round(precio_base * random.uniform(0.92, 1.08), 2)
                base_price = Decimal(str(precio))

                status = random.choice(["active", "completed", "expired"])
                if status == "completed":
                    tasa_fill = random.uniform(0.90, 1.00)
                elif status == "expired":
                    tasa_fill = random.uniform(0.20, 0.69)
                else:
                    tasa_fill = random.uniform(0.40, 0.95)
                current_kilos = Decimal(str(round(float(target_kilos) * tasa_fill, 2)))

                if status == "expired":
                    deadline = fake_datetime(days_ago_min=1, days_ago_max=30)
                else:
                    deadline = future_date(days_ahead_min=15, days_ahead_max=45)

                creator = random.choice(agro_ids) if agro_ids else random.choice(user_ids)
                created_at = fake_datetime(days_ago_min=5, days_ago_max=300)

                cursor.execute(
                    """INSERT INTO lots (id, product, producer, target_kilos, current_kilos,
                       base_price, deadline, status, created_by, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (lid, producto, random.choice(EMPRESAS_AGRO), target_kilos, current_kilos,
                     base_price, deadline, status, creator, created_at),
                )
                lot_ids.append(lid)
                lot_creators[lid] = creator

            conn.commit()
            print(f"   {producto}: {n_lotes} lotes insertados")

        conn.commit()
        print(f"   ✅ {len(lot_ids)} lotes creados")

        # ── Commitments ───────────────────────────────────────────────────
        print("\n🤝 Insertando compromisos...")
        commitment_count = 0

        cursor.execute("SELECT id, current_kilos FROM lots")
        lot_kilos = {row[0]: float(row[1]) for row in cursor.fetchall()}

        for lot_id in lot_ids:
            num_committers = random.randint(2, min(10, len(pyme_ids)))
            committers = random.sample(pyme_ids, k=num_committers)
            current_kilos = lot_kilos.get(lot_id, 5000.0)
            restantes = current_kilos

            for j, c_user in enumerate(committers):
                if restantes <= 0:
                    break
                if j == num_committers - 1:
                    kg = restantes
                else:
                    kg = min(
                        round(
                            random.uniform(0.1, 0.6)
                            * current_kilos
                            / num_committers
                            * random.uniform(0.8, 1.2),
                            2,
                        ),
                        restantes,
                    )
                restantes -= kg
                kilos = Decimal(str(max(round(kg, 2), 0.01)))

                cid = str(uuid.uuid4())
                created_at = fake_datetime(days_ago_min=1, days_ago_max=250)

                cursor.execute(
                    """INSERT INTO commitments (id, lot_id, user_id, kilos, created_at)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (cid, lot_id, c_user, kilos, created_at),
                )
                commitment_count += 1

            if commitment_count % 20 == 0:
                conn.commit()
                print(f"   {commitment_count} compromisos insertados...")

        conn.commit()
        print(f"   ✅ {commitment_count} compromisos creados")

        # ── Demand Predictions ────────────────────────────────────────────
        print("\n📊 Insertando predicciones de demanda...")
        pred_count = 0

        for i, lot_id in enumerate(lot_ids):
            if random.random() > 0.7:
                continue

            weeks = random.randint(4, 16)
            labels = [(NOW + timedelta(weeks=w)).strftime("Semana %d/%m") for w in range(1, weeks + 1)]
            base_demand = [round(random.uniform(500, 5000), 1) for _ in range(weeks)]
            predicted_demand = [round(v * random.uniform(0.93, 1.07), 1) for v in base_demand]

            prediction_data = {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Demanda base (kg)",
                        "data": base_demand,
                        "borderColor": "#3b82f6",
                        "backgroundColor": "rgba(59,130,246,0.1)",
                    },
                    {
                        "label": "Demanda predicha (kg)",
                        "data": predicted_demand,
                        "borderColor": "#ef4444",
                        "backgroundColor": "rgba(239,68,68,0.1)",
                    },
                ],
            }

            pid = str(uuid.uuid4())
            cursor.execute(
                """INSERT INTO demand_predictions (id, lot_id, labels, datasets, created_at)
                   VALUES (%s, %s, %s, %s, %s)""",
                (pid, lot_id,
                 json.dumps(prediction_data["labels"]),
                 json.dumps(prediction_data["datasets"]),
                 fake_datetime(days_ago_min=1, days_ago_max=90)),
            )
            pred_count += 1

        conn.commit()
        print(f"   ✅ {pred_count} predicciones creadas")

        print(f"\n{'='*50}")
        print("✅ Base de datos poblada exitosamente!")
        print(f"   👤 {len(user_ids)} usuarios")
        print(f"   📦 {len(lot_ids)} lotes")
        print(f"   🤝 {commitment_count} compromisos")
        print(f"   📊 {pred_count} predicciones")
        print(f"{'='*50}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
