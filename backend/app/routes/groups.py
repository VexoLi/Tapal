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

@router.delete("/grups/{grup_id}/usuaris/{usuari_id}")
def eliminar_usuari(grup_id: int, usuari_id: int, administrador_id: int):
    """
    Permet als administradors eliminar un usuari d'un grup.
    """
    for grup in grups:
        if grup["id"] == grup_id:
            if grup["administrador_id"] != administrador_id:
                raise HTTPException(status_code=403, detail="No tens permís per eliminar usuaris d'aquest grup.")
            if usuari_id not in grup["usuaris"]:
                raise HTTPException(status_code=404, detail="Usuari no trobat en aquest grup.")
            grup["usuaris"].remove(usuari_id)
            return {"missatge": "Usuari eliminat del grup."}
    raise HTTPException(status_code=404, detail="Grup no trobat.")

@router.put("/grups/{grup_id}/administrador")
def assignar_administrador(grup_id: int, nou_admin_id: int, usuari_id: int):
    """
    Permet als administradors assignar un nou administrador.
    """
    for grup in grups:
        if grup["id"] == grup_id:
            if grup["administrador_id"] != usuari_id:
                raise HTTPException(status_code=403, detail="No tens permís per assignar administradors.")
            if nou_admin_id not in grup["usuaris"]:
                raise HTTPException(status_code=400, detail="El nou administrador ha de ser membre del grup.")
            grup["administrador_id"] = nou_admin_id
            return {"missatge": "Nou administrador assignat."}
    raise HTTPException(status_code=404, detail="Grup no trobat.")

@router.delete("/grups/{grup_id}/sortir")
def sortir_grup(grup_id: int, usuari_id: int):
    """
    Permet a qualsevol usuari sortir d'un grup.
    """
    for grup in grups:
        if grup["id"] == grup_id:
            if usuari_id in grup["usuaris"]:
                grup["usuaris"].remove(usuari_id)
                return {"missatge": "Has sortit del grup."}
            else:
                raise HTTPException(status_code=404, detail="No formes part d'aquest grup.")
    raise HTTPException(status_code=404, detail="Grup no trobat.")
