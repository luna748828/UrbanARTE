import os
from auth import bp as auth_bp               
from flask import Flask, render_template, request, jsonify
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.register_blueprint(auth_bp)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Colores "de pintura" que se reparten entre las publicaciones
PALETA = ["#ff3d6e", "#ffb703", "#2ec4b6", "#7b5cff", "#ff7a1a", "#3ddc97"]


def cargar_posts():
    try:
        res = (
            supabase.table("publicaciones")
            .select("id, descripcion, imagen, fecha_publicacion, "
                    "usuarios(nombre_usuario), ubicaciones(direccion_aprox)")
            .order("fecha_publicacion", desc=True)
            .limit(20)
            .execute()
        )
    except Exception as e:
        print("Error cargando publicaciones:", e)
        return []

    posts = []
    for r in res.data:
        autor = r.get("usuarios") or {}
        ubic = r.get("ubicaciones") or {}
        if isinstance(ubic, list):
            ubic = ubic[0] if ubic else {}
        posts.append({
            "autor": autor.get("nombre_usuario", "anónimo"),
            "lugar": ubic.get("direccion_aprox", ""),
            "texto": r["descripcion"] or "",
            "imagen_url": r["imagen"],
            "acento": PALETA[r["id"] % len(PALETA)],
        })
    return posts


def cargar_historias():
    try:
        res = (
            supabase.table("usuarios")
            .select("nombre_usuario")
            .order("creado_en", desc=True)
            .limit(8)
            .execute()
        )
        return [u["nombre_usuario"] for u in res.data]
    except Exception as e:
        print("Error cargando historias:", e)
        return []


@app.route("/")
def index():
    return render_template("index.html", posts=cargar_posts(), historias=cargar_historias())


@app.route("/feed")  # lo usa la actualización automática cada 15 s
def feed():
    return render_template("_posts.html", posts=cargar_posts())

@app.route("/mapa")
def mapa():
    res = (
        supabase.table("publicaciones")
        .select("id, descripcion, usuarios(nombre_usuario), ubicaciones(id)")
        .order("fecha_publicacion", desc=True)
        .execute()
    )
    pendientes = [
        {
            "id": r["id"],
            "titulo": f'{(r.get("usuarios") or {}).get("nombre_usuario", "anónimo")}: {(r["descripcion"] or "sin descripción")[:40]}',
        }
        for r in res.data
        if not r.get("ubicaciones")  # solo las que aún no tienen ubicación
    ]
    return render_template("mapa.html", pendientes=pendientes)


@app.route("/api/ubicaciones")
def listar_ubicaciones():
    res = (
        supabase.table("ubicaciones")
        .select("direccion_aprox, latitud, longitud, "
                "publicaciones(descripcion, imagen, usuarios(nombre_usuario))")
        .execute()
    )
    return jsonify(res.data)


@app.route("/api/ubicaciones", methods=["POST"])
def guardar_ubicacion():
    d = request.get_json()
    try:
        supabase.table("ubicaciones").insert({
            "publicacion_id": d["publicacion_id"],
            "direccion_aprox": d.get("direccion_aprox"),
            "latitud": d["latitud"],
            "longitud": d["longitud"],
        }).execute()
        return jsonify({"ok": True})
    except Exception as e:
        print("Error guardando ubicación:", e)
        return jsonify({"ok": False, "error": str(e)}), 400
    
if __name__ == "__main__":
    app.run(debug=True)