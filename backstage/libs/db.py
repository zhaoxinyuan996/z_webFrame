import pymysql

from backstage.settings import DB_CONFIG


class connection():
    conn = pymysql.connect('127.0.0.1', DB_CONFIG.username, DB_CONFIG.password, 'web')
    @classmethod
    def cursor(cls):
        cursor = cls.conn
        return cursor