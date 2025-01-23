from fastapi import FastAPI
from backend.app.routes import users

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API de mensajería activa"}

app.include_router(users.router)