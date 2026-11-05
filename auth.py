import os, re
from functools import wraps
from dotenv import load_dotenv
from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, flash)
from supabase import create_client

load_dotenv()

bp = Blueprint("auth", __name__)

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

# Cliente solo para leer y escribir tablas (no se usa para iniciar sesión)
datos = create_client(URL, KEY)


def cliente_auth():
    # Uno nuevo por cada registro o login, para que la sesión de una
    # persona nunca se mezcle con la de otra.
    return create_client(URL, KEY)


def contrasena_valida(clave):  # RNF3: 8+ caracteres, un número y un símbolo
    return (len(clave) >= 8 and re.search(r"\d", clave)
            and re.search(r"[^\w\s]", clave))


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

        if not re.fullmatch(r"[A-Za-z0-9_]{3,30}", nombre):
            flash("El usuario debe tener de 3 a 30 caracteres: letras, números o guion bajo.")
            return render_template("registro.html")
        if not contrasena_valida(clave):
            flash("La contraseña necesita mínimo 8 caracteres, un número y un símbolo.")
            return render_template("registro.html")
        if datos.table("usuarios").select("id").eq("nombre_usuario", nombre).execute().data:
            flash("Ese nombre de usuario ya está en uso.")
            return render_template("registro.html")

        try:
            r = cliente_auth().auth.sign_up({"email": correo, "password": clave})
        except Exception as e:
            flash(f"No se pudo crear la cuenta: {e}")
            return render_template("registro.html")

        # Si el correo ya existía, Supabase no da error pero devuelve un usuario sin identidades
        if not r.user or not r.user.identities:
            flash("Ese correo ya está registrado.")
            return render_template("registro.html")

        try:
            datos.table("usuarios").insert({
                "id": r.user.id,          # mismo id que la cuenta de acceso
                "nombre_usuario": nombre,
                "correo": correo,
                "rol": "artista",
            }).execute()
        except Exception as e:
            flash(f"La cuenta se creó, pero falló el perfil: {e}")
            return render_template("registro.html")

        flash("Cuenta creada. Revisa tu correo para confirmarla.")
        return redirect(url_for("auth.login"))
    return render_template("registro.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        clave = request.form.get("contrasena", "")

        try:
            r = cliente_auth().auth.sign_in_with_password(
                {"email": correo, "password": clave})
        except Exception as e:
            if "not confirmed" in str(e).lower():
                flash("Confirma tu correo antes de iniciar sesión.")
            else:
                flash("Correo o contraseña incorrectos.")
            return render_template("login.html")

        perfil = (datos.table("usuarios").select("id, nombre_usuario, rol, activo")
                  .eq("id", r.user.id).execute().data)
        if not perfil:
            flash("Tu cuenta no tiene perfil. Avisa al equipo.")
            return render_template("login.html")

        # 5.6: las cuentas desactivadas no pueden entrar
        if perfil[0].get("activo") is False:
            flash("Esta cuenta está desactivada.")
            return render_template("login.html")

        session["usuario_id"] = perfil[0]["id"]
        session["nombre_usuario"] = perfil[0]["nombre_usuario"]
        session["rol"] = perfil[0]["rol"]
        return redirect(url_for("index"))
    return render_template("login.html")


# 5.5: cierre de sesión
@bp.route("/logout")
def logout():
    session.clear()
    flash("Cerraste sesión.")
    return redirect(url_for("auth.login"))


# Página de la cuenta: desde aquí se cierra sesión o se desactiva la cuenta
@bp.route("/cuenta")
@login_required
def cuenta():
    return render_template("cuenta.html")


# 5.6: desactivar la cuenta (HU12). Pide la contraseña para confirmar.
@bp.route("/cuenta/desactivar", methods=["POST"])
@login_required
def desactivar_cuenta():
    clave = request.form.get("contrasena", "")
    if not clave:
        flash("Escribe tu contraseña para confirmar.")
        return redirect(url_for("auth.cuenta"))

    perfil = (datos.table("usuarios").select("correo")
              .eq("id", session["usuario_id"]).execute().data)
    if not perfil:
        session.clear()
        return redirect(url_for("auth.login"))

    # La contraseña se comprueba iniciando sesión otra vez con un cliente nuevo
    try:
        cliente_auth().auth.sign_in_with_password(
            {"email": perfil[0]["correo"], "password": clave})
    except Exception:
        flash("La contraseña es incorrecta.")
        return redirect(url_for("auth.cuenta"))

    try:
        (datos.table("usuarios").update({"activo": False})
         .eq("id", session["usuario_id"]).execute())
    except Exception as e:
        flash(f"No se pudo desactivar la cuenta: {e}")
        return redirect(url_for("auth.cuenta"))

    session.clear()
    flash("Tu cuenta fue desactivada.")
    return redirect(url_for("auth.login"))      