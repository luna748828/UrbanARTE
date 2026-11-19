"""
API JSON para el front en React.
No cambia nada de lo existente: solo reutiliza los servicios y repositorios que ya hay.
Las rutas de eventos (/api/eventos...) siguen en features/eventos/routes.py.
"""
from functools import wraps
from flask import Blueprint, jsonify, request, session

from db import db
from features.auth.auth_service import AuthService
from features.feed.feed_service import FeedService
from features.perfil.perfil_service import PerfilService
from features.foros.foros_service import ForoService
from features.eventos.eventos_service import EventoService
from data.repositories.publicaciones import PublicacionRepository
from data.repositories.ubicaciones import UbicacionRepository

bp = Blueprint("api", __name__, url_prefix="/api")


# ---------- utilidades ----------

def api_login_required(f):
    """Como login_required, pero responde 401 en JSON en vez de redirigir a una página."""
    @wraps(f)
    def envoltura(*args, **kwargs):
        if "usuario_id" not in session:
            return jsonify({"ok": False, "mensaje": "Inicia sesión para continuar"}), 401
        return f(*args, **kwargs)
    return envoltura


def _usuario_actual():
    if "usuario_id" not in session:
        return None
    return {
        "id": session["usuario_id"],
        "nombre_usuario": session.get("nombre_usuario"),
        "rol": session.get("rol"),
    }


def _respuesta(exito, mensaje, extra=None, ok_code=200, error_code=400):
    cuerpo = {"ok": bool(exito), "mensaje": mensaje}
    if extra:
        cuerpo.update(extra)
    return jsonify(cuerpo), (ok_code if exito else error_code)


def _datos():
    return request.get_json(silent=True) or {}


# ---------- sesión ----------

@bp.route("/yo", methods=["GET"])
def yo():
    return jsonify({"usuario": _usuario_actual()})


@bp.route("/login", methods=["POST"])
def login():
    d = _datos()
    correo = (d.get("correo") or "").strip().lower()
    clave = d.get("contrasena") or ""
    perfil, error = AuthService.iniciar_sesion(correo, clave)
    if error:
        return _respuesta(False, error, error_code=401)
    session["usuario_id"] = perfil["id"]
    session["nombre_usuario"] = perfil["nombre_usuario"]
    session["rol"] = perfil["rol"]
    return jsonify({"ok": True, "usuario": _usuario_actual()})


@bp.route("/registro", methods=["POST"])
def registro():
    d = _datos()
    exito, mensaje = AuthService.registrar_usuario(
        (d.get("nombre_usuario") or "").strip(),
        (d.get("correo") or "").strip().lower(),
        d.get("contrasena") or "",
    )
    return _respuesta(exito, mensaje, ok_code=201)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


# ---------- publicaciones / grafitis ----------

@bp.route("/publicaciones", methods=["GET"])
@api_login_required
def publicaciones():
    # Se lee la tabla directo para tener siempre los mismos nombres de campo.
    base = "id, usuario_id, descripcion, imagen, fecha_publicacion, usuarios(nombre_usuario)"
    try:
        filas = (db.table("publicaciones").select(base + ", artista, categoria")
                 .order("fecha_publicacion", desc=True).execute().data)
    except Exception as e:
        print("Aviso: faltan columnas artista/categoria (corre el SQL):", e)
        filas = (db.table("publicaciones").select(base)
                 .order("fecha_publicacion", desc=True).execute().data)

    ubic = (db.table("ubicaciones")
            .select("publicacion_id, direccion_aprox, latitud, longitud").execute().data)
    ubicaciones = {u["publicacion_id"]: u for u in (ubic or [])}

    resultado = []
    for p in (filas or []):
        p = dict(p)
        p["categoria"] = p.get("categoria") or "GRAFITI"
        u = ubicaciones.get(p["id"])
        if u:
            p["latitud"] = u.get("latitud")
            p["longitud"] = u.get("longitud")
            p["direccion_aprox"] = u.get("direccion_aprox")
        resultado.append(p)
    return jsonify(resultado)


