import re
from db import get_auth_client, get_admin_client
from repositories.usuarios import UsuarioRepository

class AuthService:
    @staticmethod
    def contrasena_valida(clave):
        return (len(clave) >= 8 and re.search(r"\d", clave) and re.search(r"[^\w\s]", clave))

    @staticmethod
    def usuario_valido(nombre):
        return bool(re.fullmatch(r"[A-Za-z0-9_]{3,30}", nombre))

    @staticmethod
    def registrar_usuario(nombre, correo, clave):
        if not AuthService.usuario_valido(nombre):
            return False, "El usuario debe tener de 3 a 30 caracteres: letras, números o guion bajo."
        if not AuthService.contrasena_valida(clave):
            return False, "La contraseña necesita mínimo 8 caracteres, un número y un símbolo."
        if UsuarioRepository.buscar_por_nombre(nombre):
            return False, "Ese nombre de usuario ya está en uso."

        try:
            r = get_auth_client().auth.sign_up({"email": correo, "password": clave})
        except Exception as e:
            return False, f"No se pudo crear la cuenta: {e}"

        if not r.user or not r.user.identities:
            return False, "Ese correo ya está registrado."

        try:
            UsuarioRepository.crear_perfil(r.user.id, nombre, correo)
        except Exception as e:
            return False, f"La cuenta se creó, pero falló el perfil: {e}"

        return True, "Cuenta creada. Revisa tu correo para confirmarla."

    @staticmethod
    def iniciar_sesion(correo, clave):
        try:
            r = get_auth_client().auth.sign_in_with_password({"email": correo, "password": clave})
        except Exception as e:
            if "not confirmed" in str(e).lower():
                return None, "Confirma tu correo antes de iniciar sesión."
            return None, "Correo o contraseña incorrectos."

        perfil = UsuarioRepository.buscar_por_id(r.user.id)
        if not perfil:
            return None, "Tu cuenta no tiene perfil. Avisa al equipo."
        if perfil.get("activo") is False:
            return None, "Esta cuenta está desactivada."

        return perfil, None

    @staticmethod
    def dar_de_baja(usuario_id, clave):
        admin_client = get_admin_client()
        if not admin_client:
            return False, "No se puede eliminar la cuenta: falta SUPABASE_SERVICE_KEY en el archivo .env."

        perfil = UsuarioRepository.buscar_por_id(usuario_id)
        if not perfil:
            return False, "Perfil no encontrado."

        try:
            get_auth_client().auth.sign_in_with_password({"email": perfil["correo"], "password": clave})
        except Exception:
            return False, "La contraseña es incorrecta."

        try:
            admin_client.auth.admin.delete_user(usuario_id)
        except Exception as e:
            return False, f"No se pudo eliminar el acceso: {e}"

        try:
            UsuarioRepository.eliminar_perfil(usuario_id)
        except Exception as e:
            return False, f"Se eliminó el acceso de Auth pero falló eliminar el perfil ({e})."

        return True, "Tu cuenta fue eliminada por completo. Ya puedes volver a registrarte con ese correo o usuario."