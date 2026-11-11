from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from features.auth.routes import login_required
from features.feed.feed_service import FeedService
from data.repositories.publicaciones import PublicacionRepository
from data.repositories.ubicaciones import UbicacionRepository

bp = Blueprint("feed", __name__)


@bp.route("/")
@login_required
def index():
    posts, historias = FeedService.obtener_feed_principal()
    return render_template("feed/index.html", posts=posts, historias=historias)


@bp.route("/feed")
@login_required
def feed():
    posts = FeedService.obtener_solo_posts()
    return render_template("components/_posts.html", posts=posts)


@bp.route("/publicaciones/nueva", methods=["GET", "POST"])
@login_required
def nueva_publicacion():
    if request.method == "POST":
        descripcion = request.form.get("descripcion", "").strip()
        imagen = request.form.get("imagen", "").strip() or None
        direccion = request.form.get("direccion", "").strip() or None
        lat = request.form.get("lat")
        lng = request.form.get("lng")

        if not descripcion:
            flash("Escribe una descripción")
            return render_template("feed/nueva.html")

        try:
            pub_id = PublicacionRepository.crear(session["usuario_id"], descripcion, imagen)
            if lat and lng:
                UbicacionRepository.guardar(pub_id, float(lat), float(lng), direccion)
        except Exception as e:
            print("Error creando publicación:", e)
            flash("No se pudo crear la publicación")
            return render_template("feed/nueva.html")

        return redirect(url_for("feed.index"))

    return render_template("feed/nueva.html")