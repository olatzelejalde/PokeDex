import os.path
import sqlite3

from flask_cors import CORS
from flask import Flask, render_template, redirect, request, flash, session, url_for  # Añade render_template aquí

from app.controller.model.erabiltzaile_controller import ErabiltzaileController
from app.controller.ui.erabiltzaile_routes import erabiltzaile_blueprint
from app.controller.ui.espezie_routes import especie_blueprint
from app.controller.ui.mota_routes import mota_blueprint
from app.controller.ui.mugimendu_routes import mugimendu_blueprint
from app.controller.ui.pokemon_routes import pokemon_blueprint
from app.controller.ui.taldea_routes import taldea_blueprint
from app.controller.ui.intsignia_routes import intsignia_blueprint
from app.database.connection import Connection
from config import Config


def init_db():
    print("Iniciando la base de datos")

    # Verificar si la base de datos existe
    db_exists = os.path.exists(Config.DB_PATH)

    conn = sqlite3.connect(Config.DB_PATH)

    if not db_exists:
        print("Creando base de datos y tablas...")
        try:
            with open('app/database/schema.sql', 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            conn.commit()
            print("Base de datos creada exitosamente")
        except FileNotFoundError:
            print("ERROR: No se encontró schema.sql")

    # ↓↓↓ SIEMPRE: si la tabla espeziea está vacía, poblar ↓↓↓
    with sqlite3.connect(Config.DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM espeziea")
        count = cur.fetchone()['c']
        if count == 0:
            print(">>> Tabla espeziea vacía → poblando gen 1")
            from app.controller.model.seed_pokeapi import seed_gen1
            seed_gen1(Connection())
            print("✅ Gen 1 kargatuta!")

    conn.close()


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # Inicializar base de datos
    init_db()

    # Crear conexión a la base de datos
    db = Connection()
    user_ctrl = ErabiltzaileController(db)

    # RUTA PRINCIPAL - Añade esto
    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = user_ctrl.get_by_id(session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('login'))
        return render_template('index.html', user=user) 
         
    @app.route('/register')
    def register():
        if 'user_id' in session:
            return redirect(url_for('index'))
        return render_template('register.html')
    
    @app.route('/login')
    def login():
        if 'user_id' in session:
            return redirect(url_for('index'))
        return render_template('login.html')
    
    # -------AUTH---------
    @app.route('/auth/register', methods=['POST'])
    def auth_register():
        try:
            user_ctrl.create(
                request.form['izena'],
                request.form['abizena'],
                request.form['erabilIzena'],
                request.form['pasahitza'],
                request.form['pasahitza2'],
                request.form.get('telegramKontua')
            )
            flash('Erregistroa arrakastatsua izan da. Orain saioa hasi dezakezu.', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            print(">>> EXCEPT ValueError:", str(e))
            return render_template('register.html', error=str(e))
        
    @app.route('/auth/login', methods=['POST'])
    def auth_login():
        user = user_ctrl.login(
            request.form['erabilIzena'],
            request.form['pasahitza']
        )
        if user:
            session['user_id'] = user['id']
            session['erabilIzena'] = user['erabilIzena']
            return redirect(url_for('index'))
        print(">>> EXCEPT ValueError:", 'Kredentzial okerrak')
        return render_template('login.html', error='Kredentzial okerrak')
    
    @app.route('/auth/logout')
    def auth_logout():
        session.clear()
        flash('Saioa itxi da', 'success')
        return redirect(url_for('login'))
    
    
    # Registrar blueprints
    app.register_blueprint(erabiltzaile_blueprint(db))
    app.register_blueprint(especie_blueprint(db))
    app.register_blueprint(mota_blueprint(db))
    app.register_blueprint(mugimendu_blueprint(db))
    app.register_blueprint(pokemon_blueprint(db))
    app.register_blueprint(taldea_blueprint(db))
    app.register_blueprint(intsignia_blueprint(db))

    
    
    # Debug: Mostrar rutas registradas
    with app.app_context():
        print("\n" + "="*50)
        print("RUTAS REGISTRADAS EN LA APLICACIÓN:")
        print("="*50)
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule}")
        print("="*50 + "\n")

    return app