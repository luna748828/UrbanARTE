from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.auth_service import AuthService

bp = Blueprint("auth", __name__)

def login_required(f):
    @wraps(f)
    def envoltura(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return envoltura

@bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre_usuario", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        clave = request.form.get("contrasena", "")

        exito, mensaje = AuthService.registrar_usuario(nombre, correo, clave)
        flash(mensaje)
        if exito:
            return redirect(url_for("auth.login"))

    return render_template("registro.html")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        clave = request.form.get("contrasena", "")

        perfil, error = AuthService.iniciar_sesion(correo, clave)
        if error:
            flash(error)
            return render_template("login.html")

        session["usuario_id"] = perfil["id"]
        session["nombre_usuario"] = perfil["nombre_usuario"]
        session["rol"] = perfil["rol"]
        return redirect(url_for("feed.index"))

    return render_template("login.html")

@bp.route("/logout")
def logout():
    session.clear()
    flash("Cerraste sesión.")
    return redirect(url_for("auth.login"))

@bp.route("/cuenta")
@login_required
def cuenta():
    return render_template("cuenta.html")

@bp.route("/cuenta/desactivar", methods=["POST"])
@login_required
def desactivar_cuenta():
    clave = request.form.get("contrasena", "")
    if not clave:
        flash("Escribe tu contraseña para confirmar.")
        return redirect(url_for("auth.cuenta"))

    exito, mensaje = AuthService.dar_de_baja(session["usuario_id"], clave)
    if exito:
        session.clear()
        flash(mensaje)
        return redirect(url_for("auth.login"))
    else:
        flash(mensaje)
        return redirect(url_for("auth.cuenta"))