from dataclasses import dataclass
from typing import List

from app.domain.pokemon import Pokemon

@dataclass
class Taldea:
    izena: str
    pokemonZer: List[Pokemon]

    def __init__(self, izena: str, pokemonZer: List[Pokemon]):
        self.izena = izena
        self.pokemonZer = pokemonZer