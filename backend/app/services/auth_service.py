from fastapi import HTTPException
import hashlib
from app.models import UsuarisClase
from app.config import settings
from jose import jwt
from datetime import datetime, timedelta

# Función para verificar la contraseña
def verificar_password(password, hash_almacenado):
    try:
        esquema_y_parametros, salt, hash_real = hash_almacenado.split('$')

        if not esquema_y_parametros.startswith('scrypt:'):
            raise ValueError("Esquema de hash no soportado")

        _, n, r, p = esquema_y_parametros.split(':')
        n, r, p = int(n), int(r), int(p)

        salt_bytes = salt.encode('utf-8')
        hash_real_bytes = bytes.fromhex(hash_real)

        max_memory = 128 * 1024 * 1024
        adjusted_n = n if (n * r * 128) <= max_memory else 16384

        password_hash = hashlib.scrypt(
            password.encode('utf-8'),
            salt=salt_bytes,
            n=adjusted_n,
            r=r,
            p=p,
            maxmem=max_memory,
            dklen=len(hash_real_bytes)
        )

        return password_hash == hash_real_bytes
    except Exception as e:
        print(f"[ERROR] Error al verificar el password: {e}")
        return False

# Servicio de autenticación
def autenticar_usuario(username, password_introducido):
    try:
        # Usar el modelo para buscar al usuario
        db = UsuarisClase()
        user = db.buscaUsuario(username)

        print(f"Usuario encontrado: {user}")  # Debug

        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        # Verificar la contraseña
        is_password_correct = verificar_password(password_introducido, user["password"])
        print(f"¿Contraseña correcta?: {is_password_correct}")  # Debug

        if not is_password_correct:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        print(f"Usuario autenticado con éxito: {user['id']}, {user['username']}")  # Debug

        return {
            "id": user["id"],
            "username": user["username"]
        }  # Devolvemos el id y username en vez de solo un mensaje

    except Exception as e:
        print(f"[ERROR] Error al autenticar usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
