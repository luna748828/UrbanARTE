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

def _listar_publicaciones(usuario_id=None):
    # Se lee la tabla directo para tener siempre los mismos nombres de campo.
    # Se prueba con las columnas nuevas y, si aún no existen, con menos.
    campos = "id, usuario_id, descripcion, imagen, fecha_publicacion"
    intentos = [
        campos + ", artista, artista_propio, categoria, usuarios(nombre_usuario, tipo_artista, foto_url)",
        campos + ", artista, categoria, usuarios(nombre_usuario, tipo_artista, foto_url)",
        campos + ", artista, categoria, usuarios(nombre_usuario)",
        campos + ", usuarios(nombre_usuario)",
    ]
    filas = None
    for sel in intentos:
        try:
            q = db.table("publicaciones").select(sel)
            if usuario_id:
                q = q.eq("usuario_id", usuario_id)
            filas = q.order("fecha_publicacion", desc=True).execute().data
            break
        except Exception as e:
            print("Aviso: faltan columnas nuevas (corre el SQL):", e)
    filas = filas or []

    ubic = (db.table("ubicaciones")
            .select("publicacion_id, direccion_aprox, latitud, longitud").execute().data)
    ubicaciones = {u["publicacion_id"]: u for u in (ubic or [])}

    resultado = []
    for p in filas:
        p = dict(p)
        p["categoria"] = p.get("categoria") or "GRAFITI"
        u = ubicaciones.get(p["id"])
        if u:
            p["latitud"] = u.get("latitud")
            p["longitud"] = u.get("longitud")
            p["direccion_aprox"] = u.get("direccion_aprox")
        resultado.append(p)
    return resultado


@bp.route("/publicaciones", methods=["GET"])
@api_login_required
def publicaciones():
    return jsonify(_listar_publicaciones())


@bp.route("/mis-publicaciones", methods=["GET"])
@api_login_required
def mis_publicaciones():
    return jsonify(_listar_publicaciones(session["usuario_id"]))


@bp.route("/publicaciones/<int:publicacion_id>", methods=["PUT"])
@api_login_required
def editar_publicacion(publicacion_id):
    if not PublicacionRepository.es_del_usuario(publicacion_id, session["usuario_id"]):
        return _respuesta(False, "Solo puedes editar tus propias publicaciones", error_code=403)

    descripcion = request.form.get("descripcion", "").strip()
    if not descripcion:
        return _respuesta(False, "Escribe una descripción")
    cambios = {"descripcion": descripcion}

    archivo = request.files.get("imagen_archivo")
    if archivo and archivo.filename:
        subir = getattr(PublicacionRepository, "subir_imagen", None)
        if not subir:
            return _respuesta(False, "Falta la función subir_imagen en PublicacionRepository", error_code=500)
        url, error = subir(archivo)
        if error:
            return _respuesta(False, error)
        cambios["imagen"] = url

    try:
        db.table("publicaciones").update(cambios).eq("id", publicacion_id).execute()
    except Exception as e:
        print("Error editando publicación:", e)
        return _respuesta(False, "No se pudo guardar", error_code=500)

    propio = bool(request.form.get("artista_propio"))
    artista = session.get("nombre_usuario") if propio else (
        " ".join((request.form.get("artista") or "").split()).lstrip("@").strip() or None)
    extra = {"artista": artista, "categoria": (request.form.get("categoria") or "GRAFITI").strip().upper()}
    try:
        db.table("publicaciones").update({**extra, "artista_propio": propio}).eq("id", publicacion_id).execute()
    except Exception as e:
        print("Aviso: no se guardó artista_propio (¿falta el SQL?):", e)
        try:
            db.table("publicaciones").update(extra).eq("id", publicacion_id).execute()
        except Exception as e2:
            print("Aviso: no se guardó artista/categoria (¿falta el SQL?):", e2)

    if "direccion" in request.form:
        try:
            db.table("ubicaciones").update(
                {"direccion_aprox": (request.form.get("direccion") or "").strip() or None}
            ).eq("publicacion_id", publicacion_id).execute()
        except Exception as e:
            print("Aviso: no se guardó la dirección:", e)

    return _respuesta(True, "Publicación actualizada")


@bp.route("/publicaciones/<int:publicacion_id>", methods=["DELETE"])
@api_login_required
def eliminar_publicacion(publicacion_id):
    es_admin = session.get("rol") == "administrador"
    if not es_admin and not PublicacionRepository.es_del_usuario(publicacion_id, session["usuario_id"]):
        return _respuesta(False, "Solo puedes eliminar tus propias publicaciones", error_code=403)
    try:
        db.table("ubicaciones").delete().eq("publicacion_id", publicacion_id).execute()
        db.table("publicaciones").delete().eq("id", publicacion_id).execute()
    except Exception as e:
        print("Error eliminando publicación:", e)
        return _respuesta(False, "No se pudo eliminar la publicación", error_code=500)
    return _respuesta(True, "Publicación eliminada")


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
    propio = bool(request.form.get("artista_propio"))
    if propio:
        artista = session.get("nombre_usuario")
    else:
        artista = " ".join((request.form.get("artista") or "").split()).lstrip("@").strip() or None
    extra = {"artista": artista, "categoria": (request.form.get("categoria") or "GRAFITI").strip().upper()}
    try:
        db.table("publicaciones").update({**extra, "artista_propio": propio}).eq("id", pub_id).execute()
    except Exception as e:
        print("Aviso: no se guardó artista_propio (¿falta correr el SQL?):", e)
        try:
            db.table("publicaciones").update(extra).eq("id", pub_id).execute()
        except Exception as e2:
            print("Aviso: no se guardó artista/categoria (¿falta correr el SQL?):", e2)

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

