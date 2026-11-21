from flask import Blueprint, request, session, jsonify
from data.repositories.publicaciones import PublicacionRepository
from data.repositories.ubicaciones import UbicacionRepository

bp = Blueprint("feed", __name__)


def _validar_texto(descripcion):
    if not descripcion or len(descripcion) < 3:
        return "La descripción debe tener al menos 3 caracteres."
    if len(descripcion) > 1000:
        return "La descripción no puede superar los 1000 caracteres."
    return None


@bp.route("/api/publicaciones", methods=["GET", "POST"])
def api_publicaciones():
    # 7.4 Lectura y despliegue del feed
    if request.method == "GET":
        posts = PublicacionRepository.obtener_recientes()
        return jsonify(posts), 200

    # 7.2 y 7.3 Creación y validación de publicación
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return jsonify({"error": "Debes iniciar sesión para publicar."}), 401

    if request.content_type and "multipart/form-data" in request.content_type:
        descripcion = request.form.get("descripcion", "").strip()
        categoria = request.form.get("categoria", "GRAFITI").strip()
        artista_propio = request.form.get("artista_propio")
        artista = session.get("usuario_nombre") if artista_propio else (request.form.get("artista", "").strip() or None)
        imagen_url = request.form.get("imagen", "").strip() or None
        archivo = request.files.get("imagen_archivo") or request.files.get("archivo")
        direccion = request.form.get("direccion", "").strip() or None
        lat = request.form.get("lat")
        lng = request.form.get("lng")
    else:
        data = request.get_json(silent=True) or {}
        descripcion = (data.get("descripcion") or "").strip()
        categoria = (data.get("categoria") or "GRAFITI").strip()
        artista = (data.get("artista") or "").strip() or None
        imagen_url = (data.get("imagen") or "").strip() or None
        archivo = None
        direccion = (data.get("direccion") or "").strip() or None
        lat = data.get("lat")
        lng = data.get("lng")

    error_texto = _validar_texto(descripcion)
    if error_texto:
        return jsonify({"error": error_texto}), 400

    if archivo and archivo.filename:
        imagen_url, error_img = PublicacionRepository.subir_imagen(archivo)
        if error_img:
            return jsonify({"error": error_img}), 400

    try:
        pub_id = PublicacionRepository.crear(
            usuario_id=usuario_id,
            descripcion=descripcion,
            imagen=imagen_url,
            categoria=categoria,
            artista=artista,
        )
        if lat and lng:
            UbicacionRepository.guardar(pub_id, float(lat), float(lng), direccion)
    except Exception as e:
        print("Error creando publicación:", e)
        return jsonify({"error": "Error al guardar la publicación."}), 500

    return jsonify({"id": pub_id, "mensaje": "Obra publicada con éxito"}), 201


@bp.route("/api/mis-publicaciones", methods=["GET"])
def api_mis_publicaciones():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401
    pubs = PublicacionRepository.obtener_por_usuario(usuario_id)
    return jsonify(pubs), 200


@bp.route("/api/publicaciones/<int:pub_id>", methods=["PUT", "DELETE"])
def api_publicacion_detalle(pub_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return jsonify({"error": "No autenticado"}), 401

    # 7.6 Eliminación de publicaciones
    if request.method == "DELETE":
        ok = PublicacionRepository.eliminar(pub_id, usuario_id)
        if not ok:
            return jsonify({"error": "No tienes permiso o la publicación no existe."}), 403
        return jsonify({"mensaje": "Publicación eliminada"}), 200

    # 7.5 Edición de publicaciones
    if request.content_type and "multipart/form-data" in request.content_type:
        descripcion = request.form.get("descripcion", "").strip()
        categoria = request.form.get("categoria")
        artista = request.form.get("artista")
        imagen_url = request.form.get("imagen", "").strip() or None
        archivo = request.files.get("imagen_archivo") or request.files.get("archivo")
    else:
        data = request.get_json(silent=True) or {}
        descripcion = (data.get("descripcion") or "").strip()
        categoria = data.get("categoria")
        artista = data.get("artista")
        imagen_url = (data.get("imagen") or "").strip() or None
        archivo = None

    error_texto = _validar_texto(descripcion)
    if error_texto:
        return jsonify({"error": error_texto}), 400

    if archivo and archivo.filename:
        imagen_url, error_img = PublicacionRepository.subir_imagen(archivo)
        if error_img:
            return jsonify({"error": error_img}), 400

    ok = PublicacionRepository.actualizar(
        publicacion_id=pub_id,
        usuario_id=usuario_id,
        descripcion=descripcion,
        imagen=imagen_url,
        categoria=categoria,
        artista=artista,
    )
    if not ok:
        return jsonify({"error": "No tienes permiso o la publicación no existe."}), 403

    return jsonify({"mensaje": "Publicación actualizada"}), 200