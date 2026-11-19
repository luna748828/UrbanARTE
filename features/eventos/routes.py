from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from features.auth.routes import login_required
from features.eventos.eventos_service import EventoService
from flask import jsonify
from features.eventos.asistencia_service import AsistenciaService

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
@bp.route("/api/eventos/<int:evento_id>/unirse", methods=["POST"])
@login_required
def unirse(evento_id):
    ok, mensaje, codigo = AsistenciaService.unirse(evento_id, session["usuario_id"])
    return jsonify({"ok": ok, "mensaje": mensaje}), codigo


@bp.route("/api/eventos/<int:evento_id>/unirse", methods=["DELETE"])
@login_required
def salir(evento_id):
    ok, mensaje, codigo = AsistenciaService.salir(evento_id, session["usuario_id"])
    return jsonify({"ok": ok, "mensaje": mensaje}), codigo


@bp.route("/api/eventos/mis-eventos", methods=["GET"])
@login_required
def mis_eventos():
    return jsonify(AsistenciaService.mis_eventos(session["usuario_id"]))