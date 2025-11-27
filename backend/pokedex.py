from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from models import db, Pokemon, Erabiltzailea, Taldea

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokedex.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración CORS
CORS(app)

db.init_app(app)

MOTA_ZERRENDA = {
    'normal': 'normala',
    'fire': 'sua',
    'water': 'ura',
    'grass': 'belarra',
    'electric': 'elektrikoa',
    'ice': 'izotza',
    'fighting': 'borroka',
    'poison': 'pozoia',
    'ground': 'lurra',
    'flying': 'hegaldia',
    'psychic': 'psikikoa',
    'bug': 'intsektua',
    'rock': 'harria',
    'ghost': 'mamua',
    'dragon': 'dragoia',
    'dark': 'iluna',
    'steel': 'altzairua',
    'fairy': 'maitagarria'
}

def motaItzuli(mota):
    return MOTA_ZERRENDA.get(mota.lower(), mota.title())

def datuakKargatuPokeApi():
    print("PokeAPI datuak kargatzen...")

    for pokemonId in range(1, 152):
        try:
            if Pokemon.query.get(pokemonId):
                continue
            
            response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemonId}')
            if response.status_code == 200:
                pokemonData = response.json()
                espezieResponse = requests.get(f'https://pokeapi.co/api/v2/pokemon-species/{pokemonId}')
                espezieData = espezieResponse.json() if espezieResponse.status_code == 200 else {}

                izenaItzulia = pokemonData['name'].title()
                for name in espezieData.get('names', []):
                    if name['language']['name'] == 'eu':
                        izenaItzulia = name['name']
                        break
                
                motak = [mota['type']['name'] for mota in pokemonData['types']]
                mota1 = motaItzuli(motak[0])
                mota2 = motaItzuli(motak[1]) if len(motak) > 1 else None

                stats = {stat['stat']['name']: stat['base_stat'] for stat in pokemonData['stats']}

                pokemon = Pokemon(
                    id=pokemonData['id'],
                    izena=izenaItzulia,
                    mota=mota1,
                    mota2=mota2,
                    hp=stats.get('hp', 0),
                    atakea=stats.get('attack', 0),
                    defentsa=stats.get('defense', 0),
                    abiadura=stats.get('speed', 0),
                    irudia=pokemonData['sprites']['front_default']
                )
                db.session.add(pokemon)
                print(f'✅ Kargatu da: {izenaItzulia} (ID: {pokemonId})')
                
        except Exception as e:
            print(f'❌ Errorea kargatzean ID {pokemonId}: {e}')
    
    db.session.commit()
    print("✅ Datu guztiak kargatu dira.")

# ==================== RUTAS DE POKÉMON ====================
@app.route('/api/pokemon', methods=['GET'])
def getPokemon():
    pokemonZerrenda = Pokemon.query.all()
    return jsonify([p.to_dict() for p in pokemonZerrenda])

@app.route('/api/pokemon/<int:pokemon_id>', methods=['GET'])
def getPokemonById(pokemon_id):
    pokemon = Pokemon.query.get_or_404(pokemon_id)
    return jsonify(pokemon.to_dict())

@app.route('/api/pokemon/bilatu', methods=['GET'])
def bilatuPokemon():
    izena = request.args.get('izena', '')
    mota = request.args.get('mota', '')

    query = Pokemon.query
    if izena:
        query = query.filter(Pokemon.izena.ilike(f'%{izena}%'))
    if mota:
        query = query.filter((Pokemon.mota.ilike(f'%{mota}%')) | (Pokemon.mota2.ilike(f'%{mota}%')))
    
    emaitza = query.all()
    return jsonify([p.to_dict() for p in emaitza])

@app.route('/api/pokemon/motak', methods=['GET'])
def getMotak():
    motak = db.session.query(Pokemon.mota).distinct().all()
    motak = [mota[0] for mota in motak if mota[0]]
    return jsonify(motak)

