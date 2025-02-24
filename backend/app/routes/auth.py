from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.services.auth_service import autenticar_usuario
from app.config import settings

router = APIRouter()

# Esquema para los datos de entrada
class LoginRequest(BaseModel):
    username: str
    password: str

# Función para crear un token JWT
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/login")
async def login(login_request: LoginRequest):
    try:
        username = login_request.username
        password = login_request.password

        # Autenticar usuario
        user = autenticar_usuario(username, password)  # Ahora devuelve un diccionario con id y username

        if not user:
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

        user_id = user["id"]  # Extraer el user_id correctamente

        # Crear token JWT con el user_id
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "user_id": user_id},
            expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer", "user_id": user_id}

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"[ERROR] Error en el login: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
