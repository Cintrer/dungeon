from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from app.database import get_session
from app.models.hero import Hero
from app.schemas.hero import HeroCreate, HeroResponse
from app.schemas.dungeon import MoveRequest, RoomResponse
from app.services.hero_service import create_hero, get_all_heroes, get_hero_by_id
from app.services.dungeon_map import get_room, get_monster_of_room

router = APIRouter(prefix="/heroes", tags=["Héros"])


def format_hero_response(hero: Hero) -> HeroResponse:
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


def format_room_response(hero: Hero) -> RoomResponse:
    room = get_room(hero.salle_actuelle)
    if not room:
        raise HTTPException(
            status_code=404,
            detail={"error": "ROOM_NOT_FOUND", "message": "Salle introuvable."}
        )

    nom_monstre = None
    if hero.monstre_pv is not None:
        monster = get_monster_of_room(hero.salle_actuelle)
        if monster:
            nom_monstre = monster["name"]

    exits = room.get("exits", {})
    sorties_list = list(exits.keys())

    return RoomResponse(
        id=hero.salle_actuelle,
        nom=room["name"],
        description=room["description"],
        sorties=sorties_list,
        monstre=nom_monstre
    )


# FT-1 : Création d'un héros
@router.post("", response_model=HeroResponse, status_code=201)
def post_hero(hero_in: HeroCreate, session: Session = Depends(get_session)):
    nouveau = create_hero(session, hero_in)
    return format_hero_response(nouveau)

@router.get("", response_model=List[HeroResponse])
def get_heroes(session: Session = Depends(get_session)):
    heroes = get_all_heroes(session)
    return [format_hero_response(h) for h in heroes]

#FT-3 consulter un héros par son ID
@router.get("/{id}", response_model=HeroResponse)
def get_hero(id: int, session: Session = Depends(get_session)):
    hero = get_hero_by_id(session, id)
    if hero is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "Ce héros n'existe pas."}
        )
    return format_hero_response(hero)


#FT-5 description de la salle
@router.get("/{id}/room", response_model=RoomResponse)
def get_hero_room(id: int, session: Session = Depends(get_session)):
    hero = get_hero_by_id(session, id)
    if not hero:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "Ce héros n'existe pas."}
        )
    return format_room_response(hero)


#FT-6 déplacement du héros
@router.post("/{id}/move", response_model=RoomResponse)
def move_hero(id: int, move_req: MoveRequest, session: Session = Depends(get_session)):
    hero = get_hero_by_id(session, id)
    if not hero:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "Ce héros n'existe pas."}
        )

    room = get_room(hero.salle_actuelle)
    exits = room.get("exits", {})

    if move_req.direction not in exits:
        raise HTTPException(
            status_code=400,
            detail={"error": "NO_EXIT", "message": f"Il n'y a pas de passage vers le {move_req.direction}."}
        )

    nouvelle_salle_id = exits[move_req.direction]
    hero.salle_actuelle = nouvelle_salle_id
    monster = get_monster_of_room(nouvelle_salle_id)
    if monster:
        hero.monstre_pv = monster["hp"]
    else:
        hero.monstre_pv = None
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return format_room_response(hero)