@bp.route("/publicaciones", methods=["POST"])
@api_login_required
def crear_publicacion():
    descripcion = request.form.get("descripcion", "").strip()
    if not descripcion:
        return _respuesta(False, "Escribe una descripción")

    imagen = (request.form.get("imagen") or "").strip() or None
    archivo = request.files.get("imagen_archivo")
    if archivo and archivo.filename:
        subir = getattr(PublicacionRepository, "subir_imagen", None)
        if not subir:
            return _respuesta(False, "Falta la función subir_imagen en PublicacionRepository", error_code=500)
        url, error = subir(archivo)
        if error:
            return _respuesta(False, error)
        imagen = url

    try:
        pub_id = PublicacionRepository.crear(session["usuario_id"], descripcion, imagen)
    except Exception as e:
        print("Error creando publicación:", e)
        return _respuesta(False, "No se pudo crear la publicación", error_code=500)

    # artista y tipo (columnas nuevas)
    try:
        db.table("publicaciones").update({
            "artista": (request.form.get("artista") or "").strip() or None,
            "categoria": (request.form.get("categoria") or "GRAFITI").strip().upper(),
        }).eq("id", pub_id).execute()
    except Exception as e:
        print("Aviso: no se guardó artista/categoria (¿falta correr el SQL?):", e)

    lat, lng = request.form.get("lat"), request.form.get("lng")
    if lat and lng:
        try:
            UbicacionRepository.guardar(pub_id, float(lat), float(lng),
                                        (request.form.get("direccion") or "").strip() or None)
        except Exception as e:
            print("Error guardando ubicación:", e)
            return _respuesta(True, "Publicado, pero no se pudo guardar la ubicación", {"id": pub_id}, ok_code=201)

    return _respuesta(True, "Publicado", {"id": pub_id}, ok_code=201)


@bp.route("/artistas", methods=["GET"])
@api_login_required
def artistas():
    try:
        r = db.table("publicaciones").select("artista").not_.is_("artista", "null").execute()
        return jsonify(sorted({x["artista"] for x in r.data if x.get("artista")}))
    except Exception:
        return jsonify([])


# ---------- perfil ----------

@bp.route("/perfil", methods=["GET"])
@api_login_required
def perfil():
    return jsonify(PerfilService.obtener_perfil(session["usuario_id"]))


@bp.route("/perfil", methods=["POST"])
@api_login_required
def editar_perfil():
    d = _datos()
    nombre = (d.get("nombre_usuario") or "").strip()
    exito, mensaje = PerfilService.actualizar_datos_personales(
        session["usuario_id"], nombre, (d.get("biografia") or "").strip())
    if exito:
        session["nombre_usuario"] = nombre
    return _respuesta(exito, mensaje, {"usuario": _usuario_actual()})


# ---------- foros ----------

@bp.route("/foros", methods=["GET"])
@api_login_required
def foros():
    return jsonify(ForoService.listar_foros())


@bp.route("/foros/<int:foro_id>", methods=["GET"])
@api_login_required
def foro(foro_id):
    f = ForoService.obtener_foro(foro_id)
    if not f:
        return _respuesta(False, "Foro no encontrado", error_code=404)
    return jsonify({"foro": f, "temas": ForoService.obtener_temas(foro_id)})


@bp.route("/foros/<int:foro_id>/temas", methods=["POST"])
@api_login_required
def crear_tema(foro_id):
    d = _datos()
    exito, mensaje, tema_id = ForoService.crear_tema(
        foro_id, session["usuario_id"], d.get("titulo", ""), d.get("contenido", ""))
    return _respuesta(exito, mensaje, {"tema_id": tema_id}, ok_code=201)


@bp.route("/foros/<int:foro_id>/temas/<int:tema_id>", methods=["GET"])
@api_login_required
def tema(foro_id, tema_id):
    t = ForoService.obtener_tema(foro_id, tema_id, session["usuario_id"])
    if not t:
        return _respuesta(False, "Tema no encontrado", error_code=404)
    return jsonify(t)


@bp.route("/foros/<int:foro_id>/temas/<int:tema_id>/respuestas", methods=["POST"])
@api_login_required
def responder(foro_id, tema_id):
    exito, mensaje = ForoService.responder(
        foro_id, tema_id, session["usuario_id"], _datos().get("contenido", ""))
    return _respuesta(exito, mensaje, ok_code=201)


# ---------- eventos (crear) ----------
# La lista, unirse, salir y mis-eventos siguen en features/eventos/routes.py

@bp.route("/eventos/nuevo", methods=["POST"])
@api_login_required
def crear_evento():
    # EventoService.crear lee los campos con .get(), igual que con request.form
    exito, error = EventoService.crear(session["usuario_id"], _datos())
    return _respuesta(exito, "Evento creado" if exito else error, ok_code=201)