from pydantic import BaseModel, Field, model_validator
from typing import Literal

class HeroCreate(BaseModel):
    nom: str = Field(min_length=3, max_length=20)
    # force le joueur a chosir une des 3 classes
    classe: Literal["guerrier", "mage", "voleur"]
    force: int = Field(ge=1, le=8)
    agilite: int = Field(ge=1, le=8)
    intelligence: int = Field(ge=1, le=8)
    @model_validator(mode='after')
    def check_stats_sum(self):
        somme = self.force + self.agilite + self.intelligence
        if somme != 10:
            raise ValueError("La somme des statistiques doit faire exactement 10")
        return self

# Ce qu'on renvoie au joueur pour cacher les infos secrètes (comme les pv du monstre)
class HeroResponse(BaseModel):
    id: int
    nom: str
    classe: str
    force: int
    agilite: int
    intelligence: int
    pv: int
    pv_max: int
    salle_actuelle: str
    or_: int
    victoire: bool
    en_combat: bool
    est_vivant: bool