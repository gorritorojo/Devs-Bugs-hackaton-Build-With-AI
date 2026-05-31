import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import mysql.connector
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
}
DB_NAME = os.getenv("DB_NAME", "crowdbuy")


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
          status ENUM('active', 'completed', 'expired', 'deactivated') NOT NULL DEFAULT 'active',
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
        cursor.execute(
            """
            ALTER TABLE lots MODIFY status
            ENUM('active', 'completed', 'expired', 'deactivated')
            NOT NULL DEFAULT 'active'
            """
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


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
        WHERE status != 'deactivated'
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
