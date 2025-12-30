from flask import Blueprint, jsonify, request
from app.controller.model.espezie_controller import EspezieController

def especie_blueprint(db):
    bp = Blueprint('espezieak', __name__, url_prefix='/api')
    ctrl = EspezieController(db)
    @bp.route('/espezieak', methods=['GET'])
    def listar():
        return jsonify(ctrl.get_all())

    @bp.route('/espezieak/<izena>', methods=['GET'])
    def uno(izena):
        return jsonify(ctrl.get_by_name(izena) or {})

    return bp