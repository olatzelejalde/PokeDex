from dataclasses import dataclass
from typing import List

from app.domain.pokemon import Pokemon

@dataclass
class PokemonKatalogoa:
    pokemon: List[Pokemon]
    nirePokemon: "PokemonKatalogoa"

    def __init__(self):
        self.pokemon = []
        self.nirePokemon = self