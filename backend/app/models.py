import pymysql.cursors

class UsuarisClase:
    def __init__(self):
        self.db = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            db="whatsapp2425",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.cursor = self.db.cursor()

    def buscaUsuario(self, username):
        try:
            sql = "SELECT * FROM usuarisclase WHERE username = %s"
            self.cursor.execute(sql, (username,))
            return self.cursor.fetchone()
        except pymysql.MySQLError as e:
            print(f"[ERROR] Error al buscar usuario: {e}")
            return None

    def __del__(self):
        # Cerrar la conexión cuando el objeto se elimina
        if hasattr(self, 'db'):
            self.db.close()
