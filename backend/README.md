# CrowdBuy Backend

Backend funcional en Python para los esquemas de `frontend/docs/SCHEMAS.md`.

## Requisitos

- Python 3.10+
- MySQL 8+

## Configuracion

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` con tus credenciales de MySQL. La app crea la base de datos y las tablas al iniciar.

## Ejecutar

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

API base: `http://localhost:8000`

Documentacion interactiva: `http://localhost:8000/docs`

## Endpoints

- `POST /auth/register`
- `PUT /users/{id}/profile`
- `GET /lots`
- `GET /lots/{id}`
- `POST /lots`
- `POST /lots/{id}/commit`
- `GET /lots/{id}/prediction`
- `GET /pyme/impact`
