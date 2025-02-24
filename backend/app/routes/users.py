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
    Permite a un usuario salir de un grupo:
    - Si es el único usuario, el grupo se elimina completamente.
    - Si es el único admin pero hay más miembros, NO puede salir hasta asignar otro admin.
    - Si hay otros administradores, simplemente puede salir sin problema.
    """
    user_id = user["user_id"]
    db = UsuarisClase()

    # Obtener todos los miembros del grupo
    miembros = db.obtener_miembros_grupo(group_id)

    # ✅ CASO 1: Si el usuario es el único miembro, se elimina el grupo
    if len(miembros) == 1 and miembros[0]["id"] == user_id:
        db.eliminar_grupo(group_id)  # 🔥 Se elimina el grupo completamente
        return {"message": "Grupo eliminado correctamente porque no tenía más miembros."}

    # ✅ CASO 2: Si hay más miembros y el usuario es admin, verificar si hay otros admins
    es_admin = db.es_admin(user_id, group_id)

    if es_admin:
        otros_admins = [m for m in miembros if m["is_admin"] and m["id"] != user_id]

        if not otros_admins:  # ❌ No hay otros admins, evitar la salida
            raise HTTPException(
                status_code=400,
                detail="No puedes salir del grupo porque eres el único administrador. Asigna otro admin antes de salir."
            )

    # ✅ CASO 3: Si hay otros admins o el usuario no es admin, puede salir sin problema
    resultado = db.eliminar_miembro(group_id, user_id)

    if not resultado:
        raise HTTPException(status_code=500, detail="Error al salir del grupo")

    return {"message": "Has salido del grupo correctamente"}


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
    limit: int = 20,  # 🔥 Aquí recibimos el límite
    user: dict = Depends(verify_token)
):
    print(f"🛠️ Recibido en el backend: page={page}, limit={limit}")  # 🛠️ DEBUG

    user_id = user["user_id"]
    db = UsuarisClase()
    mensajes = db.obtener_mensajes(user_id, friend_id, page, limit)

    return {"messages": mensajes, "has_more": len(mensajes) == limit}




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
    limit: int = 20,
    user: dict = Depends(verify_token)
):
    user_id = user["user_id"]
    db = UsuarisClase()

    if not db.es_miembro(user_id, group_id):
        raise HTTPException(status_code=403, detail="No eres miembro de este grupo")

    mensajes = db.obtener_mensajes_grupo(group_id, page, limit)

    return {"messages": mensajes, "has_more": len(mensajes) == limit}



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

@router.get("/grups/{group_id}/usuarios-disponibles", tags=["Groups"])
async def obtener_usuarios_disponibles(group_id: int, user: dict = Depends(verify_token)):
    """
    Devuelve la lista de usuarios que NO están en el grupo, para poder agregarlos.
    """
    db = UsuarisClase()
    
    # Verificar si el usuario es administrador del grupo
    if not db.es_admin(user["user_id"], group_id):
        raise HTTPException(status_code=403, detail="No tienes permisos para agregar usuarios.")

    usuarios_disponibles = db.obtener_usuarios_fuera_del_grupo(group_id)
    return {"available_users": usuarios_disponibles}

@router.get("/grups/{group_id}/usuarios", tags=["Groups"])
async def obtener_usuarios_grupo(group_id: int, user: dict = Depends(verify_token)):
    """
    Devuelve una lista de usuarios dentro de un grupo, incluyendo si son administradores.
    """
    user_id = user["user_id"]
    db = UsuarisClase()

    # Verificar si el usuario es miembro del grupo
    if not db.es_miembro(user_id, group_id):
        raise HTTPException(status_code=403, detail="No eres miembro de este grupo")

    # Obtener la lista de usuarios del grupo
    usuarios = db.obtener_miembros_grupo(group_id)
    return {"users": usuarios}


@router.get("/grups/{group_id}/no-admins", tags=["Groups"])
async def obtener_no_admins(group_id: int, user: dict = Depends(verify_token)):
    """
    Devuelve los miembros de un grupo que NO son administradores.
    """
    db = UsuarisClase()
    
    # Verificar si el usuario que solicita esto es administrador
    if not db.es_admin(user["user_id"], group_id):
        raise HTTPException(status_code=403, detail="No tienes permisos para ver esto.")

    no_admins = db.obtener_no_admins_grupo(group_id)
    return {"non_admin_members": no_admins}

@router.get("/grups/{group_id}/es-admin", tags=["Groups"])
async def verificar_admin(group_id: int, user: dict = Depends(verify_token)):
    """
    Devuelve si el usuario autenticado es administrador del grupo.
    """
    user_id = user["user_id"]
    db = UsuarisClase()
    
    es_admin = db.es_admin(user_id, group_id)  # Verificamos en la base de datos

    return {"is_admin": es_admin}



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