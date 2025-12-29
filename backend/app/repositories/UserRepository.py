from app.database.connection import db
from app.models.Erabiltzailea import Erabiltzailea, Taldea
from werkzeug.security import generate_password_hash, check_password_hash

class UserRepository:

    @staticmethod
    def get_user_by_username(username: str, include_password: bool = False):
        if include_password:
            query = """
            SELECT izena, abizena, erabiltzaileIzena, telegramKontua, pasahitza, rola
            FROM erabiltzailea
            WHERE erabiltzaileIzena = ?
            """
        else:
            query = """
            SELECT izena, abizena, erabiltzaileIzena, telegramKontua, rola
            FROM erabiltzailea
            WHERE erabiltzaileIzena = ?
            """
        result = db.execute_query(query, (username,), fetch_one=True)
        
        if not result:
            return None

        return Erabiltzailea(
            izena=result['izena'],
            abizena=result['abizena'],
            erabiltzaileIzena=result['erabiltzaileIzena'],
            telegramKontua=result['telegramKontua'],
            pasahitza=result.get('pasahitza', ''),
            rola=result['rola']
        )
    
    @staticmethod
    def create(user_data: dict):
        try:
            db.execute_update(
                """
                INSERT INTO erabiltzailea (izena, abizena, erabiltzaileIzena, telegramKontua, pasahitza, rola)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_data['izena'],
                    user_data['abizena'],
                    user_data['erabiltzaileIzena'],
                    user_data.get('telegramKontua'),
                    generate_password_hash(user_data['pasahitza']),
                    user_data['rola']
                )
            )
        except Exception as e:
            print(f"Errorea erabiltzailea sortzean: {e}")
            return None
        
    @staticmethod
    def verify_password(username: str, password: str) -> bool:
        user = UserRepository.get_user_by_username(username, include_password=True)
        if not user:
            return False
        return check_password_hash(user.pasahitza, password)
    
    @staticmethod
    def get_user_teams(username: str):
        query = """
        SELECT id, izena, erabiltzaileIzena
        FROM taldea
        WHERE erabiltzaileIzena = ?
        """
        results = db.execute_query(query, (username,))

        taldeak = []
        for r in results:
            pokemon_query = """
            SELECT pokemonId
            FROM ditu
            WHERE taldeaId = ?
            ORDER BY posizioa
            """
            pokemon_results = db.execute_query(pokemon_query, (r['id'],))

            taldea = Taldea(
                id=r['id'],
                izena=r['izena'],
                erabiltzaileIzena=r['erabiltzaileIzena'],
            )
            taldea.pokemonak = [pr['pokemonId'] for pr in pokemon_results]
            taldeak.append(taldea)
        return taldeak