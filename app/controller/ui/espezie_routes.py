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

    @bp.route('/espezieak/<string:izena>/info', methods=['GET'])
    def get_pokemon_info(izena):
        data = ctrl.get_type_effectiveness(izena)
        if data:
            return jsonify(data)
        else:
            return jsonify({"error": "Ez da aurkitu"}), 404

    @bp.route('/espezieak/<string:izena>/ebo', methods=['GET'])
    def get_ebo(izena):
        return jsonify(ctrl.get_ebo_info(izena))

    @bp.route('/espezieak/<string:izena>/scan', methods=['GET'])
    def get_scan(izena):
        return jsonify(ctrl.get_scan_info(izena))


    return bp