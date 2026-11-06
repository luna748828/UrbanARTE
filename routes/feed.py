from flask import Blueprint, render_template
from routes.auth import login_required
from services.feed_service import FeedService

bp = Blueprint("feed", __name__)

@bp.route("/")
@login_required
def index():
    posts, historias = FeedService.obtener_feed_principal()
    return render_template("index.html", posts=posts, historias=historias)

@bp.route("/feed")
@login_required
def feed():
    posts = FeedService.obtener_solo_posts()
    return render_template("_posts.html", posts=posts)