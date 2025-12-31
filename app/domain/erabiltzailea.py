from dataclasses import dataclass
from typing import Optional, List

from app.domain.intsignia import Intsignia
from app.domain.taldea import Taldea
from app.domain.notifikazio import Notifikazio

@dataclass
class Erabiltzailea:
    izena: str
    abizena: str
    erabiltzaileIzena: str
    telegramKontua: str
    pasahitza: str
    rola: str
    intsigniaZer: List["Intsignia"]
    lagunZer: List["Erabiltzailea"]
    taldeZer: List["Taldea"]
    notifZer: List["Notifikazio"]

    def __init__(self, izena: str, abizena: str, erabiltzaileIzena: str,
                 pasahitza: str, rola: str, telegramKontua: str = ""):
        self.izena = izena
        self.abizena = abizena
        self.erabiltzaileIzena = erabiltzaileIzena
        self.telegramKontua = telegramKontua
        self.pasahitza = pasahitza
        self.rola = rola
        self.intsigniaZer = []
        self.lagunZer = []
        self.taldeZer = []
        self.notifZer = []