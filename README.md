# Pariente

## integrantes:

Renzo Valencia Gutierrez
Andres Velasquez Villaroel
Brayan Luna Monrroy

## link video YouTube

https://youtu.be/ffb5YKDpMJc

## Arquitectura

### MVP

El MVP funcional presentado en esta hackathon adopta una estrategia agil centrada en la experiencia de usuario (UX):

- **Frontend**: Desarrollado en **Angular** utilizando la biblioteca de componentes **PrimeNG** para una interfaz moderna y responsiva, con estilos en **Tailwind CSS**.
- **Backend**: API REST construida con **Python (FastAPI)** que expone los endpoints de autenticacion, gestion de lotes, compromisos de compra y prediccion de demanda.
- **Base de Datos**: **MySQL**, con esquema relacional que modela usuarios, lotes, compromisos y predicciones de demanda.
- **Modelo de IA**: Servicio en Python que genera predicciones de demanda por lote basado en datos historicos.
- **Despliegue**: El build de produccion se genera con `ng build` y los artefactos en `dist/` pueden servirse desde cualquier hosting estatico (Nginx, Vercel, Netlify, etc.).

### Vision de Arquitectura para Produccion

Una vez validado el MVP, la plataforma transicionara a una infraestructura robusta:

- **Frontend**: Angular + PrimeNG estructurado bajo **Screaming Architecture** para maxima modularidad del negocio.
- **Backend**: Node.js con TypeScript implementando **Clean Architecture** para separar la logica de negocio de los controladores.
- **Base de Datos**: MySQL para garantizar la integridad relacional de los pedidos financieros y el catalogo ecologico.

## Tecnologias

| Capa | Tecnologia |
|---|---|
| Frontend | Angular 20, PrimeNG 20, Tailwind CSS 4, Chart.js |
| Backend | Python 3.10+, FastAPI, Uvicorn |
| Base de Datos | MySQL|
| Modelo IA | Python, scikit-learn |
| Despliegue | Hosting estatico |
| Tooling | Ultracite (Biome), Jasmine/Karma |

## Estructura del Proyecto Monorepo

```
├── backend/         # API REST (Python/FastAPI)
│   ├── app/         # Servidor principal (FastAPI package)
│   ├── schema.sql   # Esquema de base de datos
│   └── requirements.txt
├── frontend/        # Aplicacion Angular + PrimeNG
│   └── src/app/
│       ├── agro/     # Modulo para productores agricolas
│       ├── pyme/     # Modulo para PYMEs
│       ├── auth/     # Autenticacion
│       ├── core/     # Servicios, modelos, guards
│       └── layout/   # Layout principal
└── model/           # Modelo de prediccion de demanda (Python)
    └── main.py
```

## Pasos de Ejecucion

### Requisitos

- Node.js 18+
- Python 3.10+
- MySQL 8+

### Backend


```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

Editar `.env` con las credenciales de MySQL. La base de datos y tablas se crean automaticamente al iniciar

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API disponible en `http://localhost:8000` y documentacion interactiva en `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install        # o bun install
ng serve           # o npm start
```

Abrir `http://localhost:4200` en el navegador.

### Modelo IA

```bash
cd model
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # o uv sync
python main.py
```

### Despliegue del frontend

```bash
cd frontend
ng build
```

El comando genera el bundle optimizado en `frontend/dist/`. Los archivos resultantes pueden desplegarse en cualquier servidor o plataforma de hosting estatico.
