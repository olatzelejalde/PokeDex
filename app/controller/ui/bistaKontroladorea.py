from flask import Blueprint, jsonify, request, session
import requests
from app.controller.model.erabiltzaile_controller import ErabiltzaileController
from app.controller.model.mota_controller import MotaController
from app.controller.model.intsignia_controller import IntsigniaController
from app.controller.model.espezie_controller import EspezieController
from app.controller.model.mugimendu_controller import MugimenduController
from app.controller.model.taldea_controller import TaldeaController
from app.controller.model.changelog_controller import ChangelogController
from app.controller.model.pokemon_controller import PokemonController


def register_all_routes(app, db):
    """Registra todas las rutas de la aplicación"""
    
    # ============================================
    # ERABILTZAILEAK (Usuarios)
    # ============================================
    erabiltzaileak_bp = Blueprint('erabiltzaileak', __name__, url_prefix='/api')
    erabiltzaile_ctrl = ErabiltzaileController(db)

    @erabiltzaileak_bp.route('/erabiltzaileak', methods=['GET'])
    def zerrendatu():
        users = erabiltzaile_ctrl.get_all()
        return jsonify([erabiltzaile_ctrl.to_dict(u) for u in users])

    @erabiltzaileak_bp.route('/erabiltzaileak', methods=['POST'])
    def sortu():
        data = request.get_json()
        pasahitza2 = data.get('pasahitza2', data['pasahitza'])
        try:
            erabiltzaile_ctrl.create(
                data['izena'], data['abizena'], data['erabiltzaileIzena'], 
                data['pasahitza'], pasahitza2, data.get('telegramKontua')
            )
            u = erabiltzaile_ctrl.get_by_erabilIzena(data['erabiltzaileIzena'])
            return jsonify(erabiltzaile_ctrl.to_dict(u)), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    @erabiltzaileak_bp.route('/erabiltzaileak/saioa', methods=['POST'])
    def saioa():
        data = request.get_json()
        u = erabiltzaile_ctrl.login(data['erabiltzaileIzena'], data['pasahitza'])
        if u:
            session['uid'] = u.id
            return jsonify(erabiltzaile_ctrl.to_dict(u))
        return jsonify({'error': 'Kredentzial okerrak'}), 401

    @erabiltzaileak_bp.route('/erabiltzaileak/<int:uid>', methods=['GET'])
    def bat(uid):
        u = erabiltzaile_ctrl.get_by_id(uid)
        return jsonify(erabiltzaile_ctrl.to_dict(u) if u else {})

    @erabiltzaileak_bp.route('/erabiltzaileak/<int:uid>', methods=['PUT'])
    def eguneratu(uid):
        data = request.get_json()
        try:
            erabiltzaile_ctrl.update(uid, data)
            user = erabiltzaile_ctrl.get_by_id(uid)
            return jsonify(erabiltzaile_ctrl.to_dict(user))
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    app.register_blueprint(erabiltzaileak_bp)

    # ============================================
    # MOTAK (Tipos)
    # ============================================
    motak_bp = Blueprint('motak', __name__, url_prefix='/api')
    mota_ctrl = MotaController(db)

    @motak_bp.route('/motak', methods=['GET'])
    def listar_motak():
        return jsonify(mota_ctrl.get_all())

    app.register_blueprint(motak_bp)

    # ============================================
    # INTSIGNIAK (Insignias)
    # ============================================
    bp = Blueprint('intsigniak', __name__, url_prefix='/api')
    ctrl = IntsigniaController(db)

    @bp.route('/erabiltzaileak/<int:uid>/intsigniak', methods=['GET'])
    def por_user(uid):
        badges=ctrl.get_all_badges_for_user(uid)
        return jsonify(badges)

    @bp.route('/erabiltzaileak/<int:uid>/intsigniak/<izena>', methods=['POST'])
    def award(uid, izena):
        ctrl.award_badge(uid, izena)
        return jsonify({'message': 'Intsignia eman da'})

    app.register_blueprint(bp)

    # ============================================
    # ESPEZIEAK (Especies)
    # ============================================
    espezieak_bp = Blueprint('espezieak', __name__, url_prefix='/api')
    espezie_ctrl = EspezieController(db)

    @espezieak_bp.route('/espezieak', methods=['GET'])
    def listar_espezieak():
        return jsonify(espezie_ctrl.get_all())

    @espezieak_bp.route('/espezieak/<izena>', methods=['GET'])
    def uno_espezie(izena):
        return jsonify(espezie_ctrl.get_by_name(izena) or {})

    @espezieak_bp.route('/espezieak/<string:izena>/info', methods=['GET'])
    def get_pokemon_info(izena):
        data = espezie_ctrl.get_type_effectiveness(izena)
        if data:
            return jsonify(data)
        else:
            return jsonify({"error": "Ez da aurkitu"}), 404

    @espezieak_bp.route('/espezieak/<string:izena>/ebo', methods=['GET'])
    def get_ebo(izena):
        return jsonify(espezie_ctrl.get_ebo_info(izena))

    @espezieak_bp.route('/espezieak/<string:izena>/scan', methods=['GET'])
    def get_scan(izena):
        return jsonify(espezie_ctrl.get_scan_info(izena))

    app.register_blueprint(espezieak_bp)

    # ============================================
    # POKEMONAK (Pokémon)
    # ============================================
    pokemonak_bp = Blueprint('pokemonak', __name__, url_prefix='/api')
    pokemon_ctrl = PokemonController(db)

    MOTA_MAP = {
        'normal': 'normala', 'fire': 'sua', 'water': 'ura',
        'grass': 'belarra', 'electric': 'elektrikoa', 'ice': 'izotza',
        'fighting': 'borroka', 'poison': 'pozoia', 'ground': 'lurra',
        'flying': 'hegaldia', 'psychic': 'psikikoa', 'bug': 'intsektua',
        'rock': 'harria', 'ghost': 'mamua', 'dragon': 'dragoia',
        'dark': 'iluna', 'steel': 'altzairua', 'fairy': 'maitagarria'
    }

    def mota_it(m): 
        return MOTA_MAP.get(m, m.title())

    @pokemonak_bp.route('/pokemon', methods=['GET'])
    def list_pokemon():
        rows = db.select("""
            SELECT id, izena, mota1 as mota, mota2, osasuna as hp, atakea, defentsa, 
                   atake_berezia, defentsa_berezia, abiadura, irudia 
            FROM espeziea ORDER BY id ASC
        """)
        return jsonify([dict(row) for row in rows])

    @pokemonak_bp.route('/pokemon/motak', methods=['GET'])
    def list_motak_pokemon():
        rows = db.select("SELECT DISTINCT mota1 as mota FROM espeziea WHERE mota1 IS NOT NULL ORDER BY mota1 ASC")
        motak = [row['mota'] for row in rows]
        return jsonify(motak)

    @pokemonak_bp.route('/taldeak/<int:talde_id>/mvp', methods=['GET'])
    def get_mvp(talde_id):
        pokemon_mvp = pokemon_ctrl.get_best_pokemon_by_group(talde_id)
        if pokemon_mvp:
            return jsonify(pokemon_mvp)
        else:
            return jsonify({"error": "Ez da aurkitu"}), 404

    app.register_blueprint(pokemonak_bp)

    # ============================================
    # MUGIMENDUAK (Movimientos)
    # ============================================
    mugimenduak_bp = Blueprint('mugimenduak', __name__, url_prefix='/api')
    mugimendu_ctrl = MugimenduController(db)

    @mugimenduak_bp.route('/especieak/<izena>/mugimenduak', methods=['GET'])
    def por_espezie_mugimendu(izena):
        return jsonify(mugimendu_ctrl.get_by_espezie(izena))

    app.register_blueprint(mugimenduak_bp)

    # ============================================
    # TALDEAK (Equipos)
    # ============================================
    taldeak_bp = Blueprint('taldeak', __name__, url_prefix='/api')
    taldea_ctrl = TaldeaController(db)

    @taldeak_bp.route('/taldeak/erabiltzailea/<int:uid>', methods=['GET'])
    def por_user_taldea(uid):
        return jsonify(taldea_ctrl.get_by_user(uid))

    @taldeak_bp.route('/taldeak/<int:tid>/pokemon', methods=['GET'])
    def pokemon_de_taldea(tid):
        return jsonify(taldea_ctrl.get_pokemonak(tid))

    @taldeak_bp.route('/taldeak', methods=['POST'])
    def crear_taldea():
        data = request.get_json()
        tid = taldea_ctrl.create(data['izena'], data['erabiltzaile_id'])
        return jsonify({'id': tid}), 201

    @taldeak_bp.route('/taldeak/<int:tid>/pokemon', methods=['POST'])
    def add_pokemon_taldea(tid):
        data = request.get_json()
        taldea_ctrl.add_pokemon(tid, data['pokemon_id'])
        return jsonify({'message': 'Pokemon taldera gehituta'})

    @taldeak_bp.route('/taldeak/<int:tid>/pokemon/<int:pid>', methods=['DELETE'])
    def remove_pokemon_taldea(tid, pid):
        taldea_ctrl.remove_pokemon(tid, pid)
        return jsonify({'message': 'Pokemon taldetik kendua'})

    @taldeak_bp.route('/taldeak/<int:tid>', methods=['DELETE'])
    def borrar_taldea(tid):
        taldea_ctrl.delete(tid)
        return jsonify({'message': 'Taldea ezabauta'})

    app.register_blueprint(taldeak_bp)
    # ============================================
    # CHANGELOG
    # ============================================
    changelog_bp = Blueprint('changelog', __name__, url_prefix='/api')
    changelog_ctrl = ChangelogController(db)

    @changelog_bp.route('/changelog', methods=['GET'])
    def zerrendatu_changelog():
        return jsonify(changelog_ctrl.lortu_aldaketa_guztiak())
    
    @changelog_bp.route('/changelog', methods=['POST'])
    def sortu_changelog():
        data = request.get_json()
        changelog_ctrl.create(
            data['bertsioa'],
            data['data'],
            data['deskribapena'],
            data['egilea']
        )
        return jsonify({'message': 'Changelog sarrera sortua'}), 201

    @app.route('/changelog')
    def erakutsi_changelog():
        return render_template('changelog.html', aldaketak=aldaketak)

    app.register_blueprint(changelog_bp)
