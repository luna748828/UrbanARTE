from datetime import datetime, timedelta, timezone
from data.repositories.eventos import EventoRepository
from data.repositories.asistentes import AsistenteRepository

COLOMBIA = timezone(timedelta(hours=-5))


class EventoService:
    @staticmethod
    def crear(organizador_id, form):
        nombre_evento = (form.get("nombre") or "").strip()
        descripcion = (form.get("descripcion") or "").strip()
        fecha = (form.get("fecha") or "").strip()
        hora = (form.get("hora") or "").strip()
        direccion = (form.get("direccion") or "").strip() or None
        lat = (form.get("lat") or "").strip()
        lng = (form.get("lng") or "").strip()

        if not nombre_evento:
            return False, "El nombre es obligatorio"
        if len(nombre_evento) > 100:
            return False, "El nombre es muy largo (máximo 100 caracteres)"
        if not descripcion:
            return False, "La descripción es obligatoria"
        if not fecha or not hora:
            return False, "Elige la fecha y la hora"
        try:
            momento = datetime.fromisoformat(f"{fecha}T{hora}").replace(tzinfo=COLOMBIA)
        except ValueError:
            return False, "Fecha u hora inválida"
        if momento < datetime.now(COLOMBIA):
            return False, "El evento no puede estar en el pasado"

        latitud = longitud = None
        if lat or lng:
            try:
                latitud = float(lat)
                longitud = float(lng)
            except ValueError:
                return False, "Ubicación inválida"
            if not (-90 <= latitud <= 90 and -180 <= longitud <= 180):
                return False, "Ubicación fuera de rango"

        # Cupos: vacío = sin límite (se guarda como None); un número = cupos limitados
        cupos = None
        cupos_txt = str(form.get("cupos") or "").strip()
        if cupos_txt:
            try:
                cupos = int(cupos_txt)
            except ValueError:
                return False, "Los cupos deben ser un número"
            if not 1 <= cupos <= 10000:
                return False, "Los cupos deben estar entre 1 y 10000"

        try:
            evento_id = EventoRepository.crear(
                organizador_id, nombre_evento, descripcion, momento.isoformat(),
                direccion, latitud, longitud, cupos,
            )
        except Exception as e:
            print("Error creando evento:", e)
            return False, "No se pudo guardar el evento"

        # El organizador queda inscrito automáticamente y NO gasta cupo
        try:
            AsistenteRepository.unirse(evento_id, organizador_id)
        except Exception as e:
            print("Aviso: no se pudo inscribir al organizador:", e)
        return True, None

    @staticmethod
    def listar_proximos():
        try:
            filas = EventoRepository.obtener_proximos(datetime.now(timezone.utc).isoformat())
        except Exception as e:
            print("Error cargando eventos:", e)
            return []

        eventos = []
        for f in filas:
            momento = datetime.fromisoformat(f["fecha_hora"]).astimezone(COLOMBIA)
            eventos.append({
                "nombre": f["nombre"],
                "descripcion": f["descripcion"] or "",
                "fecha": momento.strftime("%d/%m/%Y"),
                "hora": momento.strftime("%I:%M %p"),
                "direccion": f.get("direccion_aprox") or "",
                "latitud": f.get("latitud"),
                "longitud": f.get("longitud"),
                "creador": (f.get("usuarios") or {}).get("nombre_usuario", "anónimo"),
            })
        return eventos