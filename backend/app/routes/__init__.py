from fastapi import APIRouter
from app.routes.auth import router as auth_router
# Puedes importar otros routers aquí, como groups o users

router = APIRouter()

# Registrar los routers
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
