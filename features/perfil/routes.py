from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from features.auth.routes import login_required
from features.perfil.perfil_service import PerfilService

bp = Blueprint("perfil", __name__, url_prefix="/cuenta")

@bp.route("/")
@login_required
def ver_perfil():
    usuario_id = session.get("usuario_id")
    perfil = PerfilService.obtener_perfil(usuario_id)
    return render_template("perfil/cuenta.html", perfil=perfil)

@bp.route("/editar", methods=["POST"])
@login_required
def editar_perfil():
    usuario_id = session.get("usuario_id")
    nombre_usuario = request.form.get("nombre_usuario", "").strip()
    biografia = request.form.get("biografia", "").strip()

    exito, mensaje = PerfilService.actualizar_datos_personales(usuario_id, nombre_usuario, biografia)
    flash(mensaje)
    if exito:
        session["usuario_nombre"] = nombre_usuario
    return redirect(url_for("perfil.ver_perfil"))

@bp.route("/cambiar-clave", methods=["POST"])
@login_required
def cambiar_clave():
    nueva_clave = request.form.get("nueva_clave", "").strip()
    exito, mensaje = PerfilService.cambiar_contrasena(nueva_clave)
    flash(mensaje)
    return redirect(url_for("perfil.ver_perfil"))