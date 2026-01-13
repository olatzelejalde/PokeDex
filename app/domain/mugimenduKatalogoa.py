from dataclasses import dataclass
from typing import List

from app.domain.mugimendua import Mugimendua

@dataclass
class MugimenduKatalogoa:
    # Mugimendu guztien zerrenda
    mugimenduak: List[Mugimendua]
    # Bere burua katalogo nagusi gisa
    nireMotal: "MugimenduKatalogoa"

    def __init__(self):
        # Mugimendu zerrenda hutsa hasieratzen du
        self.mugimenduak = []
        # Bere burua erreferentzia nagusi gisa ezartzen du
        self.nireMotal = self
