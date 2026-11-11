from db import db

PALETA = ["#ff3d6e", "#ffb703", "#2ec4b6", "#7b5cff", "#ff7a1a", "#3ddc97"]

class PublicacionRepository:
    @staticmethod
    def obtener_recientes(limite=20):
        try:
            res = (
                db.table("publicaciones")
                .select("id, descripcion, imagen, fecha_publicacion, "
                        "usuarios(nombre_usuario), ubicaciones(direccion_aprox)")
                .order("fecha_publicacion", desc=True)
                .limit(limite)
                .execute()
            )
        except Exception as e:
            print("Error cargando publicaciones:", e)
            return []

        posts = []
        for r in res.data:
            autor = r.get("usuarios") or {}
            ubic = r.get("ubicaciones") or {}
            if isinstance(ubic, list):
                ubic = ubic[0] if ubic else {}
            posts.append({
                "autor": autor.get("nombre_usuario", "anónimo"),
                "lugar": ubic.get("direccion_aprox", ""),
                "texto": r["descripcion"] or "",
                "imagen_url": r["imagen"],
                "acento": PALETA[r["id"] % len(PALETA)],
            })
        return posts

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
    def crear(usuario_id, descripcion, imagen):
        res = db.table("publicaciones").insert({
            "usuario_id": usuario_id,
            "descripcion": descripcion,
            "imagen": imagen,
        }).execute()
        return res.data[0]["id"]

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
    def es_del_usuario(publicacion_id, usuario_id):
        r = (
            db.table("publicaciones")
            .select("id")
            .eq("id", publicacion_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
        return bool(r.data)