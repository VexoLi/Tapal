from fastapi import FastAPI
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from fastapi import Depends

app = FastAPI()


# Registrar el router de autenticación
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def root():
    return {"message": "API de WhatsApp funcionando correctamente"}

# Autenticación
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Usuarios simulados (puedes reemplazar esto por consultas a la base de datos)
fake_users_db = {
    "user1": {"username": "user1", "hashed_password": pwd_context.hash("123456")},
    "user2": {"username": "user2", "hashed_password": pwd_context.hash("123456")},
    "user3": {"username": "user3", "hashed_password": pwd_context.hash("123456")},
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    user = fake_users_db.get(username)
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user["username"], "token_type": "bearer"}

@app.get("/llistaamics")
async def llistaamics():
    # Datos de ejemplo (puedes conectar esto a tu base de datos más adelante)
    fake_users = [
        {"fullname": "Joan Vicnes", "username": "jvicnes"},
        {"fullname": "Maria Lopez", "username": "mlopez"},
        {"fullname": "Carlos Sanchez", "username": "csanchez"},
    ]
    return fake_users
