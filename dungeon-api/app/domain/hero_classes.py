from abc import ABC, abstractmethod
import random
from typing import Protocol


class HeroData(Protocol):
    classe: str
    force: int
    agilite: int
    intelligence: int


class Heros(ABC):
    def __init__(self, force: int, agilite: int, intelligence: int):
        self.force = force
        self.agilite = agilite
        self.intelligence = intelligence

    @property
    def pv_max(self) -> int:
        return 20 + self.force * 2

    @abstractmethod
    def calculer_degats(self) -> tuple[int, bool]:
        """Renvoie les dégâts et indique si l'attaque est critique."""
        raise NotImplementedError

    def subir_degats(self, attaque_monstre: int) -> int:
        return max(1, attaque_monstre)


class Guerrier(Heros):
    def calculer_degats(self) -> tuple[int, bool]:
        return 2 + self.force * 2, False

    def subir_degats(self, attaque_monstre: int) -> int:
        return max(1, attaque_monstre - 1)


class Mage(Heros):
    def calculer_degats(self) -> tuple[int, bool]:
        return 1 + self.intelligence * 3, False


class Voleur(Heros):
    def calculer_degats(self) -> tuple[int, bool]:
        critique = random.choice([True, False, False])
        degats_base = 2 + self.agilite * 2
        return (degats_base * 2 if critique else degats_base), critique


def instancier_heros(hero_db: HeroData) -> Heros:
    """Transforme un modèle de base de données en objet métier."""
    classes: dict[str, type[Heros]] = {
        "guerrier": Guerrier,
        "mage": Mage,
        "voleur": Voleur,
    }
    classe = classes.get(hero_db.classe)
    if classe is None:
        raise ValueError("Classe inconnue")
    return classe(hero_db.force, hero_db.agilite, hero_db.intelligence)
