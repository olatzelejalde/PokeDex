from flask import Blueprint, jsonify
from app.controller.model.mota_controller import MotaController

def mota_blueprint(db):
    bp = Blueprint('motak', __name__, url_prefix='/api')
    ctrl = MotaController(db)

    @bp.route('/motak', methods=['GET'])
    def listar():
        return jsonify(ctrl.get_all())

    return bp