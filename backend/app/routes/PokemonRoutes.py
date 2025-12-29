from flask import Blueprint, jsonify, request

def pokemon_blueprint(db):
    bp = Blueprint('pokemon', __name__, url_prefix='/api')
    from app.controllers.PokemonController import PokemonController
    controller = PokemonController(db)

    @bp.route('/pokemon', methods=['GET'])
    def get_pokemon():
        result = 