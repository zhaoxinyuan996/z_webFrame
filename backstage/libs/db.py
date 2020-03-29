import pymysql

from backstage.settings import DB_CONFIG


class Connection():
    def __enter__(self):
        self.conn = pymysql.connect('127.0.0.1', DB_CONFIG.username, DB_CONFIG.password, 'web')
        self.cursor = self.conn.cursor()
        return self.cursor
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

# connection = Connection()


if __name__ == '__main__':
    # print(connection.__enter__)
    pass