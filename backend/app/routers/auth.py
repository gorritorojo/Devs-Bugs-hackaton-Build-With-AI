from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.database import execute, user_to_api
from app.models import LoginUser, RegisterUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
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


@router.post("/login")
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
