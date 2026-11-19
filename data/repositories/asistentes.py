from db import db


class AsistenteRepository:

    @staticmethod
    def existe(evento_id, usuario_id):
        res = (
            db.table("asistentes_evento")
            .select("evento_id")
            .eq("evento_id", evento_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
        return len(res.data) > 0

    @staticmethod
    def unirse(evento_id, usuario_id):
        db.table("asistentes_evento").insert({
            "evento_id": evento_id,
            "usuario_id": usuario_id,
        }).execute()

    @staticmethod
    def salir(evento_id, usuario_id):
        db.table("asistentes_evento").delete() \
            .eq("evento_id", evento_id) \
            .eq("usuario_id", usuario_id) \
            .execute()

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
            .select(
                "id, organizador_id, descripcion, fecha_hora, cupos_disponibles, descripcion, nombre,  "
                "direccion_aprox, latitud, longitud"
            )
            .in_("id", ids)
            .order("fecha_hora")
            .execute()
        )

        return res.data

    @staticmethod
    def obtener_evento(evento_id):
        res = (
            db.table("eventos")
            .select("id, organizador_id, cupos_disponibles, fecha_hora")
            .eq("id", evento_id)
            .execute()
        )
        return res.data[0] if res.data else None

    @staticmethod
    def ajustar_cupos(evento_id, nuevo_valor):
        db.table("eventos").update({
            "cupos_disponibles": nuevo_valor
        }).eq("id", evento_id).execute()