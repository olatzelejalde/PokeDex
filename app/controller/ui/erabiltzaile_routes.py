from flask import Blueprint, jsonify, request, session
from app.controller.model.erabiltzaile_controller import ErabiltzaileController

def erabiltzaile_blueprint(db):
    bp = Blueprint('erabiltzaileak', __name__, url_prefix='/api')
    ctrl = ErabiltzaileController(db)

    @bp.route('/erabiltzaileak', methods=['GET'])
    def listar():
        return jsonify(ctrl.get_all())

    @bp.route('/erabiltzaileak', methods=['POST'])
    def crear():
        data = request.get_json()
        try:
            ctrl.create(data['izena'], data['abizena'], data['erabilIzena'], data['pasahitza'], data.get('telegramKontua'))
            return jsonify({'message': 'Erabiltzailea sortua'}), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    @bp.route('/erabiltzaileak/saioa', methods=['POST'])
    def saioa():
        data = request.get_json()
        u = ctrl.login(data['erabilIzena'], data['pasahitza'])
        if u:
            session['uid'] = u['id']
            return jsonify(u)
        return jsonify({'error': 'Kredentzial okerrak'}), 401

    @bp.route('/erabiltzaileak/<int:uid>', methods=['GET'])
    def uno(uid):
        return jsonify(ctrl.get_by_id(uid) or {})

    return bp