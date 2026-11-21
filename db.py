import httpx
from supabase import create_client, ClientOptions
from config import Config

def _opciones():
    # Evita el error [WinError 10035] de HTTP/2 en Windows al hacer peticiones paralelas
    cliente_http = httpx.Client(http2=False, timeout=20.0)
    return ClientOptions(httpx_client=cliente_http)

# Cliente principal para operaciones de lectura/escritura en tablas
db = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY, options=_opciones())

def get_auth_client():
    """Crea un cliente nuevo por cada registro o login para no mezclar sesiones."""
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY, options=_opciones())

def get_admin_client():
    """Cliente administrativo para acciones restringidas como eliminar usuarios."""
    if not Config.SUPABASE_SERVICE_KEY:
        return None
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY, options=_opciones())