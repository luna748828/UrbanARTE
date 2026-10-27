from flask import Flask, render_template

app = Flask(__name__)

# Datos de ejemplo (luego se reemplazan por la base de datos)
publicaciones = [
    {"autor": "mural_bogota", "lugar": "La Candelaria", "texto": "Nuevo mural terminado 🎨", "color": "#e1306c"},
    {"autor": "graffiti_lab", "lugar": "Chapinero", "texto": "Intervención de fin de semana", "color": "#833ab4"},
    {"autor": "arte_calle", "lugar": "Teusaquillo", "texto": "Stencil en proceso", "color": "#fd1d1d"},
]
historias = ["mural_bogota", "graffiti_lab", "arte_calle", "colectivo_x", "tags_co"]

@app.route("/")
def index():
    return render_template("index.html", posts=publicaciones, historias=historias)

if __name__ == "__main__":
    app.run(debug=True)