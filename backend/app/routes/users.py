from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.whatsapp_api.database import get_db
from app.models import UsuariClase

router = APIRouter()

@router.get("/llistaamics", summary="Listar todos los usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(UsuariClase).all()
    return {"usuarios": [{"id": u.id, "username": u.username, "password": u.password} for u in usuarios]}
