import os
import sys

# Agregar la raíz del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config

# Importar los blueprints según las subcarpetas de features
from features.auth.routes import bp as auth_bp
from features.feed.routes import bp as feed_bp
from features.mapa.routes import bp as mapa_bp
from features.perfil.routes import bp as perfil_bp
from features.foros.routes import bp as foros_bp
from features.eventos.routes import bp as eventos_bp

app = Flask(__name__)
app.config.from_object(Config)

# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(feed_bp)
app.register_blueprint(mapa_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(foros_bp)
app.register_blueprint(eventos_bp)

if __name__ == "__main__":
    app.run(debug=True)