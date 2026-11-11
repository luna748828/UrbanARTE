from db import db


class ForoRepository:
    """Datos de los foros (tabla foros) y de sus temas y respuestas (tabla mensajes).

    Un TEMA es un mensaje con título y sin padre (mensaje_padre_id vacío).
    Una RESPUESTA es un mensaje cuyo mensaje_padre_id apunta a su tema.
    """

    @staticmethod
    def obtener_todos():
        try:
            foros = (
                db.table("foros")
                .select("id, tema_foro, fecha_foro, usuarios(nombre_usuario)")
                .order("id")
                .execute()
                .data
            )
            mensajes = db.table("mensajes").select("foro_id, mensaje_padre_id").execute().data
        except Exception as e:
            print("Error cargando foros:", e)
            return []

        temas_por_foro = {}
        for m in mensajes:
            if m["mensaje_padre_id"] is None:
                temas_por_foro[m["foro_id"]] = temas_por_foro.get(m["foro_id"], 0) + 1
        for f in foros:
            f["total_temas"] = temas_por_foro.get(f["id"], 0)
        return foros

    @staticmethod
    def obtener_por_id(foro_id):
        try:
            res = (
                db.table("foros")
                .select("id, tema_foro, fecha_foro, usuarios(nombre_usuario)")
                .eq("id", foro_id)
                .limit(1)
                .execute()
            )
        except Exception as e:
            print("Error cargando el foro:", e)
            return None
        return res.data[0] if res.data else None

    @staticmethod
    def obtener_temas(foro_id):
        try:
            temas = (
                db.table("mensajes")
                .select("id, titulo, contenido, fecha, usuarios(nombre_usuario)")
                .eq("foro_id", foro_id)
                .is_("mensaje_padre_id", "null")
                .order("fecha", desc=True)
                .execute()
                .data
            )
            todos = db.table("mensajes").select("mensaje_padre_id").eq("foro_id", foro_id).execute().data
        except Exception as e:
            print("Error cargando temas:", e)
            return []

        respuestas_por_tema = {}
        for m in todos:
            if m["mensaje_padre_id"] is not None:
                respuestas_por_tema[m["mensaje_padre_id"]] = respuestas_por_tema.get(m["mensaje_padre_id"], 0) + 1
        for t in temas:
            t["total_respuestas"] = respuestas_por_tema.get(t["id"], 0)
        return temas

    @staticmethod
    def obtener_tema(foro_id, tema_id):
        """Un tema, solo si pertenece a ese foro."""
        try:
            res = (
                db.table("mensajes")
                .select("id, foro_id, usuario_id, titulo, contenido, fecha, usuarios(nombre_usuario)")
                .eq("id", tema_id)
                .eq("foro_id", foro_id)
                .is_("mensaje_padre_id", "null")
                .limit(1)
                .execute()
            )
        except Exception as e:
            print("Error cargando el tema:", e)
            return None
        return res.data[0] if res.data else None

    @staticmethod
    def obtener_respuestas(tema_id):
        try:
            return (
                db.table("mensajes")
                .select("id, usuario_id, contenido, fecha, usuarios(nombre_usuario)")
                .eq("mensaje_padre_id", tema_id)
                .order("fecha")
                .execute()
                .data
            )
        except Exception as e:
            print("Error cargando respuestas:", e)
            return []

    @staticmethod
    def crear_tema(foro_id, usuario_id, titulo, contenido):
        res = db.table("mensajes").insert({
            "foro_id": foro_id,
            "usuario_id": usuario_id,
            "titulo": titulo,
            "contenido": contenido,
        }).execute()
        return res.data[0]["id"]

    @staticmethod
    def crear_respuesta(foro_id, tema_id, usuario_id, contenido):
        res = db.table("mensajes").insert({
            "foro_id": foro_id,
            "usuario_id": usuario_id,
            "mensaje_padre_id": tema_id,
            "contenido": contenido,
        }).execute()
        return res.data[0]["id"]

    @staticmethod
    def obtener_respuesta(tema_id, respuesta_id):
        """Una respuesta, solo si pertenece a ese tema."""
        try:
            res = (
                db.table("mensajes")
                .select("id, usuario_id, contenido")
                .eq("id", respuesta_id)
                .eq("mensaje_padre_id", tema_id)
                .limit(1)
                .execute()
            )
        except Exception as e:
            print("Error cargando la respuesta:", e)
            return None
        return res.data[0] if res.data else None

    @staticmethod
    def actualizar_tema(tema_id, titulo, contenido):
        db.table("mensajes").update({"titulo": titulo, "contenido": contenido}).eq("id", tema_id).execute()

    @staticmethod
    def actualizar_respuesta(respuesta_id, contenido):
        db.table("mensajes").update({"contenido": contenido}).eq("id", respuesta_id).execute()

    @staticmethod
    def eliminar_tema(tema_id):
        # Primero sus respuestas y luego el tema
        db.table("mensajes").delete().eq("mensaje_padre_id", tema_id).execute()
        db.table("mensajes").delete().eq("id", tema_id).execute()

    @staticmethod
    def eliminar_respuesta(respuesta_id):
        db.table("mensajes").delete().eq("id", respuesta_id).execute()