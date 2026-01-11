from flask import Blueprint, jsonify, request, session
import logging
import os
import threading
import time
import requests
from app.domain.erabiltzaileKatalogoa import ErabiltzaileKatalogoa
from app.domain.taldeKatalogoa import TaldeKatalogoa
from app.controller.model.mota_controller import MotaController
from app.controller.model.intsignia_controller import IntsigniaController
from app.controller.model.espezie_controller import EspezieController
from app.controller.model.mugimendu_controller import MugimenduController
from app.controller.model.taldea_controller import TaldeaController
from app.services.telegram_service import TelegramService


def register_all_routes(app, db, users_katalogo=None, taldeak_katalogo=None):
    """Registra todas las rutas de la aplicación"""
    
    # ============================================
    # ERABILTZAILEAK (Usuarios)
    # ============================================
    telegram_service = TelegramService()
    erabiltzaileak_bp = Blueprint('erabiltzaileak', __name__, url_prefix='/api')

    if users_katalogo is None:
        users_katalogo = ErabiltzaileKatalogoa(db)
        users_katalogo.erabiltzaileak_kargatu()

    if taldeak_katalogo is None:
        taldeak_katalogo = TaldeKatalogoa(db)
        taldeak_katalogo.kargatu_from_bd()

    # --- TELEGRAM POLLING (LOCAL) ---
    if os.getenv("TELEGRAM_USE_POLLING") == "1" and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        def _on_start(chat_id: int, telegram_username: str | None, payload: str | None) -> bool:
            # payload = erabilIzena opcional (/start <erabilIzena>)
            u = users_katalogo.lotu_telegram_chat_id(
                chat_id=chat_id,
                telegram_username=telegram_username,
                erabilIzena=payload,
            )
            return u is not None

        telegram_service.start_polling(_on_start)

    def _user_to_dict(u):
        return {
            'id': u.id,
            'izena': u.izena,
            'abizena': u.abizena,
            'erabiltzaileIzena': u.erabiltzaileIzena,
            'telegramKontua': u.telegramKontua or '',
            'rola': u.rola,
        }

    @erabiltzaileak_bp.route('/erabiltzaileak', methods=['GET'])
    def zerrendatu():
        users = users_katalogo.guztiak()
        return jsonify([_user_to_dict(u) for u in users])

    @erabiltzaileak_bp.route('/erabiltzaileak', methods=['POST'])
    def sortu():
        data = request.get_json()
        pasahitza2 = data.get('pasahitza2', data['pasahitza'])
        try:
            u = users_katalogo.sortu(
                data['izena'], data['abizena'], data['erabiltzaileIzena'], 
                data['pasahitza'], pasahitza2, data.get('telegramKontua')
            )
            return jsonify(_user_to_dict(u)), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    @erabiltzaileak_bp.route('/erabiltzaileak/saioa', methods=['POST'])
    def saioa():
        data = request.get_json()
        u = users_katalogo.login(data['erabiltzaileIzena'], data['pasahitza'])
        if u:
            session['uid'] = u.id
            return jsonify(_user_to_dict(u))
        return jsonify({'error': 'Kredentzial okerrak'}), 401

    @erabiltzaileak_bp.route('/erabiltzaileak/<int:uid>', methods=['GET'])
    def bat(uid):
        u = users_katalogo.bilatu_by_id(uid)
        return jsonify(_user_to_dict(u) if u else {})

    @erabiltzaileak_bp.route('/erabiltzaileak/<int:uid>', methods=['PUT'])
    def eguneratu(uid):
        data = request.get_json()
        try:
            user = users_katalogo.actualizar(uid, data)
            return jsonify(_user_to_dict(user))
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    @erabiltzaileak_bp.route('/erabiltzaileak/<int:uid>/lagunak', methods=['GET'])
    def get_lagunak(uid):
        lagunak = users_katalogo.lortu_lagunak(uid, telegram_du=False)
        return jsonify([_user_to_dict(u) for u in lagunak])

    @erabiltzaileak_bp.route('/erabiltzaileak/<int:uid>/lagunak/telegram', methods=['GET'])
    def get_lagunak_telegram(uid):
        lagunak = users_katalogo.lortu_lagunak(uid, telegram_du=True)
        return jsonify([_user_to_dict(u) for u in lagunak])

    @erabiltzaileak_bp.route('/erabiltzaileak/bilatu/<izena>', methods=['GET'])
    def bilatu_erabiltzaileak(izena):
        erabiltzaileak = users_katalogo.bilatu_erabiltzaileak_by_nombre(izena)
        return jsonify([_user_to_dict(u) for u in erabiltzaileak])

    @erabiltzaileak_bp.route('/erabiltzaileak/<int:uid1>/gehitu-laguna/<int:uid2>', methods=['POST'])
    def gehitu_laguna(uid1, uid2):
        try:
            users_katalogo.gehitu_laguna(uid1, uid2)
            return jsonify({'message': 'Laguna gehitu da'}), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    @erabiltzaileak_bp.route('/erabiltzaileak/<int:uid1>/kendu-laguna/<int:uid2>', methods=['DELETE'])
    def kendu_laguna(uid1, uid2):
        try:
            users_katalogo.kendu_laguna(uid1, uid2)
            return jsonify({'message': 'Laguna kendua'})
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    @erabiltzaileak_bp.route('/erabiltzaileak/activateTelegram/<int:uid>', methods=['POST'])
    def activate_telegram(uid):
        """
        Guarda telegramKontua del usuario; el chat_id se guarda cuando el usuario hace /start al bot.
        """
        data = request.get_json(silent=True) or {}
        telegram_kontua = data.get('telegramKontua')

        if not telegram_kontua:
            return jsonify({'error': 'telegramKontua beharrezkoa da'}), 400

        try:
            user = users_katalogo.actualizar(uid, {'telegramKontua': telegram_kontua})
            return jsonify({
                'message': 'OK. Orain Telegram bot-ean idatzi: /start',
                'user': _user_to_dict(user),
            }), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    app.register_blueprint(erabiltzaileak_bp)

    # ============================================
    # TELEGRAM WEBHOOK
    # ============================================
    telegram_bp = Blueprint('telegram', __name__, url_prefix='/telegram')

    @telegram_bp.route('/webhook', methods=['POST'])
    def telegram_webhook():
        update = request.get_json(silent=True) or {}

        msg = update.get('message') or update.get('edited_message')
        if not msg:
            return jsonify({'ok': True})

        text = (msg.get('text') or '').strip()
        if not text.startswith('/start'):
            return jsonify({'ok': True})

        chat = msg.get('chat') or {}
        from_ = msg.get('from') or {}
        chat_id = chat.get('id')
        telegram_username = from_.get('username')  # puede ser None si el usuario no tiene username

        # /start <erabilIzena> (deep-link opcional)
        parts = text.split(maxsplit=1)
        erabilIzena = parts[1].strip() if len(parts) > 1 else None

        if not chat_id:
            return jsonify({'ok': True})

        user = users_katalogo.lotu_telegram_chat_id(
            chat_id=int(chat_id),
            telegram_username=telegram_username,
            erabilIzena=erabilIzena
        )

        if user:
            telegram_service.send_message(
                chat_id=int(chat_id),
                text="Chat-a lotuta geratu da. Orain zure lagunek taldeak bidali ahal dizkizute."
            )
        else:
            telegram_service.send_message(
                chat_id=int(chat_id),
                text="Ezin izan da kontua lotu. Ziurtatu web-aplikazioan zure Telegram erabiltzailea gordeta dagoela, edo erabili: /start <zure_erabilIzena>"
            )

        return jsonify({'ok': True})

    app.register_blueprint(telegram_bp)

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
    intsigniak_bp = Blueprint('intsigniak', __name__, url_prefix='/api')
    intsignia_ctrl = IntsigniaController(db)

    @intsigniak_bp.route('/erabiltzaileak/<int:uid>/intsigniak', methods=['GET'])
    def por_user_intsignia(uid):
        return jsonify(intsignia_ctrl.get_by_user(uid))

    @intsigniak_bp.route('/erabiltzaileak/<int:uid>/intsigniak/<izena>', methods=['POST'])
    def award(uid, izena):
        intsignia_ctrl.award(uid, izena)
        return jsonify({'message': 'Intsignia eman da'})

    app.register_blueprint(intsigniak_bp)

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

    app.register_blueprint(espezieak_bp)

    # ============================================
    # POKEMONAK (Pokémon)
    # ============================================
    pokemonak_bp = Blueprint('pokemonak', __name__, url_prefix='/api')

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

    def _taldea_to_dict(taldea):
        return {
            'id': taldea.id,
            'izena': taldea.izena,
            'erabiltzaile_id': taldea.erabiltzaile_id,
            'pokemonak': taldeak_katalogo.get_pokemonak(taldea.id)
        }

    @taldeak_bp.route('/taldeak/erabiltzailea/<int:uid>', methods=['GET'])
    def por_user_taldea(uid):
        taldeak = taldeak_katalogo.bilatu_by_erabiltzaile(uid)
        return jsonify([_taldea_to_dict(t) for t in taldeak])

    @taldeak_bp.route('/taldeak/<int:tid>/pokemon', methods=['GET'])
    def pokemon_de_taldea(tid):
        return jsonify(taldeak_katalogo.get_pokemonak(tid))

    @taldeak_bp.route('/taldeak', methods=['POST'])
    def crear_taldea():
        data = request.get_json()
        try:
            taldea = taldeak_katalogo.sortu(data['izena'], data['erabiltzaile_id'])
            return jsonify(_taldea_to_dict(taldea)), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    @taldeak_bp.route('/taldeak/<int:tid>/pokemon', methods=['POST'])
    def add_pokemon_taldea(tid):
        data = request.get_json()
        try:
            taldeak_katalogo.gehitu_pokemon(tid, data['pokemon_id'])
            taldea = taldeak_katalogo.bilatu_by_id(tid)
            if not taldea:
                return jsonify({'error': 'Taldea ez da existitzen'}), 404
            return jsonify(_taldea_to_dict(taldea))
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @taldeak_bp.route('/taldeak/<int:tid>/pokemon/<int:pid>', methods=['DELETE'])
    def remove_pokemon_taldea(tid, pid):
        try:
            taldeak_katalogo.kendu_pokemon(tid, pid)
            return jsonify({'message': 'Pokemon taldetik kendua'})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @taldeak_bp.route('/taldeak/<int:tid>', methods=['DELETE'])
    def borrar_taldea(tid):
        try:
            taldeak_katalogo.ezabatu(tid)
            return jsonify({'message': 'Taldea ezabauta'})
        except Exception as e:
            return jsonify({'error': str(e)}), 4000
    
    
    @taldeak_bp.route('/taldeak/<int:tid>/partekatu/<int:user_id>/<int:lagun_id>', methods=['POST'])
    def partekatu_taldea(tid, user_id, lagun_id):
        user = users_katalogo.bilatu_by_id(user_id)
        lagun = users_katalogo.bilatu_by_id(lagun_id)
        taldea = taldeak_katalogo.bilatu_by_id(tid)
        if not user or not lagun or not taldea:
            return jsonify({'error': 'Erabiltzaile edo taldea ez da existitzen'}), 404

        if not lagun.chat_id:
            return jsonify({'error': 'Lagunak ez du /start egin Telegram bot-ean (chat_id falta da)'}), 400

        # Build payload (json) from DB
        pokemonak = taldeak_katalogo.get_pokemonak(tid)

        partekatu = telegram_service.partekatu_taldea(
            lagun.chat_id,
            user.erabiltzaileIzena,
            taldea.izena,
            pokemonak
        )
        if not partekatu:
            return jsonify({'error': 'Ezin izan da taldea Telegram bidez bidali'}), 502

        return jsonify({'message': 'Taldea partekatu da'}), 200

    app.register_blueprint(taldeak_bp)


