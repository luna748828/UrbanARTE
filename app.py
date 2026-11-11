import os
import sys

# Agregar la raíz del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config

# Importar los blueprints según las subcarpetas de features
<<<<<<< HEAD
from features.auth.routes import bp as auth_bp
from features.feed.routes import bp as feed_bp
from features.mapa.routes import bp as mapa_bp
from features.perfil.routes import bp as perfil_bp
from features.foros.routes import bp as foros_bp
from features.eventos.routes import bp as eventos_bp
=======
from features.auth.auth import bp as auth_bp
from features.feed.feed import bp as feed_bp
from features.mapa.mapa import bp as mapa_bp
from features.perfil.perfil import bp as perfil_bp
from features.foros.foros import bp as foros_bp
>>>>>>> 012db9a6ef099d1a7cbd5fd9bfa670233c8c4768

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