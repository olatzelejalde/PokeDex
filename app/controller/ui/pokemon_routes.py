from flask import Blueprint, jsonify
import requests
from app.controller.model.pokemon_controller import PokemonController

def pokemon_blueprint(db):   # ← debe existir esta función
    bp = Blueprint('pokemonak', __name__, url_prefix='/api')

    controller = PokemonController(db)

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
        rows = db.select("""
            SELECT id, izena, mota1 as mota, mota2, osasuna as hp, atakea, defentsa, 
                   atake_berezia, defentsa_berezia, abiadura, irudia 
            FROM espeziea ORDER BY id ASC
        """)
        return jsonify([dict(row) for row in rows])

    @bp.route('/pokemon/motak', methods=['GET'])
    def list_motak():
        rows = db.select("SELECT DISTINCT mota1 as mota FROM espeziea WHERE mota1 IS NOT NULL ORDER BY mota1 ASC")
        motak = [row['mota'] for row in rows]
        return jsonify(motak)

    @bp.route('/taldeak/<int:talde_id>/mvp', methods=['GET'])
    def get_mvp(talde_id):
        # Llamamos a la función de tu otro archivo
        pokemon = controller.get_best_pokemon_by_group(talde_id)

        if pokemon:
            return jsonify(pokemon)
        else:
            return jsonify({"error": "Ez da aurkitu"}), 404

    return bp