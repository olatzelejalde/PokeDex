import os.path
import sqlite3

from flask import Flask
from app.database.connection import Connection
from app.routes.PokemonRoutes import pokemon_blueprint
from app.routes.UserRoutes import user_blueprint
from app.routes.TeamRoutes import team_blueprint
from config import Config

def init_db():
    print("📦 Inicializando la base de datos...")
    if os.path.exists(Config.DB_PATH):
        print("✅ La base de datos ya existe.")
        conn = sqlite3.connect(Config.DB_PATH)
        with open("app/database/schema.sql") as f:
            conn.executescript(f.read())
        conn.close()
        print("✅ La base de datos se ha inicializado correctamente.")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db()

    db = Connection()

    app.register_blueprint(pokemon_blueprint(db))
    app.register_blueprint(user_blueprint(db))
    app.register_blueprint(team_blueprint(db))

    return app
