from dataclasses import dataclass
from typing import List

from app.domain.mugimendua import Mugimendua

@dataclass
class Espeziea:
    # Espeziearen oinarrizko informazioa
    izena: str
    irudia: str
    deskripzioa: str

    # Espeziearen motak (sua, belarra...)
    motaZer: List[str]

    # Espezieak erabil ditzakeen mugimenduak
    mugimenduZer: List["Mugimendua"]

    # Oinarrizko estatistikak
    osasuna: int
    erasoa: int
    defentsa: int
    erasoBerezia: int
    defentsaBerezia: int
    abiadura: int

    # Eboluzio posibleen zerrenda
    eboluzioak: List[str]

    def __init__(self, izena: str, irudia: str, deskripzioa: str,
                 motaZer: List[str], mugimenduZer: List["Mugimendua"],
                 osasuna: int, erasoa: int, defentsa: int,
                 erasoBerezia: int, defentsaBerezia: int,
                 abiadura: int, eboluzioak: List[str]):
        #  Oinarrizko informazioa esleitzen du
        self.izena = izena
        self.irudia = irudia
        self.deskripzioa = deskripzioa

        # Motak eta mugimenduak
        self.motaZer = motaZer
        self.mugimenduZer = mugimenduZer

        # Estatistikak
        self.osasuna = osasuna
        self.erasoa = erasoa
        self.defentsa = defentsa
        self.erasoBerezia = erasoBerezia
        self.defentsaBerezia = defentsaBerezia
        self.abiadura = abiadura

        # Eboluzioen informazioa
        self.eboluzioak = eboluzioak
