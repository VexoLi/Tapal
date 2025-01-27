import hashlib

def verificar_password(password, hash_almacenado):
    try:
        esquema_y_parametros, salt, hash_real = hash_almacenado.split('$')

        if not esquema_y_parametros.startswith('scrypt:'):
            raise ValueError("Esquema de hash no soportado")

        _, n, r, p = esquema_y_parametros.split(':')
        n, r, p = int(n), int(r), int(p)

        salt_bytes = salt.encode('utf-8')
        hash_real_bytes = bytes.fromhex(hash_real)

        password_hash = hashlib.scrypt(
            password.encode('utf-8'),
            salt=salt_bytes,
            n=n,
            r=r,
            p=p,
            dklen=len(hash_real_bytes)
        )
        return password_hash == hash_real_bytes
    except Exception as e:
        print(f"Error al verificar el password: {e}")
        return False
