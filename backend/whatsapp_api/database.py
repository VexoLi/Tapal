import pymysql.cursors
from sqlalchemy.orm import Session
from app.models import User
from passlib.context import CryptContext

class UsuarisClase:
    def conecta(self):
        # Conexión a la base de datos `usuarisclase`
        self.db = pymysql.connect( host='localhost',
                                     user='root',
                                     db='usuarisclase',
                                     charset='utf8mb4',
                                     autocommit=True,
                                     cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.db.cursor()

    def desconecta(self):
        # Cerrar la conexión a la base de datos
        self.db.close()

    def cargaUsuarios(self):
        # Recupera todos los usuarios de la tabla `usuarisclase`
        sql = "SELECT * FROM usuarisclase"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def buscaUsuario(self, username):
        # Busca un usuario específico por nombre de usuario
        sql = "SELECT * FROM usuarisclase WHERE username = %s"
        self.cursor.execute(sql, (username,))
        return self.cursor.fetchone()

    def insertaUsuario(self, username, password):
        # Inserta un nuevo usuario en la tabla
        sql = "INSERT INTO usuarisclase (username, password) VALUES (%s, %s)"
        try:
            self.cursor.execute(sql, (username, password))
            self.db.commit()
            return "Usuario insertado correctamente"
        except pymysql.MySQLError as e:
            self.db.rollback()
            return f"Error al insertar usuario: {e}"

    def actualizaPassword(self, username, nuevo_password):
        # Actualiza la contraseña de un usuario
        sql = "UPDATE usuarisclase SET password = %s WHERE username = %s"
        try:
            self.cursor.execute(sql, (nuevo_password, username))
            self.db.commit()
            return "Contraseña actualizada correctamente"
        except pymysql.MySQLError as e:
            self.db.rollback()
            return f"Error al actualizar contraseña: {e}"

    def eliminaUsuario(self, username):
        # Elimina un usuario por nombre de usuario
        sql = "DELETE FROM usuarisclase WHERE username = %s"
        try:
            self.cursor.execute(sql, (username,))
            self.db.commit()
            return "Usuario eliminado correctamente"
        except pymysql.MySQLError as e:
            self.db.rollback()
            return f"Error al eliminar usuario: {e}"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_users(db: Session):
    users = [
        {"username": "user1", "hashed_password": pwd_context.hash("123456")},
        {"username": "user2", "hashed_password": pwd_context.hash("123456")},
        {"username": "user3", "hashed_password": pwd_context.hash("123456")},
    ]
    for user in users:
        db.add(User(**user))
    db.commit()