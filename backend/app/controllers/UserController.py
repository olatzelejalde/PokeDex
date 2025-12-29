from flask import jsonify, request
from app.repositories.UserRepository import UserRepository
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

class UserController:

    def __init__(self, db):
        self.repository = UserRepository()

    def register(self, user_data: dict):
        try:
            if self.repository.get_user_by_username(user_data['erabiltzaileIzena']):
                return {'success': False, 'error': 'Erabiltzailea dagoeneko existitzen da.'}

            user = self.repository.create(user_data)
            return {'success': True, 'user': user.to_dict()}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
    def login(self, login_data: dict) -> dict:
        try:
            username = login_data['erabiltzaileIzena']
            password = login_data['pasahitza']

            if not self.repository.verify_password(username, password):
                return {'success': False, 'error': 'Erabiltzaile izena edo pasahitza okerra da.'}
            
            user = self.repository.get_user_by_username(username)
            token = jwt.encode({'erabiltzaileIzena': user.erabiltzaileIzena}, 'andreacf_jwt', algorithm='HS256')

            return {
                'success': True,
                'data':{'user': user.to_dict(), 'token': token}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
    def get_user_teams(self, username: str) -> dict:
        try:
            teams = self.repository.get_user_teams(username)
            return {'success': True, 'teams': [team.to_dict() for team in teams]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        