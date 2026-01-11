import requests

POKEAPI_BASE_URL = 'https://pokeapi.co/api/v2'

def fetch_espezie_data(limit=10, offset=0): # Solo carga 10 pokemons
    url = f"{POKEAPI_BASE_URL}/pokemon-species?limit={limit}&offset={offset}"
    return requests.get(url).json()['results']

def fetch_pokemon_data(pokemon_name):
    species = requests.get(f"{POKEAPI_BASE_URL}/pokemon-species/{pokemon_name}").json()
    pokemon = requests.get(f"{POKEAPI_BASE_URL}/pokemon/{pokemon_name}").json()

    flavor = next(
        (f['flavor_text'] for f in species['flavor_text_entries']
         if f['language']['name'] == 'es'), ""
    ).replace('\n', ' ')

    types = [t['type']['name'] for t in pokemon['types']]
    mota1 = types[0] if types else 'normal'
    mota2 = types[1] if len(types) > 1 else None
    
    stats = {stat['stat']['name']: stat['base_stat'] for stat in pokemon['stats']}

    return {
        'izena': species['name'],
        'mota1': mota1,
        'mota2': mota2,
        'osasuna': stats.get('hp', 0),
        'atakea': stats.get('attack', 0),
        'defentsa': stats.get('defense', 0),
        'atake_berezia': stats.get('special-attack', 0),
        'defentsa_berezia': stats.get('special-defense', 0),
        'abiadura': stats.get('speed', 0),
        'irudia': pokemon['sprites']['front_default'],
        'deskribapena': flavor
    }