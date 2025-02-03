from fastapi import APIRouter, Depends, HTTPException
from app.utils import verify_token
from app.models import UsuarisClase

router = APIRouter()

@router.get("/llistaamics", tags=["Friends"])
async def llistaamics(user: dict = Depends(verify_token)):
    """
    Devuelve una lista de todos los usuarios excepto el usuario actual.
    """
    user_id = user["user_id"]  # Extraer el ID del usuario desde el token

    try:
        db = UsuarisClase()
        usuarios = db.obtener_todos_los_usuarios()

        # Excluir al usuario actual de la lista
        amigos = [
            {"id": usuario["id"], "username": usuario["username"]}
            for usuario in usuarios
            if usuario["id"] != user_id
        ]

        return {"friends": amigos}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener amigos: {e}")

@router.get("/grups", tags=["Groups"])
async def listar_grupos(user: dict = Depends(verify_token)):
    """
    Devuelve todos los grupos en los que el usuario autenticado es miembro.
    """
    user_id = user["user_id"]
    db = UsuarisClase()
    grupos = db.obtener_grupos_por_usuario(user_id)

    return {"groups": grupos}

@router.post("/grups", tags=["Groups"])
async def crear_grupo(nombre: str, user: dict = Depends(verify_token)):
    """
    Crea un nuevo grupo con el usuario autenticado como administrador.
    """
    user_id = user["user_id"]
    db = UsuarisClase()
    resultado = db.crear_grupo(nombre, user_id)

    if not resultado:
        raise HTTPException(status_code=500, detail="Error al crear grupo")

    return resultado

@router.put("/grups/{group_id}/transferir-admin", tags=["Groups"])
async def transferir_admin(group_id: int, new_admin_id: int, user: dict = Depends(verify_token)):
    """
    Transfiere la administración de un grupo a otro usuario.
    """
    user_id = user["user_id"]
    db = UsuarisClase()
    resultado = db.transferir_admin(group_id, user_id, new_admin_id)

    if not resultado:
        raise HTTPException(status_code=500, detail="Error al transferir admin")

    return resultado

@router.delete("/grups/{group_id}/salir", tags=["Groups"])
async def salir_grupo(group_id: int, user: dict = Depends(verify_token)):
    """
    Permite a un usuario salir de un grupo.
    """
    user_id = user["user_id"]
    db = UsuarisClase()
    resultado = db.salir_del_grupo(group_id, user_id)

    if not resultado:
        raise HTTPException(status_code=500, detail="Error al salir del grupo")

    return resultado

@router.put("/grups/{group_id}/editar-nombre", tags=["Groups"])
async def editar_nombre_grupo(group_id: int, nuevo_nombre: str, user: dict = Depends(verify_token)):
    """
    Permite al administrador cambiar el nombre del grupo.
    """
    user_id = user["user_id"]
    db = UsuarisClase()

    # Verificar si el usuario es el administrador del grupo
    if not db.es_admin(user_id, group_id):
        raise HTTPException(status_code=403, detail="No tienes permisos para editar el grupo")

    # Cambiar el nombre del grupo
    resultado = db.editar_nombre_grupo(group_id, nuevo_nombre)
    if not resultado:
        raise HTTPException(status_code=500, detail="Error al editar el nombre del grupo")

    return {"message": "Nombre del grupo actualizado correctamente"}

@router.post("/grups/{group_id}/agregar-usuario", tags=["Groups"])
async def agregar_usuario_grupo(group_id: int, nuevo_miembro_id: int, user: dict = Depends(verify_token)):
    """
    Permite al administrador añadir un usuario al grupo.
    """
    user_id = user["user_id"]
    db = UsuarisClase()

    # Verificar si el usuario es administrador del grupo
    if not db.es_admin(user_id, group_id):
        raise HTTPException(status_code=403, detail="No tienes permisos para agregar usuarios")

    # Verificar si el usuario ya es miembro del grupo
    if db.es_miembro(nuevo_miembro_id, group_id):
        raise HTTPException(status_code=400, detail="El usuario ya es miembro del grupo")

    # Agregar usuario al grupo
    resultado = db.agregar_usuario_grupo(group_id, nuevo_miembro_id)
    if not resultado:
        raise HTTPException(status_code=500, detail="Error al agregar usuario al grupo")

    return {"message": "Usuario agregado al grupo correctamente"}

