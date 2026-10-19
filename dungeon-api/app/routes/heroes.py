from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from app.database import get_session
from app.models.hero import Hero
from app.schemas.hero import HeroCreate, HeroResponse
from app.services.hero_service import create_hero, get_all_heroes, get_hero_by_id

#création du routeur
router = APIRouter(prefix="/heroes", tags=["Héros"])


def format_hero_response(hero: Hero):
    return HeroResponse(
        id=hero.id,
        nom=hero.nom,
        classe=hero.classe,
        force=hero.force,
        agilite=hero.agilite,
        intelligence=hero.intelligence,
        pv=hero.pv,
        pv_max=hero.pv_max,
        salle_actuelle=hero.salle_actuelle,
        or_=hero.or_,
        victoire=hero.victoire,
        en_combat=hero.monstre_pv is not None, 
        est_vivant=hero.pv > 0
    )

# FT-1 création d'un héros
@router.post("", response_model=HeroResponse, status_code=201)
def post_hero(hero_in: HeroCreate, session: Session = Depends(get_session)):
    nouveau = create_hero(session, hero_in)
    return format_hero_response(nouveau)

# FT-3 consulter tous les héros
@router.get("", response_model=List[HeroResponse])
def get_heroes(session: Session = Depends(get_session)):
    heroes = get_all_heroes(session)
    return [format_hero_response(h) for h in heroes]

# FT-3 consulter un héros par son ID
@router.get("/{id}", response_model=HeroResponse)
def get_hero(id: int, session: Session = Depends(get_session)):
    hero = get_hero_by_id(session, id)
    if hero is None:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": "Ce héros n'existe pas."})
    return format_hero_response(hero)