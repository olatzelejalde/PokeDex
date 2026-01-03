from dataclasses import dataclass
from typing import List

from app.domain.espeziea import Espeziea

@dataclass
class EspezieKatalogoa:
    espezieZerrenda: List[Espeziea]
    nireEspezieKatalogoa: "EspezieKatalogoa"

    def __init__(self):
        self.espezieZerrenda = []
        self.nireEspezieKatalogoa = self