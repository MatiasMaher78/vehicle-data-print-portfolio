# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import logging 

# Configuración básica del logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Importamos los routers
from .api.v1 import processing, auth, export, profile, downloads 

app = FastAPI(
    title="Homologation Vehicle API",
    description="API para procesar y gestionar datos de homologación de vehículos.",
    version="1.0.0"
)

DEFAULT_ALLOWED_ORIGINS = "http://localhost:5173,http://localhost:3000"
origins = [
    origin.strip()
    for origin in config("ALLOWED_ORIGINS", default=DEFAULT_ALLOWED_ORIGINS).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # Permite cookies/credenciales de autorización
    allow_methods=["*"],    # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],    # Permite todas las cabeceras
)
# Incluimos los routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(processing.router, prefix="/api/v1", tags=["Processing"])
app.include_router(export.router, prefix="/api/v1", tags=["Export"]) 
app.include_router(profile.router, prefix="/api/v1/profile", tags=["Profile"])
app.include_router(downloads.router, prefix="/api/v1/downloads", tags=["Downloads"])


@app.get("/")
def home():
    return {"status": "Homologation Vehicle API is running!"}
