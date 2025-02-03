from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.config import settings

# Contexto de encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """
    Genera un token JWT con datos adicionales.
    """
    to_encode = data.copy()
    to_encode.update({"exp": settings.ACCESS_TOKEN_EXPIRE_DELTA})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    """
    Verifica el token JWT y extrae los datos del usuario.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"username": username, "user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
