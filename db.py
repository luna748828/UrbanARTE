from supabase import create_client
from config import Config

# Cliente principal para operaciones de lectura/escritura en tablas
db = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def get_auth_client():
    """Crea un cliente nuevo por cada registro o login para no mezclar sesiones."""
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def get_admin_client():
    """Cliente administrativo para acciones restringidas como eliminar usuarios."""
    if not Config.SUPABASE_SERVICE_KEY:
        return None
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)