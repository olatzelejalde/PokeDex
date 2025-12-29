import sqlite3
from config import Config

class Connection:
    def __init__(self):
        self.connection = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.__initialized = True

    def select(self, query, params=None):
        cursor = self.connection.cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
    def insert(self, query, params=None):
        cursor = self.connection.cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        self.connection.commit()
        cursor.close()

    def update(self, query, params=None):
        cursor = self.connection.cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        self.connection.commit()
        cursor.close()

    def delete(self, query, params=None):
        cursor = self.connection.cursor()
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        self.connection.commit()
        cursor.close()