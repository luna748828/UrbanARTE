from db import db

class EventoRepository:
    @staticmethod
    def crear(organizador_id, nombre, descripcion, fecha_hora_iso, direccion_aprox, latitud, longitud):
        res = db.table("eventos").insert({
            "organizador_id": organizador_id,
            "nombre": nombre,
            "descripcion": descripcion,
            "fecha_hora": fecha_hora_iso,
            "direccion_aprox": direccion_aprox,
            "latitud": latitud,
            "longitud": longitud,
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