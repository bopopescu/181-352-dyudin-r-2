from flask import g
import mysql.connector

class MySQL:
    def __init__(self, app):
        self.app = app
        self.app.teardown_appcontext(self.close_db)

    def connection(self):
        if 'db' not in g:
            g.db = self.connect()
        return g.db

    def connect(self):
        return mysql.connector.connect(**self.config())

    def config(self):
        return {
            'user': self.app.config['MYSQL_USER'],
            'password': self.app.config['MYSQL_PASSWORD'],
            'host': self.app.config['MYSQL_HOST'],
            'database': self.app.config['MYSQL_DATABASE']
        }

    def close_db(self, e = None):
        db = g.pop('db',None)
        if db is not None:
            db.close()