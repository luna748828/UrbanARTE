from data.repositories.publicaciones import PublicacionRepository
from data.repositories.usuarios import UsuarioRepository
from data.repositories.ubicaciones import UbicacionRepository

class FeedService:
    @staticmethod
    def obtener_feed_principal():
        posts = PublicacionRepository.obtener_recientes()
        historias = UsuarioRepository.obtener_recientes()
        return posts, historias

    @staticmethod
    def obtener_solo_posts():
        return PublicacionRepository.obtener_recientes()

    @staticmethod
    def obtener_pendientes_mapa():
        return PublicacionRepository.obtener_pendientes_ubicacion()

    @staticmethod
    def obtener_todas_ubicaciones():
        return UbicacionRepository.obtener_todas()

    @staticmethod
    def crear_ubicacion(datos):
        return UbicacionRepository.guardar(
            publicacion_id=datos["publicacion_id"],
            latitud=datos["latitud"],
            longitud=datos["longitud"],
            direccion_aprox=datos.get("direccion_aprox")
        )
    @staticmethod
    def obtener_pendientes_de_usuario(usuario_id):
        return PublicacionRepository.obtener_pendientes_de_usuario(usuario_id)

    @staticmethod
    def publicacion_es_del_usuario(publicacion_id, usuario_id):
        return PublicacionRepository.es_del_usuario(publicacion_id, usuario_id)