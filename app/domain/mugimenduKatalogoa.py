from dataclasses import dataclass
from typing import List

from app.domain.mugimendua import Mugimendua

@dataclass
class MugimenduKatalogoa:
    mugimenduak: List[Mugimendua]
    nireMotal: "MugimenduKatalogoa"

    def __init__(self):
        self.mugimenduak = []
        self.nireMotal = self