from dataclasses import dataclass
from typing import List

from app.domain.espeziea import Espeziea

@dataclass
class EspezieKatalogoa:
    # Espezie guztien zerrenda
    espezieZerrenda: List[Espeziea]
    # Katalogoaren bere buruaren erreferentzia
    nireEspezieKatalogoa: "EspezieKatalogoa"

    def __init__(self):
        # Espezieen zerrenda hutsa hasieratzen du
        self.espezieZerrenda = []
        # Bere burua katalogo nagusi bezala ezartzen du
        self.nireEspezieKatalogoa = self
