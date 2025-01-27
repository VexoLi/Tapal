import hashlib
import pymysql

def verificar_password(password, hash_almacenado):
    try:
        # Separar el formato scrypt:<params>$<salt>$<hash>
        esquema_y_parametros, salt, hash_real = hash_almacenado.split('$')

        # Verificar que el esquema es scrypt
        if not esquema_y_parametros.startswith('scrypt:'):
            raise ValueError("Esquema de hash no soportado")

        # Extraer parámetros
        _, n, r, p = esquema_y_parametros.split(':')
        n, r, p = int(n), int(r), int(p)

        print(f"Salt: {salt}")
        print(f"Hash esperado: {hash_real}")

        # Convertir hash real desde hexadecimal
        hash_real_bytes = bytes.fromhex(hash_real)

        # Ajustar parámetros para controlar el uso de memoria
        max_memory = 128 * 1024 * 1024  # 128 MB
        adjusted_n = n if (n * r * 128) <= max_memory else 16384

        # Derivar el hash del password introducido usando scrypt
        password_hash = hashlib.scrypt(
            password.encode('utf-8'),
            salt=salt.encode('utf-8'),
            n=adjusted_n,
            r=r,
            p=p,
            maxmem=max_memory,
            dklen=len(hash_real_bytes)
        )

        # Comparar el hash derivado con el almacenado
        return password_hash == hash_real_bytes

    except Exception as e:
        print(f"Error al verificar el password: {e}")
        return False


def autenticar_usuario(username, password_introducido):
    # Configuración de la conexión a la base de datos
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "db": "whatsapp2425",
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor
    }

    try:
        # Conectar a la base de datos
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # Buscar al usuario en la base de datos
            sql = "SELECT username, password FROM usuarisclase WHERE username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()

            # Verificar si el usuario existe
            if not user:
                print("Usuario no encontrado.")
                return False

            # Extraer el hash almacenado
            hash_almacenado = user['password']
            print(f"Hash almacenado: {hash_almacenado}")

            # Verificar el password
            if verificar_password(password_introducido, hash_almacenado):
                print("Autenticación exitosa.")
                return True
            else:
                print("Contraseña incorrecta.")
                return False

    except Exception as e:
        print(f"Error al autenticar usuario: {e}")
        return False

    finally:
        # Cerrar la conexión
        if 'connection' in locals():
            connection.close()


# Prueba de autenticación
autenticar_usuario('yukhangwong', 'X8978849')
