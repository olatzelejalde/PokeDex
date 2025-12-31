from flask import Blueprint, jsonify
import requests

def pokemon_blueprint(db):   # ← debe existir esta función
    bp = Blueprint('pokemonak', __name__, url_prefix='/api')

    MOTA_MAP = {
        'normal': 'normala', 'fire': 'sua', 'water': 'ura',
        'grass': 'belarra', 'electric': 'elektrikoa', 'ice': 'izotza',
        'fighting': 'borroka', 'poison': 'pozoia', 'ground': 'lurra',
        'flying': 'hegaldia', 'psychic': 'psikikoa', 'bug': 'intsektua',
        'rock': 'harria', 'ghost': 'mamua', 'dragon': 'dragoia',
        'dark': 'iluna', 'steel': 'altzairua', 'fairy': 'maitagarria'
    }

    def mota_it(m): return MOTA_MAP.get(m, m.title())

    def fetch_gen1():
        species = requests.get("https://pokeapi.co/api/v2/pokemon-species?limit=151").json()['results']
        for s in species:
            p = requests.get(f"https://pokeapi.co/api/v2/pokemon/{s['name']}").json()
            stats = {st['stat']['name']: st['base_stat'] for st in p['stats']}
            tipos = [t['type']['name'] for t in p['types']]
            yield {
                'id': p['id'],
                'izena': p['name'].title(),
                'mota': mota_it(tipos[0]),
                'mota2': mota_it(tipos[1]) if len(tipos) > 1 else None,
                'hp': stats.get('hp', 0),
                'atakea': stats.get('attack', 0),
                'defentsa': stats.get('defense', 0),
                'atake_berezia': stats.get('special-attack', 0),
                'defentsa_berezia': stats.get('special-defense', 0),
                'abiadura': stats.get('speed', 0),
                'irudia': p['sprites']['front_default']
            }

    @bp.route('/pokemon', methods=['GET'])
    def list_pokemon():
        rows = db.select("SELECT * FROM espeziea ORDER BY id ASC")
        return jsonify([dict(row) for row in rows])

    return bp