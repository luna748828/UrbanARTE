from db import db

class EventoRepository:
    @staticmethod
    def crear(organizador_id, nombre, descripcion, fecha_hora_iso, direccion_aprox, latitud, longitud, cupos=None):
        res = db.table("eventos").insert({
            "organizador_id": organizador_id,
            "nombre": nombre,
            "descripcion": descripcion,
            "fecha_hora": fecha_hora_iso,
            "direccion_aprox": direccion_aprox,
            "latitud": latitud,
            "longitud": longitud,
            "cupos_disponibles": cupos,
        }).execute()
        return res.data[0]["id"]

    @staticmethod
    def obtener_proximos(desde_iso):
        res = (
            db.table("eventos")
            .select("id, nombre, descripcion, fecha_hora, direccion_aprox, "
                    "latitud, longitud, usuarios!eventos_organizador_id_fkey(nombre_usuario)")
            .gte("fecha_hora", desde_iso)
            .order("fecha_hora")
            .execute()
        )
        return res.data
    
    @staticmethod
    def eventos_de_usuario(usuario_id):
        filas = (
            db.table("asistentes_evento")
            .select("evento_id")
            .eq("usuario_id", usuario_id)
            .execute()
        )
        ids = [f["evento_id"] for f in filas.data]
        if not ids:
            return []
        res = (
            db.table("eventos")
            .select("*")
            .in_("id", ids)
            .execute()
        )
        return res.data
    
    @staticmethod
    def obtener_todos():
        res = (
            db.table("eventos")
            .select("id, nombre, descripcion, fecha_hora, direccion_aprox, "
                    "latitud, longitud, cupos_disponibles, "
                    "usuarios!eventos_organizador_id_fkey(nombre_usuario)")
            .order("fecha_hora", desc=True)
            .execute()
        )
        return res.data

    