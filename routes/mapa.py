from flask import Blueprint, render_template, request, jsonify
from services.feed_service import FeedService

bp = Blueprint("mapa", __name__)

@bp.route("/mapa")
def mapa():
    pendientes = FeedService.obtener_pendientes_mapa()
    return render_template("mapa.html", pendientes=pendientes)

@bp.route("/api/ubicaciones")
def listar_ubicaciones():
    ubicaciones = FeedService.obtener_todas_ubicaciones()
    return jsonify(ubicaciones)

@bp.route("/api/ubicaciones", methods=["POST"])
def guardar_ubicacion():
    d = request.get_json()
    try:
        FeedService.crear_ubicacion(d)
        return jsonify({"ok": True})
    except Exception as e:
        print("Error guardando ubicación:", e)
        return jsonify({"ok": False, "error": str(e)}), 400