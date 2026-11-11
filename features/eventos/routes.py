from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from features.auth.routes import login_required
from features.eventos.eventos_service import EventoService

bp = Blueprint("eventos", __name__)


@bp.route("/eventos")
@login_required
def lista():
    eventos = EventoService.listar_proximos()
    return render_template("eventos/lista.html", eventos=eventos)


@bp.route("/eventos/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    if request.method == "POST":
        ok, error = EventoService.crear(session["usuario_id"], request.form)
        if ok:
            flash("Evento creado")
            return redirect(url_for("eventos.lista"))
        flash(error)
        return render_template("eventos/eventos.html", form=request.form)
    return render_template("eventos/eventos.html", form={})