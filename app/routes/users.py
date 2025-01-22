from fastapi import APIRouter

router = APIRouter()

# Mock data per a usuaris
usuaris = [
    {"id": 1, "username": "user1", "password": "123456"},
    {"id": 2, "username": "user2", "password": "123456"},
    {"id": 3, "username": "user3", "password": "123456"}
]

@router.get("/llistaamics")
def get_llista_amics():
    """
    Retorna tots els usuaris de la classe.
    """
    return {"amics": usuaris}
