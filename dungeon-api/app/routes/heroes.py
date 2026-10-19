import asyncio
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.hero import Hero
from app.models.user import User
from app.schemas.hero import HeroCreate, HeroResponse
from app.schemas.dungeon import AttackResponse, MoveRequest, RoomResponse
from app.services.dungeon_map import (
    FINAL_ROOM,
    get_monster_of_room,
    get_room,
)
from app.services.hero_service import create_hero, get_hero_by_id
from app.routes.auth import get_current_user
from app.domain.hero_classes import instancier_heros

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


def ensure_hero_owner(hero: Hero, current_user: User) -> None:
    if hero.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "NOT_YOUR_HERO",
                "message": "Ce héros ne vous appartient pas.",
            },
        )


# FT-1 : Création d'un héros
@router.post("", response_model=HeroResponse, status_code=201)
def post_hero(
    hero_in: HeroCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    nouveau = create_hero(session, hero_in, current_user.id)
    return format_hero_response(nouveau)


@router.get("", response_model=List[HeroResponse])
def get_heroes(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    heroes = session.exec(
        select(Hero).where(Hero.owner_id == current_user.id)
    ).all()
    return [format_hero_response(h) for h in heroes]


#FT-3 consulter un héros par son ID
@router.get("/{id}", response_model=HeroResponse)
def get_hero(
    id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    hero = get_hero_by_id(session, id)
    if hero is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "Ce héros n'existe pas."}
        )
    ensure_hero_owner(hero, current_user)
    return format_hero_response(hero)


#FT-5 description de la salle
@router.get("/{id}/room", response_model=RoomResponse)
def get_hero_room(
    id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    hero = get_hero_by_id(session, id)
    if not hero:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "Ce héros n'existe pas."}
        )
    ensure_hero_owner(hero, current_user)
    return format_room_response(hero)


#FT-6 déplacement du héros
@router.post("/{id}/move", response_model=RoomResponse)
def move_hero(
    id: int,
    move_req: MoveRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    hero = get_hero_by_id(session, id)
    if not hero:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "Ce héros n'existe pas."}
        )
    ensure_hero_owner(hero, current_user)

    if hero.monstre_pv is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "IN_COMBAT",
                "message": "Impossible de fuir le combat.",
            },
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


@router.post("/{id}/attack", response_model=AttackResponse)
def attack_monster(
    id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    hero = get_hero_by_id(session, id)
    if hero is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "Héros introuvable."},
        )
    ensure_hero_owner(hero, current_user)

    if hero.pv <= 0:
        raise HTTPException(
            status_code=409,
            detail={"error": "HERO_DEAD", "message": "Le héros est mort."},
        )
    if hero.monstre_pv is None:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "NO_MONSTER",
                "message": "Aucun monstre dans la salle.",
            },
        )

    monster = get_monster_of_room(hero.salle_actuelle)
    if monster is None:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "NO_MONSTER",
                "message": "Aucun monstre dans la salle.",
            },
        )

    heros_poo = instancier_heros(hero)
    degats_heros, est_critique = heros_poo.calculer_degats()
    hero.monstre_pv = max(0, hero.monstre_pv - degats_heros)

    degats_subis = 0
    issue = "en_cours"
    or_gagne = 0

    if hero.monstre_pv == 0:
        issue = "monstre_vaincu"
        or_gagne = monster.get("gold", 0)
        hero.or_ += or_gagne
        hero.monstre_pv = None
        if hero.salle_actuelle == FINAL_ROOM:
            hero.victoire = True
    else:
        degats_subis = heros_poo.subir_degats(monster.get("attack", 2))
        hero.pv = max(0, hero.pv - degats_subis)
        if hero.pv == 0:
            issue = "heros_mort"
            hero.monstre_pv = None

    session.add(hero)
    session.commit()
    session.refresh(hero)

    return AttackResponse(
        degats_infliges=degats_heros,
        critique=est_critique,
        degats_subis=degats_subis,
        pv_heros=hero.pv,
        pv_monstre=hero.monstre_pv or 0,
        issue=issue,
        or_gagne=or_gagne,
        victoire=hero.victoire,
    )


@router.post("/{id}/rest", response_model=HeroResponse)
async def rest_hero(
    id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    hero = get_hero_by_id(session, id)
    if hero is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "Héros introuvable."},
        )
    ensure_hero_owner(hero, current_user)

    if hero.pv <= 0:
        raise HTTPException(
            status_code=409,
            detail={"error": "HERO_DEAD", "message": "Le héros est mort."},
        )
    if hero.monstre_pv is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "IN_COMBAT",
                "message": "Impossible de se reposer en combat.",
            },
        )

    await asyncio.sleep(3)

    hero.pv = hero.pv_max
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return format_hero_response(hero)