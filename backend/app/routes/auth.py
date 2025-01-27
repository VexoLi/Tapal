from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.auth_service import autenticar_usuario

router = APIRouter()

# Esquema para los datos de entrada
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(login_request: LoginRequest):
    try:
        # Extraer datos del cuerpo de la solicitud
        username = login_request.username
        password = login_request.password

        # Llamada al servicio de autenticación
        mensaje = autenticar_usuario(username, password)
        return {"message": mensaje}
    except HTTPException as e:
        raise e
