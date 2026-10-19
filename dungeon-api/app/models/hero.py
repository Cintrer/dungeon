from sqlmodel import SQLModel, Field
from typing import Optional

class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str
    classe: str
    force: int
    agilite: int
    intelligence: int
    pv: int
    pv_max: int
    salle_actuelle: str
    or_: int = 0
    monstre_pv: Optional[int] = None
    victoire: bool = False
    owner_id: Optional[int] = None # 