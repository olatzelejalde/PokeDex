class MotaController:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return [dict(row) for row in self.db.select("SELECT * FROM mota")]