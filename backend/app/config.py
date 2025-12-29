import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    # SQLite
    DB_PATH = os.path.join(BASE_DIR, "library.sqlite")
    SECRET_KEY = "andreacf_sql"

    # Pokeapi
    POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/"
    MAX_POKEMON = 10

    # JWT autentifikazioa
    JWT_SECRET = "andreacf_jwt"

    # balidazioak
    MIN_PASSWORD_LENGTH = 6
    MAX_TEAM_SIZE = 6

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}