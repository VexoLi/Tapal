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
        """
        Busca un usuario por su username en la base de datos.
        """
        try:
            sql = "SELECT * FROM usuarisclase WHERE username = %s"
            self.cursor.execute(sql, (username,))
            return self.cursor.fetchone()
        except pymysql.MySQLError as e:
            print(f"[ERROR] Error al buscar usuario: {e}")
            return None

    def obtener_todos_los_usuarios(self):
        """
        Devuelve todos los usuarios de la tabla usuarisclase.
        """
        try:
            sql = "SELECT id, username FROM usuarisclase"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"[ERROR] Error al obtener usuarios: {e}")
            return None
        
    def agregar_usuario_grupo(self, group_id, nuevo_miembro_id):
        """
        Agrega un usuario a un grupo.
        """
        sql = "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)"
        self.cursor.execute(sql, (group_id, nuevo_miembro_id))
        self.db.commit()
        return True

    def eliminar_miembro(self, group_id, user_id):
        """
        Elimina un usuario de un grupo.
        """
        sql = "DELETE FROM group_members WHERE group_id = %s AND user_id = %s"
        self.cursor.execute(sql, (group_id, user_id))
        self.db.commit()
        return True
        
    
    def obtener_grupos_por_usuario(self, user_id):
        """
        Obtiene los grupos en los que un usuario es miembro.
        """
        try:
            sql = """
                SELECT g.id, g.name, 
                    CASE WHEN gm.is_admin THEN true ELSE false END AS is_admin
                FROM groups g
                JOIN group_members gm ON g.id = gm.group_id
                WHERE gm.user_id = %s
            """
            self.cursor.execute(sql, (user_id,))
            return self.cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"[ERROR] Error al obtener grupos: {e}")
            return None

    def obtener_id_disponible(self):
        """
        Busca el ID más bajo disponible en la tabla de grupos.
        Si no hay huecos, devuelve el próximo ID autoincremental.
        """
        sql = """
            SELECT MIN(t1.id + 1) AS next_id
            FROM groups t1
            LEFT JOIN groups t2 ON t1.id + 1 = t2.id
            WHERE t2.id IS NULL
        """
        self.cursor.execute(sql)
        resultado = self.cursor.fetchone()
    
        if resultado and resultado["next_id"]:
            return resultado["next_id"]
    
    # Si no hay huecos, usar el siguiente ID autoincremental
        sql_max = "SELECT MAX(id) + 1 AS next_id FROM groups"
        self.cursor.execute(sql_max)
        resultado = self.cursor.fetchone()
        return resultado["next_id"] if resultado["next_id"] else 1  # Si no hay grupos, empezar desde 1

    def crear_grupo(self, nombre_grupo, admin_id):
        """
        Crea un nuevo grupo y lo asigna al usuario como administrador.
        """
        try:
            group_id = self.obtener_id_disponible()
        
            sql_grupo = "INSERT INTO groups (id, name, admin_id) VALUES (%s, %s, %s)"
            self.cursor.execute(sql_grupo, (group_id, nombre_grupo, admin_id))

            sql_miembro = "INSERT INTO group_members (group_id, user_id, is_admin) VALUES (%s, %s, %s)"
            self.cursor.execute(sql_miembro, (group_id, admin_id, True))
        
            self.db.commit()
            return {"message": "Grupo creado exitosamente", "group_id": group_id}
        except pymysql.MySQLError as e:
            print(f"[ERROR] Error al crear grupo: {e}")
            return None

    def transferir_admin(self, group_id, current_admin_id, new_admin_id):
        """
        Transfiere el rol de admin a otro usuario dentro del grupo.
        """
        try:
            sql_check = "SELECT * FROM group_members WHERE group_id = %s AND user_id = %s"
            self.cursor.execute(sql_check, (group_id, new_admin_id))
            nuevo_admin = self.cursor.fetchone()

            if not nuevo_admin:
                return {"error": "El usuario no está en el grupo"}

            sql_update_admin = "UPDATE groups SET admin_id = %s WHERE id = %s"
            self.cursor.execute(sql_update_admin, (new_admin_id, group_id))

            sql_update_member = "UPDATE group_members SET is_admin = FALSE WHERE group_id = %s AND user_id = %s"
            self.cursor.execute(sql_update_member, (group_id, current_admin_id))

            sql_promote_new_admin = "UPDATE group_members SET is_admin = TRUE WHERE group_id = %s AND user_id = %s"
            self.cursor.execute(sql_promote_new_admin, (group_id, new_admin_id))

            self.db.commit()
            return {"message": "Admin transferido exitosamente"}
        except pymysql.MySQLError as e:
            print(f"[ERROR] Error al transferir admin: {e}")
            return None

    def salir_del_grupo(self, group_id, user_id):
        """
        Permite a un usuario salir del grupo.
        Si el usuario es el admin, transfiere el rol al usuario con ID más bajo.
        Si es el último usuario, el grupo se elimina.
        """
        try:
            sql_verificar_admin = "SELECT admin_id FROM groups WHERE id = %s"
            self.cursor.execute(sql_verificar_admin, (group_id,))
            grupo = self.cursor.fetchone()

            if not grupo:
                return {"error": "El grupo no existe"}

            sql_eliminar_miembro = "DELETE FROM group_members WHERE group_id = %s AND user_id = %s"
            self.cursor.execute(sql_eliminar_miembro, (group_id, user_id))

            sql_contar_miembros = "SELECT user_id FROM group_members WHERE group_id = %s ORDER BY user_id ASC LIMIT 1"
            self.cursor.execute(sql_contar_miembros, (group_id,))
            nuevo_admin = self.cursor.fetchone()

            if nuevo_admin:
                # Si el usuario era admin, se asigna el nuevo admin
                if grupo["admin_id"] == user_id:
                    sql_actualizar_admin = "UPDATE groups SET admin_id = %s WHERE id = %s"
                    self.cursor.execute(sql_actualizar_admin, (nuevo_admin["user_id"], group_id))
            else:
                # Si no hay miembros, se borra el grupo
                sql_eliminar_grupo = "DELETE FROM groups WHERE id = %s"
                self.cursor.execute(sql_eliminar_grupo, (group_id,))

            self.db.commit()
            return {"message": "Usuario ha salido del grupo correctamente"}
        except pymysql.MySQLError as e:
            print(f"[ERROR] Error al salir del grupo: {e}")
            return None
        
    def eliminar_miembro(self, group_id, user_id):
        """
        Expulsa a un usuario del grupo.
        """
        try:
            sql = "DELETE FROM group_members WHERE group_id = %s AND user_id = %s"
            self.cursor.execute(sql, (group_id, user_id))
            self.db.commit()
            return True
        except pymysql.MySQLError as e:
            print(f"[ERROR] Error al eliminar usuario del grupo: {e}")
        return False

        
    def es_admin(self, user_id, group_id):
        """
        Verifica si el usuario es administrador de un grupo.
        """
        sql = "SELECT * FROM groups WHERE id = %s AND admin_id = %s"
        self.cursor.execute(sql, (group_id, user_id))
        return self.cursor.fetchone() is not None

    def es_miembro(self, user_id, group_id):
        """
        Verifica si un usuario es miembro de un grupo.
        """
        sql = "SELECT * FROM group_members WHERE group_id = %s AND user_id = %s"
        self.cursor.execute(sql, (group_id, user_id))
        return self.cursor.fetchone() is not None

    def obtener_miembros_grupo(self, group_id):
        """
        Obtiene todos los miembros de un grupo.
        """
        sql = """
            SELECT u.id, u.username, gm.is_admin
            FROM usuarisclase u
            JOIN group_members gm ON u.id = gm.user_id
            WHERE gm.group_id = %s
            """
        self.cursor.execute(sql, (group_id,))
        return self.cursor.fetchall()
    
    def guardar_mensaje(self, sender_id, receiver_id, content):
        """
        Guarda un mensaje enviado en la base de datos.
        """
        try:
            sql = "INSERT INTO messages (sender_id, receiver_id, content) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (sender_id, receiver_id, content))
            self.db.commit()
            return True
        except pymysql.MySQLError as e:
            print(f"[ERROR] Error al guardar mensaje: {e}")
            return False


    def obtener_mensajes(self, user_id, friend_id, page):
        """
        Obtiene los mensajes entre dos usuarios con paginación.
        """
        offset = (page - 1) * 10  # Cada página muestra 10 mensajes
        sql = """
            SELECT sender_id, receiver_id, content, timestamp
            FROM messages
            WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
            ORDER BY timestamp DESC
            LIMIT 10 OFFSET %s
        """
        self.cursor.execute(sql, (user_id, friend_id, friend_id, user_id, offset))
        return self.cursor.fetchall()

    def actualizar_estado_mensajes(self, user_id, friend_id, nuevo_estado):
        """
        Actualiza el estado de los mensajes enviados al usuario.
        """
        sql = """
            UPDATE message_status 
            SET status = %s 
            WHERE user_id = %s 
            AND message_id IN (
                SELECT id FROM messages 
                WHERE sender_id = %s AND receiver_id = %s
            )
        """
        self.cursor.execute(sql, (nuevo_estado, user_id, friend_id, user_id))
        self.db.commit()
        return True

    def obtener_mensajes_grupo(self, group_id, page):
        """
        Obtiene los mensajes de un grupo con paginación.
        """
        offset = (page - 1) * 10  # Cada página muestra 10 mensajes
        sql = """
            SELECT m.sender_id, u.username AS sender_username, m.content, m.timestamp
            FROM messages m
            JOIN usuarisclase u ON m.sender_id = u.id
            WHERE m.group_id = %s
            ORDER BY m.timestamp DESC
            LIMIT 10 OFFSET %s
        """
        self.cursor.execute(sql, (group_id, offset))
        return self.cursor.fetchall()

    def enviar_mensaje_grupo(self, user_id, group_id, content):
        """
        Guarda un nuevo mensaje en un grupo.
        """
        sql = """
            INSERT INTO messages (sender_id, group_id, content)
            VALUES (%s, %s, %s)
        """
        self.cursor.execute(sql, (user_id, group_id, content))
        self.db.commit()
        return {"message": "Mensaje enviado correctamente"}

    def enviar_mensaje_grupo(self, user_id, group_id, content):
        """
        Envía un mensaje a un grupo y asigna estado 'recibido' a los miembros.
        """
        try:
            # Insertar el mensaje en la tabla messages
            sql = """
                INSERT INTO messages (sender_id, group_id, content)
                VALUES (%s, %s, %s)
            """
            self.cursor.execute(sql, (user_id, group_id, content))
            message_id = self.cursor.lastrowid

            # Obtener todos los miembros del grupo excepto el remitente
            sql_miembros = "SELECT user_id FROM group_members WHERE group_id = %s AND user_id != %s"
            self.cursor.execute(sql_miembros, (group_id, user_id))
            miembros = self.cursor.fetchall()

            # Asignar estado 'recibido' a cada usuario
            for miembro in miembros:
                sql_estado = """
                    INSERT INTO message_status (message_id, user_id, status, group_id) 
                    VALUES (%s, %s, 'received', %s)
                """
                self.cursor.execute(sql_estado, (message_id, miembro["user_id"], group_id))

            self.db.commit()
            return {"message": "Mensaje enviado correctamente al grupo"}
        except pymysql.MySQLError as e:
            print(f"[ERROR] Error al enviar mensaje al grupo: {e}")
            return None
        
    def marcar_mensajes_leidos_grupo(self, user_id, group_id):
        """
        Marca como 'leído' todos los mensajes no leídos en un grupo.
        """
        try:
            sql = """
                UPDATE message_status 
                SET status = 'read' 
                WHERE user_id = %s AND group_id = %s AND status = 'received'
            """
            self.cursor.execute(sql, (user_id, group_id))
            self.db.commit()
            return {"message": "Mensajes marcados como leídos"}
        except pymysql.MySQLError as e:
            print(f"[ERROR] Error al marcar mensajes como leídos en grupo: {e}")
            return None
        
    def obtener_mensajes_no_llegits(self, user_id):
        """
        Obtiene la cantidad de mensajes no leídos en chats individuales y grupales.
        """
        try:
            # Mensajes no leídos en chats individuales
            sql_individual = """
                SELECT sender_id AS chat_id, COUNT(*) AS unread_count
                FROM message_status ms
                JOIN messages m ON ms.message_id = m.id
                WHERE ms.user_id = %s AND ms.status IN ('sent', 'received')
                GROUP BY sender_id
            """
            self.cursor.execute(sql_individual, (user_id,))
            chats_no_llegits = self.cursor.fetchall()

            # Mensajes no leídos en grupos
            sql_grupal = """
                SELECT m.group_id AS group_id, COUNT(*) AS unread_count
                FROM message_status ms
                JOIN messages m ON ms.message_id = m.id
                WHERE ms.user_id = %s AND ms.status IN ('sent', 'received') AND m.group_id IS NOT NULL
                GROUP BY m.group_id
            """
            self.cursor.execute(sql_grupal, (user_id,))
            grups_no_llegits = self.cursor.fetchall()

            return {
                "chats_no_llegits": chats_no_llegits,
                "grups_no_llegits": grups_no_llegits
            }
        except pymysql.MySQLError as e:
            print(f"[ERROR] Error al obtener mensajes no leídos: {e}")
            return None
        
    def asignar_admin(self, user_id, group_id):
        """
        Asigna el rol de administrador a un usuario dentro de un grupo.
        """
        try:
            sql = "UPDATE group_members SET is_admin = TRUE WHERE group_id = %s AND user_id = %s"
            self.cursor.execute(sql, (group_id, user_id))
            self.db.commit()
            return True
        except pymysql.MySQLError as e:
            print(f"[ERROR] Error al asignar administrador: {e}")
            return False

        
        
    def __del__(self):
        """
        Cierra la conexión cuando se destruye el objeto.
        """
        if hasattr(self, 'db'):
            self.db.close()

