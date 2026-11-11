from flask import Blueprint, render_template, request, jsonify, session
from features.auth.routes import login_required
from data.repositories.ubicaciones import UbicacionRepository
from data.repositories.publicaciones import PublicacionRepository

bp = Blueprint("mapa", __name__)


@bp.route("/mapa")
@login_required
def index():
    pendientes = PublicacionRepository.obtener_pendientes_de_usuario(session["usuario_id"])
    return render_template("mapa/mapa.html", pendientes=pendientes)


@bp.route("/api/ubicaciones", methods=["GET"])
@login_required
def listar():
    return jsonify(UbicacionRepository.obtener_todas())


@bp.route("/api/ubicaciones", methods=["POST"])
@login_required
def crear():
    datos = request.get_json(silent=True) or {}
    direccion = (datos.get("direccion_aprox") or "").strip() or None

    try:
        publicacion_id = int(datos.get("publicacion_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Elige una publicación"}), 400

    try:
        latitud = float(datos.get("latitud"))
        longitud = float(datos.get("longitud"))
    except (TypeError, ValueError):
        return jsonify({"error": "Coordenadas inválidas"}), 400

    if not (-90 <= latitud <= 90 and -180 <= longitud <= 180):
        return jsonify({"error": "Coordenadas fuera de rango"}), 400

    # Solo se puede ubicar una publicación propia
    if not PublicacionRepository.es_del_usuario(publicacion_id, session["usuario_id"]):
        return jsonify({"error": "Solo puedes ubicar tus propias publicaciones"}), 403

    try:
        res = UbicacionRepository.guardar(publicacion_id, latitud, longitud, direccion)
    except Exception as e:
        print("Error guardando ubicación:", e)
        return jsonify({"error": "No se pudo guardar"}), 500

    return jsonify(res.data), 201