from pydantic import BaseModel
from typing import Literal, List, Optional

# Validation de la direction (le joueur ne peut taper que ces 4 mots)
class MoveRequest(BaseModel):
    direction: Literal["nord", "sud", "est", "ouest"]

# Format de réponse pour décrire une salle
class RoomResponse(BaseModel):
    id: str
    nom: str
    description: str
    sorties: List[str]
    monstre: Optional[str] = None


class AttackResponse(BaseModel):
    degats_infliges: int
    critique: bool
    degats_subis: int
    pv_heros: int
    pv_monstre: int
    issue: str
    or_gagne: int
    victoire: bool