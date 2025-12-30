from flask import Blueprint, jsonify, request
from app.controller.model.intsignia_controller import IntsigniaController

def intsignia_blueprint(db):
    bp = Blueprint('intsigniak', __name__, url_prefix='/api')
    ctrl = IntsigniaController(db)

    @bp.route('/erabiltzaileak/<int:uid>/intsigniak', methods=['GET'])
    def por_user(uid):
        return jsonify(ctrl.get_by_user(uid))

    @bp.route('/erabiltzaileak/<int:uid>/intsigniak/<izena>', methods=['POST'])
    def award(uid, izena):
        ctrl.award(uid, izena)
        return jsonify({'message': 'Intsignia eman da'})

    return bp