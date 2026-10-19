from sqlmodel import Session, select
from app.models.hero import Hero
from app.schemas.hero import HeroCreate
from app.services.dungeon_map import START_ROOM

def create_hero(session: Session, hero_in: HeroCreate):    #calcul des PV max comme demandé : 20 + force * 2
    pv_max = 20 + (hero_in.force * 2)
#on crée l'objet pour la base de données
    nouveau_heros = Hero(
        nom=hero_in.nom,
        classe=hero_in.classe,
        force=hero_in.force,
        agilite=hero_in.agilite,
        intelligence=hero_in.intelligence,
        pv=pv_max,
        pv_max=pv_max,
        salle_actuelle=START_ROOM,
        or_=0
    )
    
#on sauvegarde dans la base de données
    session.add(nouveau_heros)
    session.commit()
    session.refresh(nouveau_heros)
    return nouveau_heros

def get_all_heroes(session: Session):
    return session.exec(select(Hero)).all()

def get_hero_by_id(session: Session, hero_id: int):
    return session.get(Hero, hero_id)