def _extras_usuario(uid):
    try:
        r = db.table("usuarios").select("tipo_artista, foto_url").eq("id", uid).execute()
        return r.data[0] if r.data else {}
    except Exception as e:
        print("Aviso: faltan columnas tipo_artista/foto_url (corre el SQL):", e)
        return {}


def _registrar_tipo(nombre):
    """Devuelve (nombre_guardado, error). Si el tipo no existe, lo agrega a la lista."""
    nombre = " ".join((nombre or "").split())
    if len(nombre) < 2 or len(nombre) > 40:
        return None, "El tipo de artista debe tener entre 2 y 40 caracteres"
    nombre = nombre[0].upper() + nombre[1:]
    existentes = [x["nombre"] for x in db.table("tipos_artista").select("nombre").execute().data]
    for t in existentes:
        if t.lower() == nombre.lower():
            return t, None
    db.table("tipos_artista").insert({"nombre": nombre}).execute()
    return nombre, None


@bp.route("/tipos-artista", methods=["GET"])
@api_login_required
def tipos_artista():
    try:
        r = db.table("tipos_artista").select("nombre").order("nombre").execute()
        return jsonify([x["nombre"] for x in r.data])
    except Exception as e:
        print("Aviso: falta la tabla tipos_artista (corre el SQL):", e)
        return jsonify([])


@bp.route("/perfil", methods=["GET"])
@api_login_required
def perfil():
    datos = dict(PerfilService.obtener_perfil(session["usuario_id"]) or {})
    datos.update(_extras_usuario(session["usuario_id"]))
    return jsonify(datos)


@bp.route("/perfil", methods=["POST"])
@api_login_required
def editar_perfil():
    d = _datos()
    nombre = (d.get("nombre_usuario") or "").strip()
    exito, mensaje = PerfilService.actualizar_datos_personales(
        session["usuario_id"], nombre, (d.get("biografia") or "").strip())
    if not exito:
        return _respuesta(False, mensaje)
    session["nombre_usuario"] = nombre

    if d.get("tipo_artista") is not None:
        tipo = (d.get("tipo_artista") or "").strip()
        try:
            if tipo:
                tipo, error = _registrar_tipo(tipo)
                if error:
                    return _respuesta(False, error)
            db.table("usuarios").update({"tipo_artista": tipo or None}).eq("id", session["usuario_id"]).execute()
        except Exception as e:
            print("Error guardando tipo de artista:", e)
            return _respuesta(False, "No se pudo guardar el tipo de artista", error_code=500)

    return _respuesta(True, mensaje, {"usuario": _usuario_actual()})


@bp.route("/perfil/foto", methods=["POST"])
@api_login_required
def foto_perfil():
    archivo = request.files.get("foto")
    if not archivo or not archivo.filename:
        return _respuesta(False, "Elige una foto")
    subir = getattr(PublicacionRepository, "subir_imagen", None)
    if not subir:
        return _respuesta(False, "Falta la función subir_imagen en PublicacionRepository", error_code=500)
    url, error = subir(archivo)
    if error:
        return _respuesta(False, error)
    try:
        db.table("usuarios").update({"foto_url": url}).eq("id", session["usuario_id"]).execute()
    except Exception as e:
        print("Error guardando foto de perfil:", e)
        return _respuesta(False, "No se pudo guardar la foto", error_code=500)
    return _respuesta(True, "Foto actualizada", {"foto_url": url})


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


# ---------- foros: editar y borrar ----------

@bp.route("/foros/<int:foro_id>/temas/<int:tema_id>", methods=["PUT"])
@api_login_required
def editar_tema(foro_id, tema_id):
    d = _datos()
    exito, mensaje = ForoService.editar_tema(
        foro_id, tema_id, session["usuario_id"], d.get("titulo", ""), d.get("contenido", ""))
    return _respuesta(exito, mensaje, error_code=403)


@bp.route("/foros/<int:foro_id>/temas/<int:tema_id>", methods=["DELETE"])
@api_login_required
def eliminar_tema(foro_id, tema_id):
    exito, mensaje = ForoService.eliminar_tema(foro_id, tema_id, session["usuario_id"])
    return _respuesta(exito, mensaje, error_code=403)


@bp.route("/foros/<int:foro_id>/temas/<int:tema_id>/respuestas/<int:respuesta_id>", methods=["PUT"])
@api_login_required
def editar_respuesta(foro_id, tema_id, respuesta_id):
    exito, mensaje = ForoService.editar_respuesta(
        foro_id, tema_id, respuesta_id, session["usuario_id"], _datos().get("contenido", ""))
    return _respuesta(exito, mensaje, error_code=403)


@bp.route("/foros/<int:foro_id>/temas/<int:tema_id>/respuestas/<int:respuesta_id>", methods=["DELETE"])
@api_login_required
def eliminar_respuesta(foro_id, tema_id, respuesta_id):
    exito, mensaje = ForoService.eliminar_respuesta(foro_id, tema_id, respuesta_id, session["usuario_id"])
    return _respuesta(exito, mensaje, error_code=403)


# ---------- cuenta ----------

@bp.route("/cuenta/clave", methods=["POST"])
@api_login_required
def cambiar_clave():
    exito, mensaje = PerfilService.cambiar_contrasena((_datos().get("nueva_clave") or "").strip())
    return _respuesta(exito, mensaje)


@bp.route("/cuenta/desactivar", methods=["POST"])
@api_login_required
def desactivar_cuenta():
    clave = _datos().get("contrasena") or ""
    if not clave:
        return _respuesta(False, "Escribe tu contraseña para confirmar.")
    exito, mensaje = AuthService.dar_de_baja(session["usuario_id"], clave)
    if exito:
        session.clear()
    return _respuesta(exito, mensaje)