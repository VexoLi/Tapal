from sqlalchemy import Column, Integer, String
from backend.whatsapp_api.database import Base

class UsuariClase(Base):
    __tablename__ = "usuarisclase"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
