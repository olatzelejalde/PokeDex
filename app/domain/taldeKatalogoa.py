from dataclasses import dataclass
from typing import List

from app.domain.taldea import Taldea

@dataclass
class TaldeKatalogoa:
    taldeak: List[Taldea]
    nireTalde: "TaldeKatalogoa"

    def __init__(self):
        self.taldeak = []
        self.nireTalde = self