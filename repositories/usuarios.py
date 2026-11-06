from db import db

class UsuarioRepository:
    @staticmethod
    def buscar_por_nombre(nombre_usuario):
        res = db.table("usuarios").select("id").eq("nombre_usuario", nombre_usuario).execute()
        return res.data

    @staticmethod
    def buscar_por_id(usuario_id):
        res = db.table("usuarios").select("*").eq("id", usuario_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def crear_perfil(usuario_id, nombre, correo, rol="artista"):
        return db.table("usuarios").insert({
            "id": usuario_id,
            "nombre_usuario": nombre,
            "correo": correo,
            "rol": rol
        }).execute()

    @staticmethod
    def obtener_recientes(limite=8):
        res = db.table("usuarios").select("nombre_usuario").order("creado_en", desc=True).limit(limite).execute()
        return [u["nombre_usuario"] for u in res.data] if res.data else []

    @staticmethod
    def actualizar_perfil(usuario_id, datos):
        return db.table("usuarios").update(datos).eq("id", usuario_id).execute()

    @staticmethod
    def eliminar_perfil(usuario_id):
        return db.table("usuarios").delete().eq("id", usuario_id).execute()