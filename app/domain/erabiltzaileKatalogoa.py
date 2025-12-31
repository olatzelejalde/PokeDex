from dataclasses import dataclass
from typing import List

from app.domain.erabiltzailea import Erabiltzailea

@dataclass
class ErabiltzaileKatalogoa:
    erabiltzaileak: List[Erabiltzailea]
    nireErabiltzaileak: "ErabiltzaileKatalogoa"

    def __init__(self):
        self.erabiltzaileak = []
        self.nireErabiltzaileak = self