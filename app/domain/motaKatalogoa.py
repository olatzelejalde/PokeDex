from dataclasses import dataclass
from typing import List

from app.domain.mota import Mota

@dataclass
class MotaKatalogoa:
    motak: List[Mota]
    nireMotak: "MotaKatalogoa"

    def __init__(self):
        self.motak = []
        self.nireMotak = self