@router.delete("/grups/{group_id}/eliminar-usuario/{miembro_id}", tags=["Groups"])
async def eliminar_usuario_grupo(group_id: int, miembro_id: int, user: dict = Depends(verify_token)):
    """
    Permite al administrador eliminar un usuario del grupo.
    """
    user_id = user["user_id"]
    db = UsuarisClase()

    # Verificar si el usuario que ejecuta la acción es el administrador del grupo
    if not db.es_admin(user_id, group_id):
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar miembros del grupo")

    # Verificar si el usuario es miembro del grupo
    if not db.es_miembro(miembro_id, group_id):
        raise HTTPException(status_code=400, detail="El usuario no pertenece al grupo")

    # No permitir que el administrador se elimine a sí mismo
    if user_id == miembro_id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")

    # Eliminar usuario del grupo
    resultado = db.eliminar_miembro(group_id, miembro_id)
    if not resultado:
        raise HTTPException(status_code=500, detail="Error al eliminar usuario del grupo")

    return {"message": "Usuario eliminado del grupo correctamente"}

@router.delete("/grups/{group_id}/expulsar-usuario", tags=["Groups"])
async def expulsar_usuario_grupo(group_id: int, usuario_a_expulsar: int, user: dict = Depends(verify_token)):
    """
    Permite al administrador expulsar a un usuario del grupo.
    El administrador NO puede autoexpulsarse.
    """
    user_id = user["user_id"]
    db = UsuarisClase()

    # Verificar si el usuario es administrador del grupo
    if not db.es_admin(user_id, group_id):
        raise HTTPException(status_code=403, detail="No tienes permisos para expulsar usuarios")

    # Evitar que el admin se autoexpulse
    if user_id == usuario_a_expulsar:
        raise HTTPException(status_code=400, detail="No puedes autoexpulsarte, usa la opción de salir del grupo")

    # Verificar si el usuario está en el grupo
    if not db.es_miembro(usuario_a_expulsar, group_id):
        raise HTTPException(status_code=400, detail="El usuario no es miembro de este grupo")

    # Expulsar al usuario del grupo
    resultado = db.eliminar_miembro(group_id, usuario_a_expulsar)
    if not resultado:
        raise HTTPException(status_code=500, detail="Error al expulsar usuario del grupo")

    return {"message": "Usuario expulsado correctamente"}

@router.post("/missatgesAmics", tags=["Messages"])
async def enviar_mensaje_amigo(
    receiver_id: int,
    content: str,
    user: dict = Depends(verify_token)
):
    """
    Permite a un usuario enviar un mensaje a otro usuario.
    No se permite enviarse mensajes a sí mismo.
    """
    sender_id = user["user_id"]
    db = UsuarisClase()

    if sender_id == receiver_id:
        raise HTTPException(status_code=400, detail="No puedes enviarte mensajes a ti mismo")

    # Guardar el mensaje en la base de datos
    resultado = db.guardar_mensaje(sender_id, receiver_id, content)

    if not resultado:
        raise HTTPException(status_code=500, detail="Error al enviar el mensaje")

    return {"message": "Mensaje enviado correctamente"}

@router.get("/missatgesAmics", tags=["Messages"])
async def obtener_mensajes_amigo(
    friend_id: int,
    page: int = 1,
    user: dict = Depends(verify_token)
):
    """
    Obtiene los 10 mensajes más recientes con un usuario.
    Se pueden obtener mensajes más antiguos con paginación.
    """
    
    if page < 1:
        raise HTTPException(status_code=400, detail="El número de página debe ser 1 o mayor")
    
    user_id = user["user_id"]
    db = UsuarisClase()

    # Obtener mensajes con paginación
    mensajes = db.obtener_mensajes(user_id, friend_id, page)

    return {"messages": mensajes}

@router.get("/missatgesAmics", tags=["Messages"])
async def obtener_mensajes_amigo(
    friend_id: int,
    page: int = 1,
    user: dict = Depends(verify_token)
):
    """
    Obtiene los 10 mensajes más recientes con un usuario.
    Al abrir el chat, los mensajes enviados a este usuario se marcan como 'received'.
    """
    user_id = user["user_id"]
    db = UsuarisClase()

    # Obtener mensajes con paginación
    mensajes = db.obtener_mensajes(user_id, friend_id, page)

    # Marcar mensajes como 'received' al abrir el chat
    db.actualizar_estado_mensajes(user_id, friend_id, "received")

    return {"messages": mensajes}


@router.put("/check", tags=["Messages"])
async def marcar_mensajes_como_leidos(friend_id: int, user: dict = Depends(verify_token)):
    """
    Permite actualizar el estado de los mensajes con un amigo a 'read'.
    """
    user_id = user["user_id"]
    db = UsuarisClase()

    resultado = db.actualizar_estado_mensajes(user_id, friend_id, "read")
    
    if not resultado:
        raise HTTPException(status_code=500, detail="Error al actualizar el estado de los mensajes")

    return {"message": "Mensajes marcados como 'read'"}

