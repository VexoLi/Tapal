from fastapi import APIRouter

router = APIRouter()

# Mock data per a grups
grups = [
    {"id": 1, "nom": "Grup 1", "administrador_id": 1, "usuaris": [1, 2]},
    {"id": 2, "nom": "Grup 2", "administrador_id": 2, "usuaris": [2, 3]}
]

@router.get("/grups")
def get_grups(usuari_id: int):
    """
    Retorna els grups on participa l'usuari.
    """
    return {
        "grups": [
            grup for grup in grups if usuari_id in grup["usuaris"]
        ]
    }

@router.post("/grups")
def crear_grup(nom: str, administrador_id: int):
    """
    Crea un nou grup i assigna l'usuari com a administrador.
    """
    nou_grup = {
        "id": len(grups) + 1,
        "nom": nom,
        "administrador_id": administrador_id,
        "usuaris": [administrador_id]
    }
    grups.append(nou_grup)
    return {"missatge": "Grup creat correctament", "grup": nou_grup}
