"""Point d'entrée de l'API Dungeon as a Service.

Lancer le serveur depuis la racine du projet :
    fastapi dev app/main.py
Puis ouvrir http://127.0.0.1:8000/docs
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routes import heroes 
from sqlmodel import SQLModel 
from app.models.hero import Hero


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Exécuté une fois au démarrage du serveur : crée les tables si besoin
    create_db_and_tables()
    yield


app = FastAPI(
    title="Dungeon as a Service",
    description="Moteur de jeu de rôle textuel — Pixel Crypt",
    version="0.1.0",
    lifespan=lifespan,
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(heroes.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health", tags=["Système"])
def health() -> dict:
    """Vérifie que le serveur répond."""
    return {"status": "ok", "message": "Le donjon vous attend..."}
