from dataclasses import dataclass
from typing import List

@dataclass
class Espeziea:
    # Espeziearen oinarrizko informazioa
    izena: str
    irudia: str
    deskripzioa: str

    # Espeziearen motak (sua, belarra...)
    motaZer: List[str]

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
                 motaZer: List[str],osasuna: int, erasoa: int, defentsa: int,
                 erasoBerezia: int, defentsaBerezia: int,
                 abiadura: int, eboluzioak: List[str]):
        #  Oinarrizko informazioa esleitzen du
        self.izena = izena
        self.irudia = irudia
        self.deskripzioa = deskripzioa

        # Motak eta mugimenduak
        self.motaZer = motaZer

        # Estatistikak
        self.osasuna = osasuna
        self.erasoa = erasoa
        self.defentsa = defentsa
        self.erasoBerezia = erasoBerezia
        self.defentsaBerezia = defentsaBerezia
        self.abiadura = abiadura

        # Eboluzioen informazioa
        self.eboluzioak = eboluzioak
