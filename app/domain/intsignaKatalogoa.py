from dataclasses import dataclass
from typing import List

from app.domain.intsignia import Intsignia

@dataclass
class IntsignaKatalogoa:
    intsignak: List[Intsignia]
    nireIntsignak: "IntsignaKatalogoa"

    def __init__(self):
        self.intsignak = []
        self.nireIntsignak = self