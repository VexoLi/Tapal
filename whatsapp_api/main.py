from fastapi import FastAPI
from app.routes import groups, users

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API de mensajería activa"}


app.include_router(groups.router)
app.include_router(users.router)