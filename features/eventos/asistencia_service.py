from datetime import datetime, timezone
from data.repositories.asistentes import AsistenteRepository


class AsistenciaService:
    @staticmethod
    def unirse(evento_id, usuario_id):
        evento = AsistenteRepository.obtener_evento(evento_id)
        if not evento:
            return False, "El evento no existe", 404

        if evento["fecha_hora"]:
            momento = datetime.fromisoformat(evento["fecha_hora"])
            if momento < datetime.now(timezone.utc):
                return False, "El evento ya pasó", 400

        if AsistenteRepository.existe(evento_id, usuario_id):
            return False, "Ya estás inscrito en este evento", 409

        # El organizador no gasta cupo
        es_organizador = evento.get("organizador_id") == usuario_id
        cupos = evento.get("cupos_disponibles")
        if not es_organizador and cupos is not None and cupos <= 0:
            return False, "No quedan cupos", 409

        try:
            AsistenteRepository.unirse(evento_id, usuario_id)
        except Exception as e:
            if "23505" in str(e) or "duplicate" in str(e).lower():
                return False, "Ya estás inscrito en este evento", 409
            print("Error inscribiendo:", e)
            return False, "No se pudo inscribir", 500

        if not es_organizador and cupos is not None:
            AsistenteRepository.ajustar_cupos(evento_id, cupos - 1)
        return True, "Inscripción exitosa", 201

    @staticmethod
    def salir(evento_id, usuario_id):
        evento = AsistenteRepository.obtener_evento(evento_id)
        if not evento:
            return False, "El evento no existe", 404
        if evento.get("organizador_id") == usuario_id:
            return False, "El organizador no puede salir de su propio evento", 400
        if not AsistenteRepository.existe(evento_id, usuario_id):
            return False, "No estás inscrito en este evento", 409

        AsistenteRepository.salir(evento_id, usuario_id)
        cupos = evento.get("cupos_disponibles")
        if cupos is not None:
            AsistenteRepository.ajustar_cupos(evento_id, cupos + 1)
        return True, "Inscripción cancelada", 200

    @staticmethod
    def mis_eventos(usuario_id):
        try:
            return AsistenteRepository.eventos_de_usuario(usuario_id)
        except Exception as e:
            print("Error cargando mis eventos:", e)
            return []