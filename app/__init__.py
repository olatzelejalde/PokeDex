import os.path
import sqlite3

from flask_cors import CORS
from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify  # Añade render_template aquí

from app.controller.model.erabiltzaile_controller import ErabiltzaileController
from app.controller.model.pokemon_controller import PokemonController
from app.controller.model.taldea_controller import TaldeaController
from app.controller.model.espezie_controller import EspezieController
from flask import Flask, render_template, redirect, request, flash, session, url_for

from app.domain.erabiltzaileKatalogoa import ErabiltzaileKatalogoa
from app.controller.ui.bistaKontroladorea import register_all_routes
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


    # Crear conexión y catálogo de usuarios
    db = Connection()
    user_ctrl = ErabiltzaileController(db)
    poke_ctrl_model = PokemonController(db)
    taldea_ctrl_model = TaldeaController(db, poke_ctrl_model)
    espezie_ctrl = EspezieController(db)
    users_katalogo = ErabiltzaileKatalogoa(db)
    users_katalogo.erabiltzaileak_kargatu()

    # RUTA PRINCIPAL - Añade esto
    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = users_katalogo.bilatu_by_id(session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('login'))
        return render_template('index.html', user={
            'id': user.id,
            'izena': user.izena,
            'abizena': user.abizena,
            'erabiltzaileIzena': user.erabiltzaileIzena,
            'telegramKontua': user.telegramKontua or '',
            'rola': user.rola,
        })
         
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
            users_katalogo.sortu(
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
        user = users_katalogo.login(
            request.form['erabilIzena'],
            request.form['pasahitza']
        )
        if user:
            session['user_id'] = user.id
            session['erabilIzena'] = user.erabiltzaileIzena
            return redirect(url_for('index'))
        print(">>> EXCEPT ValueError:", 'Kredentzial okerrak')
        return render_template('login.html', error='Kredentzial okerrak')
    
    @app.route('/auth/logout')
    def auth_logout():
        session.clear()
        flash('Saioa itxi da', 'success')
        return redirect(url_for('login'))

    @app.route('/api/taldeak/list', methods=['GET'])
    def api_taldeak_list():
        data = poke_ctrl_model.get_users_with_pokemon()
        return jsonify(data)

    @app.route('/api/taldeak/<int:talde_id>/mvp', methods=['GET'])
    def api_taldeak_mvp(talde_id):
        best = poke_ctrl_model.get_best_pokemon_by_group(talde_id)
        if best:
            return jsonify(best)
        return jsonify({
            "Izena": None,
            "PokeImage": None,
            "Estatistikak": {k: 0 for k in ["Osasuna","Atakea","Defentsa","Atake berezia","Defentsa berezia","Abiadura"]}
        })

    @app.route('/api/espezieak/list', methods=['GET'])
    def api_espezieak_list():
        # Reutilizamos get_all que seguramente ya tengas
        rows = espezie_ctrl.get_all()
        return jsonify(rows)

    @app.route('/api/espezieak/<string:izena>/info', methods=['GET'])
    def api_espezie_info(izena):
        # CAMBIO REALIZADO: get_effectiveness -> get_type_effectiveness
        data = espezie_ctrl.get_type_effectiveness(izena)
        if data:
            return jsonify(data)
        return jsonify({"error": "Ez da aurkitu"}), 404

    @app.route('/api/espezieak/<string:izena>/ebo', methods=['GET'])
    def api_espezie_ebo(izena):
        data = espezie_ctrl.get_ebo_info(izena)
        if data:
            return jsonify(data)
        return jsonify({"error": "Ez da aurkitu"}), 404

    @app.route('/api/espezieak/<string:izena>/scan', methods=['GET'])
    def api_espezie_scan(izena):
        data = espezie_ctrl.get_scan_info(izena)
        if data:
            return jsonify(data)
        return jsonify({"error": "Ez da aurkitu"}), 404
    
    # Registrar todas las rutas de la API
    register_all_routes(app, db, users_katalogo)
    
    # Debug: Mostrar rutas registradas
    with app.app_context():
        print("\n" + "="*50)
        print("RUTAS REGISTRADAS EN LA APLICACIÓN:")
        print("="*50)
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule}")
        print("="*50 + "\n")

    return app