# ==================== RUTAS DE ERABILTZAILEA ====================
@app.route('/api/erabiltzaileak', methods=['POST'])
def createErabiltzailea():
    try:
        data = request.get_json()
        print("🎯 Erabiltzailea sortzeko datuak:", data)
        
        # Egiaztatu datuak
        if not data:
            return jsonify({'error': 'Datuak beharrezkoak dira'}), 400
            
        if 'izena' not in data or not data['izena'].strip():
            return jsonify({'error': 'Izena beharrezkoa da'}), 400
            
        if 'pasahitza' not in data or not data['pasahitza']:
            return jsonify({'error': 'Pasahitza beharrezkoa da'}), 400
        
        izena = data['izena'].strip()
        pasahitza = data['pasahitza']
        
        # Egiaztatu erabiltzailea existitzen den
        existitzen_da = Erabiltzailea.query.filter_by(izena=izena).first()
        if existitzen_da:
            return jsonify({'error': 'Erabiltzaile izena jada existitzen da'}), 409
        
        # Sortu erabiltzaile berria
        erabiltzailea = Erabiltzailea(
            izena=izena,
            pasahitza=pasahitza,
            telegramKontua=data.get('telegramKontua')
        )
        
        db.session.add(erabiltzailea)
        db.session.commit()
        
        print(f"✅ Erabiltzailea sortu da: {erabiltzailea.izena} (ID: {erabiltzailea.id})")
        return jsonify(erabiltzailea.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Errorea erabiltzailea sortzean: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Barneko errorea erabiltzailea sortzean'}), 500

@app.route('/api/erabiltzaileak/saioa', methods=['POST'])
def saioaHasi():
    try:
        data = request.get_json()
        print("🔐 Saioa hasteko datuak:", data)
        
        if not data:
            return jsonify({'error': 'Datuak beharrezkoak dira'}), 400
            
        if 'izena' not in data or not data['izena']:
            return jsonify({'error': 'Izena beharrezkoa da'}), 400
            
        if 'pasahitza' not in data or not data['pasahitza']:
            return jsonify({'error': 'Pasahitza beharrezkoa da'}), 400
        
        izena = data['izena'].strip()
        pasahitza = data['pasahitza']
        
        # Bilatu erabiltzailea
        erabiltzailea = Erabiltzailea.query.filter_by(izena=izena).first()
        
        if erabiltzailea:
            print(f"🔍 Erabiltzailea aurkitu: {erabiltzailea.izena}")
            print(f"🔑 Pasahitza konparatzen: sartutakoa='{pasahitza}', db='{erabiltzailea.pasahitza}'")
            
            if erabiltzailea.pasahitza == pasahitza:
                print(f"✅ Saioa hasteko: {erabiltzailea.izena}")
                return jsonify(erabiltzailea.to_dict())
            else:
                print("❌ Pasahitza okerra")
                return jsonify({'error': 'Erabiltzaile izena edo pasahitza okerra'}), 401
        else:
            print("❌ Erabiltzailea ez da aurkitu")
            return jsonify({'error': 'Erabiltzaile izena edo pasahitza okerra'}), 401
            
    except Exception as e:
        print(f"❌ Errorea saioa hasten: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Barneko errorea saioa hasten'}), 500

@app.route('/api/erabiltzaileak/<int:erabiltzailea_id>', methods=['GET'])
def getErabiltzailea(erabiltzailea_id):
    try:
        erabiltzailea = Erabiltzailea.query.get(erabiltzailea_id)
        if erabiltzailea:
            return jsonify(erabiltzailea.to_dict())
        else:
            return jsonify({'error': 'Erabiltzailea ez da aurkitu'}), 404
    except Exception as e:
        print(f"❌ Errorea erabiltzailea eskuratzean: {str(e)}")
        return jsonify({'error': 'Barneko errorea erabiltzailea eskuratzean'}), 500

# ==================== RUTAS DE TALDEAK ====================
@app.route('/api/taldeak', methods=['POST'])
def createTaldea():
    try:
        data = request.json
        print("🏆 Taldea sortzeko datuak:", data)
        
        taldea = Taldea(
            izena=data['izena'],
            erabiltzailea_id=data['erabiltzailea_id']
        )

        db.session.add(taldea)
        db.session.commit()
        
        print(f"✅ Taldea sortu da: {taldea.izena} (ID: {taldea.id})")
        return jsonify(taldea.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Errorea taldea sortzean: {str(e)}")
        return jsonify({'error': 'Barneko errorea taldea sortzean'}), 500

@app.route('/api/taldeak/<int:taldea_id>/pokemon', methods=['POST'])
def addPokemonToTaldea(taldea_id):
    try:
        data = request.json
        print(f"➕ Pokémon gehitzen taldera {taldea_id}:", data)
        
        taldea = Taldea.query.get_or_404(taldea_id)
        pokemon = Pokemon.query.get_or_404(data['pokemon_id'])

        if len(taldea.pokemonak) >= 6:
            return jsonify({'error': 'Taldeak ezin du 6 pokemon baino gehiago izan'}), 400
        
        taldea.pokemonak.append(pokemon)
        db.session.commit()
        
        print(f"✅ Pokémon gehituta: {pokemon.izena} -> {taldea.izena}")
        return jsonify(taldea.to_dict())
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Errorea Pokémona taldera gehitzean: {str(e)}")
        return jsonify({'error': 'Barneko errorea Pokémona taldera gehitzean'}), 500

@app.route('/api/taldeak/<int:taldea_id>/pokemon/<int:pokemon_id>', methods=['DELETE'])
def removePokemonFromTaldea(taldea_id, pokemon_id):
    try:
        taldea = Taldea.query.get_or_404(taldea_id)
        pokemon = Pokemon.query.get_or_404(pokemon_id)
        
        if pokemon in taldea.pokemonak:
            taldea.pokemonak.remove(pokemon)
            db.session.commit()
            print(f"✅ Pokémon kenduta: {pokemon.izena} -> {taldea.izena}")
        
        return jsonify(taldea.to_dict())
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Errorea Pokémona taldetik kentzean: {str(e)}")
        return jsonify({'error': 'Barneko errorea Pokémona taldetik kentzean'}), 500

@app.route('/api/taldeak/erabiltzailea/<int:erabiltzailea_id>', methods=['GET'])
def getTaldeakByErabiltzailea(erabiltzailea_id):
    try:
        taldeak = Taldea.query.filter_by(erabiltzailea_id=erabiltzailea_id).all()
        print(f"📋 Erabiltzaile {erabiltzailea_id} taldeak: {len(taldeak)}")
        return jsonify([t.to_dict() for t in taldeak])
        
    except Exception as e:
        print(f"❌ Errorea taldeak kargatzean: {str(e)}")
        return jsonify({'error': 'Barneko errorea taldeak kargatzean'}), 500

@app.route('/api/taldeak/<int:taldea_id>', methods=['DELETE'])
def deleteTaldea(taldea_id):
    try:
        taldea = Taldea.query.get_or_404(taldea_id)
        db.session.delete(taldea)
        db.session.commit()
        print(f"🗑️ Taldea ezabatu da: {taldea.izena}")
        return jsonify({'message': 'Taldea ezabatu da'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Errorea taldea ezabatzean: {str(e)}")
        return jsonify({'error': 'Barneko errorea taldea ezabatzean'}), 500

@app.route('/api/taldeak/<int:taldea_id>/partekatu', methods=['POST'])
def partekatuTaldea(taldea_id):
    try:
        data = request.json
        taldea = Taldea.query.get_or_404(taldea_id)
        erabiltzailea = taldea.erabiltzailea
        
        print(f"📤 Taldea partekatzen: {taldea.izena} -> {erabiltzailea.izena}")
        
        # Simulatu Telegram partekatzea
        if erabiltzailea.telegramKontua:
            partekatzea_arrakastatsua = True  # Simulatuta
            
            if partekatzea_arrakastatsua:
                # Insignia eman
                if erabiltzailea.insignakGehitu("partekatzaile_aktiboa"):
                    db.session.commit()
                    print(f"🎖️ Intsigna eman da: partekatzaile_aktiboa")
                
                return jsonify({
                    'message': 'Taldea arrakastaz partekatu da',
                    'intsigna': 'partekatzaile_aktiboa'
                })
            else:
                return jsonify({'error': 'Errorea taldea partekatzean'}), 500
        else:
            return jsonify({'error': 'Erabiltzaileak ez du Telegram konturik'}), 400
            
    except Exception as e:
        print(f"❌ Errorea taldea partekatzean: {str(e)}")
        return jsonify({'error': 'Barneko errorea taldea partekatzean'}), 500

# ==================== EXEKUTATZEA ====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        datuakKargatuPokeApi()
    app.run(debug=True, port=5000)