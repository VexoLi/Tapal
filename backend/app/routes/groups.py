from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Mock data per a grups
grups = [
    {"id": 1, "nom": "Grup 1", "administrador_id": 1, "usuaris": [1, 2]},
    {"id": 2, "nom": "Grup 2", "administrador_id": 2, "usuaris": [2, 3]},
]

# Models per a les dades
class GrupNou(BaseModel):
    nom: str
    administrador_id: int

class ModificarGrup(BaseModel):
    nom: Optional[str]
    usuaris: Optional[List[int]]

@router.get("/grups")
def get_grups(usuari_id: int):
    """
    Retorna els grups on participa l'usuari.
    """
    grups_usuari = [grup for grup in grups if usuari_id in grup["usuaris"]]
    if not grups_usuari:
        raise HTTPException(status_code=404, detail="L'usuari no forma part de cap grup.")
    return {"grups": grups_usuari}

@router.post("/grups")
def crear_grup(grup: GrupNou):
    """
    Crea un nou grup i assigna l'usuari com a administrador.
    """
    nou_grup = {
        "id": len(grups) + 1,
        "nom": grup.nom,
        "administrador_id": grup.administrador_id,
        "usuaris": [grup.administrador_id]
    }
    grups.append(nou_grup)
    return {"missatge": "Grup creat correctament", "grup": nou_grup}

@router.put("/grups/{grup_id}")
def modificar_grup(grup_id: int, modificacions: ModificarGrup, usuari_id: int):
    """
    Modifica el nom o els usuaris d'un grup. Només l'administrador pot modificar un grup.
    """
    for grup in grups:
        if grup["id"] == grup_id:
            if grup["administrador_id"] != usuari_id:
                raise HTTPException(status_code=403, detail="No tens permís per modificar aquest grup.")
            if modificacions.nom:
                grup["nom"] = modificacions.nom
            if modificacions.usuaris:
                grup["usuaris"] = modificacions.usuaris
            return {"missatge": "Grup modificat correctament", "grup": grup}
    raise HTTPException(status_code=404, detail="Grup no trobat.")
