from datetime import datetime, timedelta, timezone

from data.repositories.foros import ForoRepository

BOGOTA = timezone(timedelta(hours=-5))  # Colombia no tiene horario de verano

TITULO_MIN = 3
TITULO_MAX = 120
TEMA_MAX = 2000
RESPUESTA_MAX = 1000


def _fecha(valor):
    """Convierte la fecha de Supabase a 'dd/mm/aaaa hh:mm' en hora de Colombia."""
    if not valor:
        return ""
    try:
        f = datetime.fromisoformat(str(valor))
        if f.tzinfo is None:
            f = f.replace(tzinfo=timezone.utc)
        return f.astimezone(BOGOTA).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return str(valor)


def _autor(fila):
    """Nombre de quien escribió. Las cuentas dadas de baja salen como 'Usuario eliminado'."""
    u = fila.get("usuarios") or {}
    if isinstance(u, list):
        u = u[0] if u else {}
    nombre = u.get("nombre_usuario")
    if not nombre or nombre.startswith("desactivada_"):
        return "Usuario eliminado"
    return nombre


class ForoService:
    # ---------- lectura ----------

    @staticmethod
    def listar_foros():
        return [
            {
                "id": f["id"],
                "nombre": f["tema_foro"],
                "creador": _autor(f),
                "total_temas": f.get("total_temas", 0),
            }
            for f in ForoRepository.obtener_todos()
        ]

    @staticmethod
    def obtener_foro(foro_id):
        f = ForoRepository.obtener_por_id(foro_id)
        if not f:
            return None
        return {"id": f["id"], "nombre": f["tema_foro"], "creador": _autor(f), "fecha": _fecha(f.get("fecha_foro"))}

    @staticmethod
    def obtener_temas(foro_id):
        temas = []
        for t in ForoRepository.obtener_temas(foro_id):
            contenido = t["contenido"] or ""
            temas.append({
                "id": t["id"],
                "titulo": t["titulo"] or "(sin título)",
                "autor": _autor(t),
                "fecha": _fecha(t.get("fecha")),
                "resumen": contenido if len(contenido) <= 140 else contenido[:140].rstrip() + "…",
                "total_respuestas": t.get("total_respuestas", 0),
            })
        return temas

    @staticmethod
    def obtener_tema(foro_id, tema_id):
        t = ForoRepository.obtener_tema(foro_id, tema_id)
        if not t:
            return None
        return {
            "id": t["id"],
            "titulo": t["titulo"] or "(sin título)",
            "contenido": t["contenido"],
            "autor": _autor(t),
            "fecha": _fecha(t.get("fecha")),
            "respuestas": [
                {"id": r["id"], "contenido": r["contenido"], "autor": _autor(r), "fecha": _fecha(r.get("fecha"))}
                for r in ForoRepository.obtener_respuestas(tema_id)
            ],
        }

    # ---------- escritura (reglas) ----------

    @staticmethod
    def crear_tema(foro_id, usuario_id, titulo, contenido):
        """Devuelve (exito, mensaje, id_del_tema)."""
        titulo = (titulo or "").strip()
        contenido = (contenido or "").strip()

        if len(titulo) < TITULO_MIN:
            return False, f"El título debe tener al menos {TITULO_MIN} caracteres.", None
        if len(titulo) > TITULO_MAX:
            return False, f"El título no puede pasar de {TITULO_MAX} caracteres.", None
        if not contenido:
            return False, "Escribe el contenido del tema.", None
        if len(contenido) > TEMA_MAX:
            return False, f"El contenido no puede pasar de {TEMA_MAX} caracteres.", None
        if not ForoRepository.obtener_por_id(foro_id):
            return False, "Ese foro no existe.", None

        try:
            tema_id = ForoRepository.crear_tema(foro_id, usuario_id, titulo, contenido)
        except Exception as e:
            print("Error creando el tema:", e)
            return False, "No se pudo publicar el tema.", None
        return True, "Tema publicado.", tema_id

    @staticmethod
    def responder(foro_id, tema_id, usuario_id, contenido):
        """Devuelve (exito, mensaje)."""
        contenido = (contenido or "").strip()

        if not contenido:
            return False, "Escribe tu respuesta."
        if len(contenido) > RESPUESTA_MAX:
            return False, f"La respuesta no puede pasar de {RESPUESTA_MAX} caracteres."
        if not ForoRepository.obtener_tema(foro_id, tema_id):
            return False, "Ese tema no existe."

        try:
            ForoRepository.crear_respuesta(foro_id, tema_id, usuario_id, contenido)
        except Exception as e:
            print("Error creando la respuesta:", e)
            return False, "No se pudo publicar la respuesta."
        return True, "Respuesta publicada."