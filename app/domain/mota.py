from dataclasses import dataclass

from app.domain.efektibitatea import Efektibitatea

@dataclass
class Mota:
    # Mota izena (adib. Sua, Ura, Lurra…)
    izena: str
    # Mota honen efektibitate taula
    efektibitatea: "Efektibitatea"

    def __init__(self, izena: str, efektibitatea):
        # Izena esleitzen du
        self.izena = izena
        # Efektibitate objektua esleitzen du
        self.efektibitatea = efektibitatea
