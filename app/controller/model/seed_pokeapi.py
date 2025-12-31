import requests
from app.database.connection import Connection

MOTA_MAP = {
    'normal': 'normala', 'fire': 'sua', 'water': 'ura',
    'grass': 'belarra', 'electric': 'elektrikoa', 'ice': 'izotza',
    'fighting': 'borroka', 'poison': 'pozoia', 'ground': 'lurra',
    'flying': 'hegaldia', 'psychic': 'psikikoa', 'bug': 'intsektua',
    'rock': 'harria', 'ghost': 'mamua', 'dragon': 'dragoia',
    'dark': 'iluna', 'steel': 'altzairua', 'fairy': 'maitagarria'
}

def mota_it(m): return MOTA_MAP.get(m, m.title())

def seed_gen1(db: Connection):
    """Descarga gen 1 y guarda: 151 especies"""
    print("🔄 Descargando Pokéapi gen 1...")
    species = requests.get("https://pokeapi.co/api/v2/pokemon-species?limit=151").json()['results']

    for idx, s in enumerate(species, 1):
        # ---------- DATOS DE LA ESPECIE ----------
        species_data = requests.get(s['url']).json()
        pokemon_data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{idx}").json()

        stats = {st['stat']['name']: st['base_stat'] for st in pokemon_data['stats']}
        tipos = [t['type']['name'] for t in pokemon_data['types']]

        # Descripción en español
        flavor = next(
            (f['flavor_text'] for f in species_data['flavor_text_entries']
             if f['language']['name'] == 'es'), ""
        ).replace('\n', ' ')

        # ---------- INSERTAR ESPECIE ----------
        db.insert("""
            INSERT OR IGNORE INTO espeziea (id, izena, mota1, mota2, osasuna, atakea, defentsa,
                                            atake_berezia, defentsa_berezia, abiadura, irudia, deskribapena)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            pokemon_data['id'],
            pokemon_data['name'].title(),
            mota_it(tipos[0]),
            mota_it(tipos[1]) if len(tipos) > 1 else None,
            stats['hp'], stats['attack'], stats['defense'],
            stats['special-attack'], stats['special-defense'], stats['speed'],
            pokemon_data['sprites']['front_default'],
            flavor
        ])

        print(f"✅ {idx:03d} - {pokemon_data['name'].title()}")

    print("✅ Gen 1 kargatuta!")