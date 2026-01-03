from dataclasses import dataclass

from app.domain.efektibitatea import Efektibitatea

@dataclass
class Mota:
    izena: str
    efektibitatea: "Efektibitatea"

    def __init__(self, izena: str, efektibitatea):
        self.izena = izena
        self.efektibitatea = efektibitatea