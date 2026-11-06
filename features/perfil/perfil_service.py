import re
from data.repositories.usuarios import UsuarioRepository
from db import get_auth_client

class PerfilService:
    @staticmethod
    def obtener_perfil(usuario_id):
        return UsuarioRepository.buscar_por_id(usuario_id)

    @staticmethod
    def actualizar_datos_personales(usuario_id, nuevo_nombre, biografia=None):
        if not re.fullmatch(r"[A-Za-z0-9_]{3,30}", nuevo_nombre):
            return False, "El nombre de usuario debe contener entre 3 y 30 caracteres (letras, números o guion bajo)."

        perfil_actual = UsuarioRepository.buscar_por_id(usuario_id)
        if perfil_actual.get("nombre_usuario") != nuevo_nombre:
            existente = UsuarioRepository.buscar_por_nombre(nuevo_nombre)
            if existente:
                return False, "Ese nombre de usuario ya está ocupado."

        datos = {"nombre_usuario": nuevo_nombre}
        if biografia is not None:
            datos["biografia"] = biografia

        try:
            UsuarioRepository.actualizar_perfil(usuario_id, datos)
            return True, "Perfil actualizado correctamente."
        except Exception as e:
            return False, f"Error al actualizar perfil: {e}"

    @staticmethod
    def cambiar_contrasena(nueva_clave):
        if not (len(nueva_clave) >= 8 and re.search(r"\d", nueva_clave) and re.search(r"[^\w\s]", nueva_clave)):
            return False, "La contraseña necesita mínimo 8 caracteres, un número y un símbolo."

        try:
            get_auth_client().auth.update_user({"password": nueva_clave})
            return True, "Contraseña actualizada exitosamente."
        except Exception as e:
            return False, f"No se pudo cambiar la contraseña: {e}"