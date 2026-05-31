from fastapi import APIRouter, HTTPException

from app.database import execute, user_to_api
from app.models import UpdateProfile

router = APIRouter(prefix="/users", tags=["users"])


@router.put("/{user_id}/profile")
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
