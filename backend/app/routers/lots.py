import json
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query

from app.database import (
    execute,
    get_lot_or_404,
    iso,
    lot_to_api,
    next_lot_id,
    parse_datetime,
    refresh_lot_statuses,
)
from app.models import CommitLot, CreateLot, UpdateLotStatus

router = APIRouter(prefix="/lots", tags=["lots"])


@router.get("")
def list_lots(all: bool = Query(False), created_by: str = Query("")):
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


@router.get("/{lot_id}")
def lot_detail(lot_id: str):
    return lot_to_api(get_lot_or_404(lot_id))


@router.post("")
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


@router.post("/{lot_id}/commit")
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


@router.patch("/{lot_id}/status")
def update_lot_status(lot_id: str, payload: UpdateLotStatus):
    lot = get_lot_or_404(lot_id)
    if lot["created_by"] and lot["created_by"] != payload.user_id:
        raise HTTPException(status_code=403, detail="No autorizado")
    if payload.status not in ("active", "deactivated"):
        raise HTTPException(status_code=400, detail="Estado inválido. Use 'active' o 'deactivated'")
    execute(
        "UPDATE lots SET status = %s WHERE id = %s",
        (payload.status, lot_id),
    )
    return lot_to_api(get_lot_or_404(lot_id))


@router.get("/{lot_id}/prediction")
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
        "Ene", "Feb", "Mar", "Abr", "May", "Jun",
        "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
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
