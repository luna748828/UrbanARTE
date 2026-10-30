import os
from flask import Flask, render_template
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
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


if __name__ == "__main__":
    app.run(debug=True)