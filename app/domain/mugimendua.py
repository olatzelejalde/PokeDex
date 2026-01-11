from dataclasses import dataclass
from typing import List

@dataclass
class Mugimendua:
    izena: str
    indarra: int
    zehaztasuna: float
    mota: List[str]

    def __init__(self, izena: str, indarra: int,
                 zehaztasuna: float, mota: List[str]):
        self.izena = izena
        self.indarra = indarra
        self.zehaztasuna = zehaztasuna
        self.mota = mota