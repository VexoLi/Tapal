from fastapi import FastAPI
from app.routes.auth import router as auth_router

app = FastAPI()

# Registrar el router de autenticación
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def root():
    return {"message": "API funcionando correctamente"}
