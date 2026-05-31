import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4

import mysql.connector
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mysql.connector import Error
from pydantic import BaseModel, Field

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
}
DB_NAME = os.getenv("DB_NAME", "crowdbuy")

app = FastAPI(title="CrowdBuy API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterUser(BaseModel):
    role: str
    contact_name: str | None = Field(default=None, alias="contactName")
    email: str | None = None
    company_name: str | None = Field(default=None, alias="companyName")
    phone: str | None = None

    model_config = {"populate_by_name": True}


class LoginUser(BaseModel):
    role: str
    email: str | None = None
    phone: str | None = None


class UpdateProfile(BaseModel):
    area: str | None = None
    products: str | None = None
    business_size: str | None = Field(default=None, alias="businessSize")

    model_config = {"populate_by_name": True}


class CreateLot(BaseModel):
    product: str
    producer: str
    target_kilos: float = Field(alias="targetKilos")
    base_price: float = Field(alias="basePrice")
    deadline: str
    created_by: str | None = Field(default=None, alias="createdBy")

    model_config = {"populate_by_name": True}


class CommitLot(BaseModel):
    kilos: float
    user_id: str | None = Field(default=None, alias="userId")

    model_config = {"populate_by_name": True}


def db(database: bool = True):
    config = DB_CONFIG.copy()
    if database:
        config["database"] = DB_NAME
    return mysql.connector.connect(**config)


def execute(sql: str, params: tuple[Any, ...] = (), fetchone: bool = False):
    conn = db()
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(sql, params)
        if cursor.with_rows:
            return cursor.fetchone() if fetchone else cursor.fetchall()
        conn.commit()
        return None
    finally:
        cursor.close()
        conn.close()


def init_db() -> None:
    conn = db(database=False)
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    statements = [
        """
        CREATE TABLE IF NOT EXISTS users (
          id CHAR(36) PRIMARY KEY,
          role ENUM('pyme', 'agro') NOT NULL,
          contact_name VARCHAR(255) NOT NULL,
          email VARCHAR(255) NULL,
          company_name VARCHAR(255) NULL,
          phone VARCHAR(50) NULL,
          area VARCHAR(255) NULL,
          products TEXT NULL,
          business_size VARCHAR(255) NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS lots (
          id VARCHAR(20) PRIMARY KEY,
          product VARCHAR(255) NOT NULL,
          producer VARCHAR(255) NOT NULL,
          target_kilos DECIMAL(12,2) NOT NULL,
          current_kilos DECIMAL(12,2) NOT NULL DEFAULT 0,
          base_price DECIMAL(12,2) NOT NULL,
          deadline DATETIME NOT NULL,
          status ENUM('active', 'completed', 'expired') NOT NULL DEFAULT 'active',
          created_by CHAR(36) NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          CONSTRAINT fk_lots_created_by FOREIGN KEY (created_by) REFERENCES users(id)
            ON DELETE SET NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS commitments (
          id CHAR(36) PRIMARY KEY,
          lot_id VARCHAR(20) NOT NULL,
          user_id CHAR(36) NULL,
          kilos DECIMAL(12,2) NOT NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          CONSTRAINT fk_commitments_lot FOREIGN KEY (lot_id) REFERENCES lots(id)
            ON DELETE CASCADE,
          CONSTRAINT fk_commitments_user FOREIGN KEY (user_id) REFERENCES users(id)
            ON DELETE SET NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS demand_predictions (
          id CHAR(36) PRIMARY KEY,
          lot_id VARCHAR(20) NOT NULL,
          labels JSON NOT NULL,
          datasets JSON NOT NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          CONSTRAINT fk_predictions_lot FOREIGN KEY (lot_id) REFERENCES lots(id)
            ON DELETE CASCADE
        )
        """,
    ]

    conn = db()
    cursor = conn.cursor()
    try:
        for statement in statements:
            cursor.execute(statement)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


@app.on_event("startup")
def startup() -> None:
    try:
        init_db()
    except Error as exc:
        raise RuntimeError(f"No se pudo inicializar MySQL: {exc}") from exc


def to_float(value: Any) -> float:
    if isinstance(value, Decimal):
        return float(value)
    return value


def iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def parse_datetime(value: str) -> datetime:
    clean = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(clean)
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def refresh_lot_statuses() -> None:
    execute(
        """
        UPDATE lots
        SET status = CASE
          WHEN current_kilos >= target_kilos THEN 'completed'
          WHEN deadline < UTC_TIMESTAMP() THEN 'expired'
          ELSE 'active'
        END
        """
    )


def lot_to_api(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "product": row["product"],
        "producer": row["producer"],
        "targetKilos": to_float(row["target_kilos"]),
        "currentKilos": to_float(row["current_kilos"]),
        "basePrice": to_float(row["base_price"]),
        "deadline": iso(row["deadline"]),
        "status": row["status"],
        "createdBy": row["created_by"],
        "createdAt": iso(row["created_at"]),
    }


def user_to_api(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "role": row["role"],
        "contactName": row["contact_name"],
        "email": row["email"],
        "companyName": row["company_name"],
        "phone": row["phone"],
        "area": row["area"],
        "products": row["products"],
        "businessSize": row["business_size"],
        "createdAt": iso(row["created_at"]),
    }


def get_lot_or_404(lot_id: str) -> dict[str, Any]:
    refresh_lot_statuses()
    lot = execute("SELECT * FROM lots WHERE id = %s", (lot_id,), fetchone=True)
    if not lot:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    return lot


def next_lot_id() -> str:
    row = execute(
        """
        SELECT COALESCE(MAX(CAST(SUBSTRING(id, 5) AS UNSIGNED)), 0) + 1 AS next_id
        FROM lots
        WHERE id LIKE 'LOT-%'
        """,
        fetchone=True,
    )
    return f"LOT-{int(row['next_id']):03d}"


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/auth/register")
def register(payload: RegisterUser):
    user_id = str(uuid4())
    execute(
        """
        INSERT INTO users (id, role, contact_name, email, company_name, phone)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            payload.role,
            payload.contact_name or "",
            payload.email,
            payload.company_name,
            payload.phone,
        ),
    )
    user = execute("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)
    return user_to_api(user)


@app.post("/auth/login")
def login(payload: LoginUser):
    if payload.role == "pyme":
        if not payload.email:
            raise HTTPException(status_code=400, detail="Email requerido para PYME")
        user = execute(
            "SELECT * FROM users WHERE role = %s AND email = %s",
            (payload.role, payload.email),
            fetchone=True,
        )
    else:
        if not payload.phone:
            raise HTTPException(
                status_code=400, detail="Telefono requerido para Productor"
            )
        user = execute(
            "SELECT * FROM users WHERE role = %s AND phone = %s",
            (payload.role, payload.phone),
            fetchone=True,
        )
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user_to_api(user)


@app.put("/users/{user_id}/profile")
def update_profile(user_id: str, payload: UpdateProfile):
    execute(
        """
        UPDATE users
        SET area = %s, products = %s, business_size = %s
        WHERE id = %s
        """,
        (payload.area, payload.products, payload.business_size, user_id),
    )
    user = execute("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user_to_api(user)


@app.get("/lots")
def list_lots(all: bool = False, created_by: str = ""):
    refresh_lot_statuses()
    if all:
        if created_by:
            rows = execute(
                "SELECT * FROM lots WHERE created_by = %s ORDER BY created_at DESC",
                (created_by,),
            )
        else:
            rows = execute("SELECT * FROM lots ORDER BY created_at DESC")
    else:
        if created_by:
            rows = execute(
                "SELECT * FROM lots WHERE status = 'active' AND created_by = %s ORDER BY created_at DESC",
                (created_by,),
            )
        else:
            rows = execute(
                "SELECT * FROM lots WHERE status = 'active' ORDER BY created_at DESC"
            )
    return [lot_to_api(row) for row in rows]


@app.get("/lots/{lot_id}")
def lot_detail(lot_id: str):
    return lot_to_api(get_lot_or_404(lot_id))


@app.post("/lots")
def create_lot(payload: CreateLot):
    lot_id = next_lot_id()
    execute(
        """
        INSERT INTO lots
          (id, product, producer, target_kilos, current_kilos, base_price, deadline, created_by)
        VALUES (%s, %s, %s, %s, 0, %s, %s, %s)
        """,
        (
            lot_id,
            payload.product,
            payload.producer,
            payload.target_kilos,
            payload.base_price,
            parse_datetime(payload.deadline),
            payload.created_by,
        ),
    )
    return lot_to_api(get_lot_or_404(lot_id))


@app.post("/lots/{lot_id}/commit")
def commit_to_lot(lot_id: str, payload: CommitLot):
    get_lot_or_404(lot_id)
    commitment_id = str(uuid4())
    execute(
        """
        INSERT INTO commitments (id, lot_id, user_id, kilos)
        VALUES (%s, %s, %s, %s)
        """,
        (commitment_id, lot_id, payload.user_id, payload.kilos),
    )
    execute(
        """
        UPDATE lots
        SET current_kilos = (
          SELECT COALESCE(SUM(kilos), 0)
          FROM commitments
          WHERE lot_id = %s
        )
        WHERE id = %s
        """,
        (lot_id, lot_id),
    )
    lot = lot_to_api(get_lot_or_404(lot_id))
    return {
        "commitment": {
            "id": commitment_id,
            "lotId": lot_id,
            "userId": payload.user_id,
            "kilos": payload.kilos,
            "createdAt": datetime.utcnow().isoformat(),
        },
        "lot": lot,
    }


@app.get("/lots/{lot_id}/prediction")
def prediction(lot_id: str):
    get_lot_or_404(lot_id)
    existing = execute(
        """
        SELECT * FROM demand_predictions
        WHERE lot_id = %s
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (lot_id,),
        fetchone=True,
    )
    if existing:
        return {
            "id": existing["id"],
            "lotId": existing["lot_id"],
            "labels": json.loads(existing["labels"]),
            "datasets": json.loads(existing["datasets"]),
            "createdAt": iso(existing["created_at"]),
        }

    labels = [
        "Ene",
        "Feb",
        "Mar",
        "Abr",
        "May",
        "Jun",
        "Jul",
        "Ago",
        "Sep",
        "Oct",
        "Nov",
        "Dic",
    ]
    datasets = [
        {
            "label": "Historico",
            "data": [120, 135, 110, 160, 180, 200, 190, 210, 170, 150, 140, 130],
            "fill": False,
            "borderColor": "#61BAC2",
            "borderDash": None,
            "tension": 0.4,
        },
        {
            "label": "Prediccion",
            "data": [None, None, None, None, None, None, 190, 210, 220, 250, 270, 300],
            "fill": False,
            "borderColor": "#C29A61",
            "borderDash": [5, 5],
            "tension": 0.4,
        },
    ]
    prediction_id = str(uuid4())
    execute(
        """
        INSERT INTO demand_predictions (id, lot_id, labels, datasets)
        VALUES (%s, %s, %s, %s)
        """,
        (prediction_id, lot_id, json.dumps(labels), json.dumps(datasets)),
    )
    return {
        "id": prediction_id,
        "lotId": lot_id,
        "labels": labels,
        "datasets": datasets,
        "createdAt": datetime.utcnow().isoformat(),
    }


@app.get("/pyme/impact")
def pyme_impact(userId: str | None = None):
    params: tuple[Any, ...] = ()
    where = ""
    if userId:
        where = "WHERE c.user_id = %s"
        params = (userId,)

    totals = execute(
        f"""
        SELECT
          COALESCE(SUM(c.kilos), 0) AS total_kilos,
          COUNT(DISTINCT c.lot_id) AS active_lotes,
          COUNT(DISTINCT l.producer) AS producers
        FROM commitments c
        JOIN lots l ON l.id = c.lot_id
        {where}
        """,
        params,
        fetchone=True,
    )
    producers = execute(
        f"""
        SELECT DISTINCT l.producer
        FROM commitments c
        JOIN lots l ON l.id = c.lot_id
        {where}
        ORDER BY l.producer
        """,
        params,
    )
    progress = execute(
        """
        SELECT
          COALESCE(SUM(current_kilos), 0) AS current_total,
          COALESCE(SUM(target_kilos), 0) AS target_total
        FROM lots
        """,
        fetchone=True,
    )
    target = to_float(progress["target_total"])
    current = to_float(progress["current_total"])
    return {
        "totalKilos": to_float(totals["total_kilos"]),
        "activeLotes": int(totals["active_lotes"]),
        "totalProgress": round((current / target) * 100) if target else 0,
        "uniqueProducers": [row["producer"] for row in producers],
        "producerCount": int(totals["producers"]),
    }
