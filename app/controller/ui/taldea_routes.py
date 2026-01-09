from flask import Blueprint, jsonify, request, session
from app.controller.model.taldea_controller import TaldeaController
from app.controller.model.pokemon_controller import PokemonController

def taldea_blueprint(db):
    bp = Blueprint('taldeak', __name__, url_prefix='/api')
    pokemon_ctrl = PokemonController(db)
    ctrl = TaldeaController(db, pokemon_ctrl)

    @bp.route('/taldeak/erabiltzailea/<int:uid>', methods=['GET'])
    def por_user(uid):
        return jsonify(ctrl.get_by_user(uid))

    @bp.route('/taldeak/<int:tid>/pokemon', methods=['GET'])
    def pokemon_de_taldea(tid):
        return jsonify(pokemon_ctrl.get_pokemon_by_group(tid))


    @bp.route('/taldeak', methods=['POST'])
    def crear():
        data = request.get_json()
        tid = ctrl.create(data['izena'], data['erabiltzaile_id'])
        return jsonify({'id': tid}), 201

    @bp.route('/taldeak/<int:tid>/pokemon', methods=['POST'])
    def add_pokemon(tid):
        data = request.get_json()
        ctrl.add_pokemon(tid, data['pokemon_id'])
        return jsonify({'message': 'Pokemon taldera gehituta'})

    @bp.route('/taldeak/<int:tid>/pokemon/<int:pid>', methods=['DELETE'])
    def remove_pokemon(tid, pid):
        ctrl.remove_pokemon(tid, pid)
        return jsonify({'message': 'Pokemon taldetik kendua'})

    @bp.route('/taldeak/<int:tid>', methods=['DELETE'])
    def borrar(tid):
        ctrl.delete(tid)
        return jsonify({'message': 'Taldea ezabauta'})

    return bp