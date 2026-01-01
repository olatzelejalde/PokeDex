from flask import Blueprint, jsonify, request, session
from app.controller.model.erabiltzaile_controller import ErabiltzaileController

def erabiltzaile_blueprint(db):
    bp = Blueprint('erabiltzaileak', __name__, url_prefix='/api')
    ctrl = ErabiltzaileController(db)

    @bp.route('/erabiltzaileak', methods=['GET'])
    def zerrendatu():
        users = ctrl.get_all()
        return jsonify([ctrl.to_dict(u) for u in users])

    @bp.route('/erabiltzaileak', methods=['POST'])
    def sortu():
        data = request.get_json()
        pasahitza2 = data.get('pasahitza2', data['pasahitza'])
        try:
            ctrl.create(
                data['izena'], data['abizena'], data['erabiltzaileIzena'], data['pasahitza'], pasahitza2, data.get('telegramKontua')
            )
            u = ctrl.get_by_erabilIzena(data['erabiltzaileIzena'])
            return jsonify(ctrl.to_dict(u)), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    @bp.route('/erabiltzaileak/saioa', methods=['POST'])
    def saioa():
        data = request.get_json()
        u = ctrl.login(data['erabiltzaileIzena'], data['pasahitza'])
        if u:
            session['uid'] = u.id
            return jsonify(ctrl.to_dict(u))
        return jsonify({'error': 'Kredentzial okerrak'}), 401

    @bp.route('/erabiltzaileak/<int:uid>', methods=['GET'])
    def bat(uid):
        u = ctrl.get_by_id(uid)
        return jsonify(ctrl.to_dict(u) if u else {})

    @bp.route('/erabiltzaileak/<int:uid>', methods=['PUT'])
    def eguneratu(uid):
        data = request.get_json()
        try:
            ctrl.update(uid, data)
            user = ctrl.get_by_id(uid)
            return jsonify(ctrl.to_dict(user))
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    return bp