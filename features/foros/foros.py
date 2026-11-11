from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from features.auth.auth import login_required
from features.foros.foros_service import ForoService

bp = Blueprint("foros", __name__, url_prefix="/foros")


def _aviso(exito, mensaje):
    # La categoría deja mostrar los avisos buenos en verde y los malos en rojo
    flash(mensaje, "ok" if exito else "error")


@bp.route("/")
@login_required
def listar():
    return render_template("foros/lista.html", foros=ForoService.listar_foros())


@bp.route("/<int:foro_id>")
@login_required
def ver_foro(foro_id):
    foro = ForoService.obtener_foro(foro_id)
    if not foro:
        abort(404)
    return render_template("foros/foro.html", foro=foro, temas=ForoService.obtener_temas(foro_id))


@bp.route("/<int:foro_id>/temas", methods=["POST"])
@login_required
def crear_tema(foro_id):
    foro = ForoService.obtener_foro(foro_id)
    if not foro:
        abort(404)

    titulo = request.form.get("titulo", "")
    contenido = request.form.get("contenido", "")
    exito, mensaje, tema_id = ForoService.crear_tema(foro_id, session["usuario_id"], titulo, contenido)
    _aviso(exito, mensaje)
    if exito:
        return redirect(url_for("foros.ver_tema", foro_id=foro_id, tema_id=tema_id))

    # Si algo falló, se vuelve a mostrar el foro con lo que la persona ya había escrito
    return render_template("foros/foro.html", foro=foro, temas=ForoService.obtener_temas(foro_id),
                           titulo=titulo, contenido=contenido)


@bp.route("/<int:foro_id>/temas/<int:tema_id>")
@login_required
def ver_tema(foro_id, tema_id):
    foro = ForoService.obtener_foro(foro_id)
    tema = ForoService.obtener_tema(foro_id, tema_id, session["usuario_id"])
    if not foro or not tema:
        abort(404)
    return render_template("foros/tema.html", foro=foro, tema=tema)


@bp.route("/<int:foro_id>/temas/<int:tema_id>/editar", methods=["POST"])
@login_required
def editar_tema(foro_id, tema_id):
    exito, mensaje = ForoService.editar_tema(
        foro_id, tema_id, session["usuario_id"],
        request.form.get("titulo", ""), request.form.get("contenido", ""))
    _aviso(exito, mensaje)
    return redirect(url_for("foros.ver_tema", foro_id=foro_id, tema_id=tema_id))


@bp.route("/<int:foro_id>/temas/<int:tema_id>/eliminar", methods=["POST"])
@login_required
def eliminar_tema(foro_id, tema_id):
    exito, mensaje = ForoService.eliminar_tema(foro_id, tema_id, session["usuario_id"])
    _aviso(exito, mensaje)
    if exito:
        return redirect(url_for("foros.ver_foro", foro_id=foro_id))
    return redirect(url_for("foros.ver_tema", foro_id=foro_id, tema_id=tema_id))


@bp.route("/<int:foro_id>/temas/<int:tema_id>/respuestas", methods=["POST"])
@login_required
def responder(foro_id, tema_id):
    foro = ForoService.obtener_foro(foro_id)
    tema = ForoService.obtener_tema(foro_id, tema_id, session["usuario_id"])
    if not foro or not tema:
        abort(404)

    contenido = request.form.get("contenido", "")
    exito, mensaje = ForoService.responder(foro_id, tema_id, session["usuario_id"], contenido)
    _aviso(exito, mensaje)
    if exito:
        return redirect(url_for("foros.ver_tema", foro_id=foro_id, tema_id=tema_id))

    return render_template("foros/tema.html", foro=foro, tema=tema, borrador=contenido)


@bp.route("/<int:foro_id>/temas/<int:tema_id>/respuestas/<int:respuesta_id>/editar", methods=["POST"])
@login_required
def editar_respuesta(foro_id, tema_id, respuesta_id):
    exito, mensaje = ForoService.editar_respuesta(
        foro_id, tema_id, respuesta_id, session["usuario_id"], request.form.get("contenido", ""))
    _aviso(exito, mensaje)
    return redirect(url_for("foros.ver_tema", foro_id=foro_id, tema_id=tema_id))


@bp.route("/<int:foro_id>/temas/<int:tema_id>/respuestas/<int:respuesta_id>/eliminar", methods=["POST"])
@login_required
def eliminar_respuesta(foro_id, tema_id, respuesta_id):
    exito, mensaje = ForoService.eliminar_respuesta(foro_id, tema_id, respuesta_id, session["usuario_id"])
    _aviso(exito, mensaje)
    return redirect(url_for("foros.ver_tema", foro_id=foro_id, tema_id=tema_id))