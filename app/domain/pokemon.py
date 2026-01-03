from dataclasses import dataclass
from typing import List

from app.domain.mugimendua import Mugimendua

@dataclass
class Pokemon:
    izena: str
    irudia: str
    pokEspeziea: str
    mugZer: List["Mugimendua"]

    def __init__(self, izena: str, irudia: str,
                 pokEspeziea: str, mugZer: List["Mugimendua"]):
        self.izena = izena
        self.irudia = irudia
        self.pokEspeziea = pokEspeziea
        self.mugZer = mugZer