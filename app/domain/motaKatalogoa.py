from dataclasses import dataclass
from typing import List

from app.domain.mota import Mota

@dataclass
class MotaKatalogoa:
    # Mota guztiak gordetzen dituen zerrenda
    motak: List[Mota]
    # Bere burua katalogo nagusi bezala
    nireMotak: "MotaKatalogoa"

    def __init__(self):
        # Moten zerrenda hutsa hasieratzen du
        self.motak = []
        # Bere burua katalogo nagusi gisa ezartzen du
        self.nireMotak = self
