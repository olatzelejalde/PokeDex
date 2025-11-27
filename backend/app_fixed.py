from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
import os

# Inicializar extensiones
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokedex.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuración CORS
    CORS(app)
    
    # Inicializar extensiones con la app
    db.init_app(app)
    
    return app

app = create_app()

# Definir modelos
pokemon_taldea = db.Table('pokemon_taldea',
    db.Column('pokemon_id', db.Integer, db.ForeignKey('pokemon.id'), primary_key=True),
    db.Column('taldea_id', db.Integer, db.ForeignKey('taldea.id'), primary_key=True)
)

class Pokemon(db.Model):
    __tablename__ = 'pokemon'

    id = db.Column(db.Integer, primary_key=True)
    izena = db.Column(db.String(100), nullable=False)
    mota = db.Column(db.String(50), nullable=True)
    mota2 = db.Column(db.String(50), nullable=True)
    hp = db.Column(db.Integer, nullable=False)
    atakea = db.Column(db.Integer, nullable=False)
    defentsa = db.Column(db.Integer, nullable=False)
    abiadura = db.Column(db.Integer, nullable=False)
    irudia = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'izena': self.izena,
            'mota': self.mota,
            'mota2': self.mota2,
            'hp': self.hp,
            'atakea': self.atakea,
            'defentsa': self.defentsa,
            'abiadura': self.abiadura,
            'irudia': self.irudia
        }

class Erabiltzailea(db.Model):
    __tablename__ = 'erabiltzailea'

    id = db.Column(db.Integer, primary_key=True)
    izena = db.Column(db.String(100), unique=True, nullable=False)
    pasahitza = db.Column(db.String(200), nullable=False)
    telegramKontua = db.Column(db.String(100), nullable=True)
    insignak = db.Column(db.JSON, default=list)

    taldeak = db.relationship('Taldea', backref='erabiltzailea', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'izena': self.izena,
            'telegramKontua': self.telegramKontua,
            'insignak': self.insignak,
            'taldeKopurua': len(self.taldeak)
        }
    
    def insignakGehitu(self, insigna):
        if insigna not in self.insignak:
            self.insignak.append(insigna)
            return True
        return False

