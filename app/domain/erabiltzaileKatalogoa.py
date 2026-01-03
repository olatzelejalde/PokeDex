from dataclasses import dataclass
from typing import List, Optional

from app.domain.erabiltzailea import Erabiltzailea

@dataclass
class ErabiltzaileKatalogoa:
    erabiltzaileak: List[Erabiltzailea]
    nireErabiltzaileak: "ErabiltzaileKatalogoa"

    def __init__(self):
        self.erabiltzaileak = []
        self.nireErabiltzaileak = self

    def bilatu_by_id(self, uid: int) -> Optional[Erabiltzailea]:
        """Bilatu erabiltzailea IDren arabera"""
        for erabiltzailea in self.erabiltzaileak:
            if erabiltzailea.id == uid:
                return erabiltzailea
        return None

    def bilatu_by_erabilIzena(self, erabilIzena: str) -> Optional[Erabiltzailea]:
        """Bilatu erabiltzailea erabiltzaile izenaren arabera"""
        for erabiltzailea in self.erabiltzaileak:
            if erabiltzailea.erabiltzaileIzena == erabilIzena:
                return erabiltzailea
        return None

    def gehitu(self, erabiltzailea: Erabiltzailea) -> None:
        """Gehitu erabiltzailea katalogoan"""
        self.erabiltzaileak.append(erabiltzailea)

    def guztiak(self) -> List[Erabiltzailea]:
        """Itzuli guztiak erabiltzaileak"""
        return self.erabiltzaileak