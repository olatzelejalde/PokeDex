import os
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

SPRITE_DIR = "app/static/sprites/pokemon"
os.makedirs(SPRITE_DIR, exist_ok=True)

def download_sprite(pokemon_id: int) -> str:
    """Descarga el sprite y devuelve la ruta local"""
    url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_id}.png"
    local_path = os.path.join(SPRITE_DIR, f"{pokemon_id}.png")
    if not os.path.exists(local_path):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                f.write(r.content)
            print(f"📥 Descargado: {local_path}")
        except Exception as e:
            print(f"⚠️ Error al descargar sprite {pokemon_id}: {e}")
            return "/app/static/img/pokeball.webp"  # imagen por defecto
    return f"/app/static/sprites/pokemon/{pokemon_id}.png"

def mota_it(m): return MOTA_MAP.get(m, m.title())

def seed_gen1(db: Connection):
    print("🔄 Descargando Pokéapi gen 1...")
    species = requests.get("https://pokeapi.co/api/v2/pokemon-species?limit=151").json()['results']

    for idx, s in enumerate(species, 1):
        species_data = requests.get(s['url']).json()
        pokemon_data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{idx}").json()

        stats = {st['stat']['name']: st['base_stat'] for st in pokemon_data['stats']}
        tipos = [t['type']['name'] for t in pokemon_data['types']]

        flavor = next(
            (f['flavor_text'] for f in species_data['flavor_text_entries']
             if f['language']['name'] == 'es'), ""
        ).replace('\n', ' ')

        local_image = download_sprite(pokemon_data['id'])

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
            local_image,
            flavor
        ])

        print(f"✅ {idx:03d} - {pokemon_data['name'].title()} ({local_image})")

    print("✅ Gen 1 kargatuta con imágenes locales!")