class Taldea(db.Model):
    __tablename__ = 'taldea'

    id = db.Column(db.Integer, primary_key=True)
    izena = db.Column(db.String(100), nullable=False)
    erabiltzailea_id = db.Column(db.Integer, db.ForeignKey('erabiltzailea.id'), nullable=False)

    pokemonak = db.relationship('Pokemon', secondary=pokemon_taldea, lazy='subquery',
        backref=db.backref('taldeak', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'izena': self.izena,
            'erabiltzailea_id': self.erabiltzailea_id,
            'pokemonak': [p.to_dict() for p in self.pokemonak],
            'pokemonKopurua': len(self.pokemonak)
        }

# Configuración de tipos
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

# ==================== RUTAS ====================

@app.route('/api/pokemon', methods=['GET'])
def getPokemon():
    try:
        pokemonZerrenda = Pokemon.query.all()
        return jsonify([p.to_dict() for p in pokemonZerrenda])
    except Exception as e:
        print(f"❌ Errorea Pokémonak eskuratzean: {e}")
        return jsonify({'error': 'Errorea datuak eskuratzean'}), 500

@app.route('/api/pokemon/<int:pokemon_id>', methods=['GET'])
def getPokemonById(pokemon_id):
    try:
        pokemon = Pokemon.query.get_or_404(pokemon_id)
        return jsonify(pokemon.to_dict())
    except Exception as e:
        print(f"❌ Errorea Pokémona eskuratzean: {e}")
        return jsonify({'error': 'Pokémona ez da aurkitu'}), 404

@app.route('/api/pokemon/bilatu', methods=['GET'])
def bilatuPokemon():
    try:
        izena = request.args.get('izena', '')
        mota = request.args.get('mota', '')

        query = Pokemon.query
        if izena:
            query = query.filter(Pokemon.izena.ilike(f'%{izena}%'))
        if mota:
            query = query.filter((Pokemon.mota.ilike(f'%{mota}%')) | (Pokemon.mota2.ilike(f'%{mota}%')))
        
        emaitza = query.all()
        return jsonify([p.to_dict() for p in emaitza])
    except Exception as e:
        print(f"❌ Errorea Pokémonak bilatzean: {e}")
        return jsonify({'error': 'Errorea bilaketan'}), 500

@app.route('/api/pokemon/motak', methods=['GET'])
def getMotak():
    try:
        motak = db.session.query(Pokemon.mota).distinct().all()
        motak = [mota[0] for mota in motak if mota[0]]
        return jsonify(motak)
    except Exception as e:
        print(f"❌ Errorea motak eskuratzean: {e}")
        return jsonify({'error': 'Errorea motak eskuratzean'}), 500

@app.route('/api/erabiltzaileak', methods=['POST'])
def createErabiltzailea():
    try:
        data = request.get_json()
        print("🎯 Erabiltzailea sortzeko datuak:", data)
        
        if not data:
            return jsonify({'error': 'Datuak beharrezkoak dira'}), 400
            
        izena = data.get('izena', '').strip()
        pasahitza = data.get('pasahitza', '')
        
        if not izena:
            return jsonify({'error': 'Izena beharrezkoa da'}), 400
            
        if not pasahitza:
            return jsonify({'error': 'Pasahitza beharrezkoa da'}), 400
        
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
            
        izena = data.get('izena', '').strip()
        pasahitza = data.get('pasahitza', '')
        
        if not izena:
            return jsonify({'error': 'Izena beharrezkoa da'}), 400
            
        if not pasahitza:
            return jsonify({'error': 'Pasahitza beharrezkoa da'}), 400
        
        # Bilatu erabiltzailea
        erabiltzailea = Erabiltzailea.query.filter_by(izena=izena).first()
        
        if erabiltzailea and erabiltzailea.pasahitza == pasahitza:
            print(f"✅ Saioa hasteko: {erabiltzailea.izena}")
            return jsonify(erabiltzailea.to_dict())
        else:
            print("❌ Saioa hasteko errorea: erabiltzailea edo pasahitza okerra")
            return jsonify({'error': 'Erabiltzaile izena edo pasahitza okerra'}), 401
            
    except Exception as e:
        print(f"❌ Errorea saioa hasten: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Barneko errorea saioa hasten'}), 500

# Rutas simples para Taldeak (para probar primero)
@app.route('/api/taldeak', methods=['POST'])
def createTaldea():
    try:
        data = request.get_json()
        taldea = Taldea(
            izena=data['izena'],
            erabiltzailea_id=data['erabiltzailea_id']
        )
        db.session.add(taldea)
        db.session.commit()
        return jsonify(taldea.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"❌ Errorea taldea sortzean: {e}")
        return jsonify({'error': 'Errorea taldea sortzean'}), 500

@app.route('/api/taldeak/erabiltzailea/<int:erabiltzailea_id>', methods=['GET'])
def getTaldeakByErabiltzailea(erabiltzailea_id):
    try:
        taldeak = Taldea.query.filter_by(erabiltzailea_id=erabiltzailea_id).all()
        return jsonify([t.to_dict() for t in taldeak])
    except Exception as e:
        print(f"❌ Errorea taldeak kargatzean: {e}")
        return jsonify({'error': 'Errorea taldeak kargatzean'}), 500

# ==================== INICIALIZACIÓN ====================

def initialize_database():
    """Inicializar la base de datos"""
    with app.app_context():
        # Crear tablas
        db.create_all()
        print("✅ Database tablak sortu dira")
        
        # Comprobar si ya hay datos
        pokemon_count = Pokemon.query.count()
        if pokemon_count == 0:
            print("🔍 Pokémon datuak kargatzen...")
            datuakKargatuPokeApi()
        else:
            print(f"✅ {pokemon_count} Pokémon dagoeneko datu-basean")
        
        # Crear usuario demo si no existe
        demo_user = Erabiltzailea.query.filter_by(izena='demo').first()
        if not demo_user:
            demo_user = Erabiltzailea(izena='demo', pasahitza='demo123')
            db.session.add(demo_user)
            db.session.commit()
            print("✅ Erabiltzaile demo sortu da: demo / demo123")

if __name__ == '__main__':
    # Limpiar archivo de base de datos viejo si existe
    if os.path.exists('pokedex.db'):
        os.remove('pokedex.db')
        print("🗑️  Database zaharra ezabatu da")
    
    # Inicializar
    initialize_database()
    
    # Ejecutar aplicación
    print("🚀 Backend abiarazten http://localhost:5000")
    app.run(debug=True, port=5000)