@router.get("/missatgesgrup", tags=["Group Messages"])
async def obtener_mensajes_grupo(
    group_id: int,
    page: int = 1,
    user: dict = Depends(verify_token)
):
    """
    Obtiene los 10 mensajes más recientes de un grupo con paginación.
    """
    user_id = user["user_id"]
    db = UsuarisClase()

    # Verificar si el usuario es miembro del grupo
    if not db.es_miembro(user_id, group_id):
        raise HTTPException(status_code=403, detail="No eres miembro de este grupo")

    # Obtener mensajes
    mensajes = db.obtener_mensajes_grupo(group_id, page)

    return {"messages": mensajes}

@router.post("/missatgesgrup", tags=["Group Messages"])
async def enviar_mensaje_grupo(
    group_id: int,
    content: str,
    user: dict = Depends(verify_token)
):
    """
    Permite a un usuario enviar un mensaje a un grupo.
    """
    user_id = user["user_id"]
    db = UsuarisClase()

    # Verificar si el usuario es miembro del grupo
    if not db.es_miembro(user_id, group_id):
        raise HTTPException(status_code=403, detail="No eres miembro de este grupo")

    # Guardar mensaje en la base de datos
    resultado = db.enviar_mensaje_grupo(user_id, group_id, content)

    return resultado

@router.post("/missatgesgrup", tags=["Group Messages"])
async def enviar_mensaje_grupo(
    group_id: int, content: str, user: dict = Depends(verify_token)
):
    """
    Envía un mensaje a un grupo y lo marca como 'recibido' para los demás miembros.
    """
    user_id = user["user_id"]
    db = UsuarisClase()
    resultado = db.enviar_mensaje_grupo(user_id, group_id, content)

    if not resultado:
        raise HTTPException(status_code=500, detail="Error al enviar mensaje")

    return resultado

@router.put("/missatgesgrup/leidos", tags=["Group Messages"])
async def marcar_mensajes_grupo_leidos(group_id: int, user: dict = Depends(verify_token)):
    """
    Marca todos los mensajes no leídos en un grupo como 'leído' para el usuario autenticado.
    """
    user_id = user["user_id"]
    db = UsuarisClase()
    resultado = db.marcar_mensajes_leidos_grupo(user_id, group_id)

    if not resultado:
        raise HTTPException(status_code=500, detail="Error al marcar mensajes como leídos")

    return resultado

@router.get("/missatges/nolegits", tags=["Messages"])
async def obtener_mensajes_no_llegits(user: dict = Depends(verify_token)):
    """
    Devuelve la cantidad de mensajes no leídos en chats individuales y grupales.
    """
    user_id = user["user_id"]
    db = UsuarisClase()
    mensajes_no_llegits = db.obtener_mensajes_no_llegits(user_id)

    if mensajes_no_llegits is None:
        raise HTTPException(status_code=500, detail="Error al obtener mensajes no leídos")

    return mensajes_no_llegits

@router.put("/grups/{group_id}/asignar-admin", tags=["Groups"])
async def asignar_admin(group_id: int, nuevo_admin_id: int, user: dict = Depends(verify_token)):
    """
    Permite a un administrador del grupo otorgar el rol de admin a otro usuario.
    """
    user_id = user["user_id"]
    db = UsuarisClase()

    # Verificar si el usuario que ejecuta la acción es admin
    if not db.es_admin(user_id, group_id):
        raise HTTPException(status_code=403, detail="No tienes permisos para asignar administradores")

    # Verificar si el usuario a promover ya es admin
    if db.es_admin(nuevo_admin_id, group_id):
        raise HTTPException(status_code=400, detail="El usuario ya es administrador")

    # No permitir que el usuario se asigne a sí mismo
    if user_id == nuevo_admin_id:
        raise HTTPException(status_code=400, detail="No puedes asignarte el rol de administrador a ti mismo")

    # Verificar si el usuario a promover es miembro del grupo
    if not db.es_miembro(nuevo_admin_id, group_id):
        raise HTTPException(status_code=400, detail="El usuario no pertenece al grupo")

    # Asignar el rol de admin al usuario
    resultado = db.asignar_admin(nuevo_admin_id, group_id)
    if not resultado:
        raise HTTPException(status_code=500, detail="Error al asignar el rol de administrador")

    return {"message": "Usuario promovido a administrador correctamente"}
