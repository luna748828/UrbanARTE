from flask import Blueprint, render_template, request, jsonify
from features.auth.auth import login_required
from data.repositories.ubicaciones import UbicacionRepository
from data.repositories.publicaciones import PublicacionRepository

bp = Blueprint("mapa", __name__)


@bp.route("/mapa")
@login_required
def index():
    pendientes = PublicacionRepository.obtener_pendientes_ubicacion()
    return render_template("mapa/mapa.html", pendientes=pendientes)


@bp.route("/api/ubicaciones", methods=["GET"])
@login_required
def listar():
    return jsonify(UbicacionRepository.obtener_todas())


@bp.route("/api/ubicaciones", methods=["POST"])
@login_required
def crear():
    datos = request.get_json(silent=True) or {}
    publicacion_id = datos.get("publicacion_id")
    direccion = (datos.get("direccion_aprox") or "").strip() or None

    try:
        latitud = float(datos.get("latitud"))
        longitud = float(datos.get("longitud"))
    except (TypeError, ValueError):
        return jsonify({"error": "Coordenadas inválidas"}), 400

    if not publicacion_id:
        return jsonify({"error": "Elige una publicación"}), 400
    if not (-90 <= latitud <= 90 and -180 <= longitud <= 180):
        return jsonify({"error": "Coordenadas fuera de rango"}), 400

    try:
        res = UbicacionRepository.guardar(publicacion_id, latitud, longitud, direccion)
    except Exception as e:
        print("Error guardando ubicación:", e)
        return jsonify({"error": "No se pudo guardar"}), 500

    return jsonify(res.data), 201