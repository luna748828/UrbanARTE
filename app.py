from flask import Flask
from config import Config
from features.auth.auth import bp as auth_bp
from features.feed.feed import bp as feed_bp
from features.mapa.mapa import bp as mapa_bp
from features.perfil.perfil import bp as perfil_bp

app = Flask(__name__)
app.config.from_object(Config)

# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(feed_bp)
app.register_blueprint(mapa_bp)
app.register_blueprint(perfil_bp)

if __name__ == "__main__":
    app.run(debug=True)