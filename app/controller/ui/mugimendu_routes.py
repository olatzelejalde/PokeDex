from flask import Blueprint, jsonify
from app.controller.model.mugimendu_controller import MugimenduController

def mugimendu_blueprint(db):
    bp = Blueprint('mugimenduak', __name__, url_prefix='/api')
    ctrl = MugimenduController(db)

    @bp.route('/especieak/<izena>/mugimenduak', methods=['GET'])
    def por_espezie(izena):
        return jsonify(ctrl.get_by_espezie(izena))

    return bp