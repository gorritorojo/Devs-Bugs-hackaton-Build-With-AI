from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mysql.connector import Error

from app.database import init_db
from app.routers.auth import router as auth_router
from app.routers.lots import router as lots_router
from app.routers.predictions import router as predictions_router
from app.routers.pyme import router as pyme_router
from app.routers.users import router as users_router

app = FastAPI(title="CrowdBuy API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(lots_router)
app.include_router(predictions_router)
app.include_router(pyme_router)
app.include_router(users_router)


@app.on_event("startup")
def startup() -> None:
    try:
        init_db()
    except Error as exc:
        raise RuntimeError(f"No se pudo inicializar MySQL: {exc}") from exc


@app.get("/health")
def health():
    return {"ok": True}
