from flask import Flask
from config import Config
from routes.auth import bp as auth_bp
from routes.feed import bp as feed_bp
from routes.mapa import bp as mapa_bp
from routes.perfil import bp as perfil_bp

app = Flask(__name__)
app.config.from_object(Config)

# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(feed_bp)
app.register_blueprint(mapa_bp)
app.register_blueprint(perfil_bp)

if __name__ == "__main__":
    app.run(debug=True)