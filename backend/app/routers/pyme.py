from typing import Any

from fastapi import APIRouter, Query

from app.database import execute, to_float

router = APIRouter(prefix="/pyme", tags=["pyme"])


@router.get("/impact")
def pyme_impact(userId: str | None = Query(None)):
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
