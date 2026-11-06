from db import db

class UbicacionRepository:
    @staticmethod
    def obtener_todas():
        res = (
            db.table("ubicaciones")
            .select("direccion_aprox, latitud, longitud, "
                    "publicaciones(descripcion, imagen, usuarios(nombre_usuario))")
            .execute()
        )
        return res.data

    @staticmethod
    def guardar(publicacion_id, latitud, longitud, direccion_aprox=None):
        return db.table("ubicaciones").insert({
            "publicacion_id": publicacion_id,
            "direccion_aprox": direccion_aprox,
            "latitud": latitud,
            "longitud": longitud,
        }).execute()