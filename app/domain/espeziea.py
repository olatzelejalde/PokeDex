from dataclasses import dataclass
from typing import List

from app.domain.mugimendua import Mugimendua

@dataclass
class Espeziea:
    izena: str
    irudia: str
    deskripzioa: str
    motaZer: List[str]
    mugimenduZer: List["Mugimendua"]
    osasuna: int
    erasoa: int
    defentsa: int
    erasoBerezia: int
    defentsaBerezia: int
    abiadura: int
    eboluzioak: List[str]

    def __init__(self, izena: str, irudia: str, deskripzioa: str,
                 motaZer: List[str], mugimenduZer: List["Mugimendua"],
                 osasuna: int, erasoa: int, defentsa: int,
                 erasoBerezia: int, defentsaBerezia: int,
                 abiadura: int, eboluzioak: List[str]):
        self.izena = izena
        self.irudia = irudia
        self.deskripzioa = deskripzioa
        self.motaZer = motaZer
        self.mugimenduZer = mugimenduZer
        self.osasuna = osasuna
        self.erasoa = erasoa
        self.defentsa = defentsa
        self.erasoBerezia = erasoBerezia
        self.defentsaBerezia = defentsaBerezia
        self.abiadura = abiadura
        self.eboluzioak = eboluzioak