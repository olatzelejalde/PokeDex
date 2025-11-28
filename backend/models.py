from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

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
    insignak = db.Column(db.Text, default='[]')

    taldeak = db.relationship('Taldea', backref='erabiltzailea', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'izena': self.izena,
            'telegramKontua': self.telegramKontua,
            'insignak': json.loads(self.insignak) if self.insignak else [],
            'taldeKopurua': len(self.taldeak)
        }
    
    def insignakGehitu(self, insigna):
        insignak_list = json.loads(self.insignak) if self.insignak else []
        if insigna not in insignak_list:
            insignak_list.append(insigna)
            self.insignak = json.dumps(insignak_list)
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