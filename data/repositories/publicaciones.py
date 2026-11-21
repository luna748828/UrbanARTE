import uuid
from db import db, get_admin_client

PALETA = ["#ff3d6e", "#ffb703", "#2ec4b6", "#7b5cff", "#ff7a1a", "#3ddc97"]

class PublicacionRepository:
    @staticmethod
    def _formatear_post(r):
        autor = r.get("usuarios") or {}
        ubic = r.get("ubicaciones") or {}
        if isinstance(ubic, list):
            ubic = ubic[0] if ubic else {}

        return {
            "id": r["id"],
            "usuario_id": r["usuario_id"],
            "autor": autor.get("nombre_usuario", "anónimo"),
            "artista": r.get("artista") or autor.get("nombre_usuario", "anónimo"),
            "categoria": r.get("categoria") or "GRAFITI",
            "descripcion": r.get("descripcion") or "",
            "texto": r.get("descripcion") or "",
            "imagen": r.get("imagen"),
            "imagen_url": r.get("imagen"),
            "lugar": ubic.get("direccion_aprox", ""),
            "lat": ubic.get("latitud"),
            "lng": ubic.get("longitud"),
            "fecha_publicacion": r.get("fecha_publicacion"),
            "acento": PALETA[r["id"] % len(PALETA)],
        }

    @staticmethod
    def obtener_recientes(limite=30):
        try:
            res = (
                db.table("publicaciones")
                .select("id, usuario_id, descripcion, imagen, categoria, artista, fecha_publicacion, "
                        "usuarios(nombre_usuario), ubicaciones(direccion_aprox, latitud, longitud)")
                .order("fecha_publicacion", desc=True)
                .limit(limite)
                .execute()
            )
            return [PublicacionRepository._formatear_post(r) for r in (res.data or [])]
        except Exception as e:
            print("Error cargando publicaciones:", e)
            return []

    @staticmethod
    def obtener_por_usuario(usuario_id):
        try:
            res = (
                db.table("publicaciones")
                .select("id, usuario_id, descripcion, imagen, categoria, artista, fecha_publicacion, "
                        "usuarios(nombre_usuario), ubicaciones(direccion_aprox, latitud, longitud)")
                .eq("usuario_id", usuario_id)
                .order("fecha_publicacion", desc=True)
                .execute()
            )
            return [PublicacionRepository._formatear_post(r) for r in (res.data or [])]
        except Exception as e:
            print("Error cargando mis publicaciones:", e)
            return []

    @staticmethod
    def obtener_por_id(publicacion_id):
        res = (
            db.table("publicaciones")
            .select("*")
            .eq("id", publicacion_id)
            .execute()
        )
        return res.data[0] if res.data else None

    @staticmethod
    def crear(usuario_id, descripcion, imagen=None, categoria="GRAFITI", artista=None):
        datos = {
            "usuario_id": usuario_id,
            "descripcion": descripcion,
            "imagen": imagen,
            "categoria": categoria,
            "artista": artista,
        }
        res = db.table("publicaciones").insert(datos).execute()
        return res.data[0]["id"]

    @staticmethod
    def actualizar(publicacion_id, usuario_id, descripcion, imagen=None, categoria=None, artista=None):
        datos = {"descripcion": descripcion}
        if imagen is not None:
            datos["imagen"] = imagen
        if categoria is not None:
            datos["categoria"] = categoria
        if artista is not None:
            datos["artista"] = artista

        res = (
            db.table("publicaciones")
            .update(datos)
            .eq("id", publicacion_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
        return bool(res.data)

    @staticmethod
    def eliminar(publicacion_id, usuario_id):
        db.table("ubicaciones").delete().eq("publicacion_id", publicacion_id).execute()
        res = (
            db.table("publicaciones")
            .delete()
            .eq("id", publicacion_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
        return bool(res.data)

    @staticmethod
    def es_del_usuario(publicacion_id, usuario_id):
        r = (
            db.table("publicaciones")
            .select("id")
            .eq("id", publicacion_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
        return bool(r.data)

    @staticmethod
    def obtener_pendientes_ubicacion():
        res = (
            db.table("publicaciones")
            .select("id, descripcion, usuarios(nombre_usuario), ubicaciones(id)")
            .order("fecha_publicacion", desc=True)
            .execute()
        )
        return [
            {
                "id": r["id"],
                "titulo": f'{(r.get("usuarios") or {}).get("nombre_usuario", "anónimo")}: {(r["descripcion"] or "sin descripción")[:40]}',
            }
            for r in res.data
            if not r.get("ubicaciones")
        ]

    @staticmethod
    def obtener_pendientes_de_usuario(usuario_id):
        pubs = (
            db.table("publicaciones")
            .select("id, descripcion, ubicaciones(id)")
            .eq("usuario_id", usuario_id)
            .order("fecha_publicacion", desc=True)
            .execute()
        ).data
        return [
            {"id": p["id"], "titulo": (p["descripcion"] or "Sin descripción")[:50]}
            for p in pubs
            if not p.get("ubicaciones")
        ]

    @staticmethod
    def subir_imagen(archivo):
        """Valida formato y tamaño, y sube a Supabase Storage. Devuelve (url, error)."""
        if not archivo or archivo.filename == "":
            return None, None

        tipos = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
        ext = tipos.get(archivo.mimetype)
        if not ext:
            return None, "Solo se permiten imágenes JPG, PNG o WEBP."

        datos = archivo.read()
        if len(datos) > 5 * 1024 * 1024:
            return None, "La imagen pesa más de 5 MB."

        cliente = get_admin_client() or db
        nombre = f"{uuid.uuid4().hex}.{ext}"
        try:
            cliente.storage.from_("publicaciones").upload(
                nombre, datos, {"content-type": archivo.mimetype}
            )
        except Exception as e:
            print("Error subiendo imagen:", e)
            return None, "No se pudo subir la imagen al servidor."

        return cliente.storage.from_("publicaciones").get_public_url(nombre), None