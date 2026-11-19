// Todas las llamadas al back (Flask) viven aquí.
const BASE = "/api";

async function pedir(ruta, { json, form, method } = {}) {
  const opciones = { method: method || (json || form ? "POST" : "GET"), credentials: "include", headers: {} };
  if (json !== undefined) {
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(json);
  }
  if (form) opciones.body = form; // FormData: el navegador pone el Content-Type
  const r = await fetch(BASE + ruta, opciones);
  const datos = await r.json().catch(() => ({}));
  if (!r.ok) {
    const e = new Error(datos.mensaje || datos.error || "Error " + r.status);
    e.status = r.status;
    throw e;
  }
  return datos;
}

// sesión
export const yo = () => pedir("/yo");
export const login = (correo, contrasena) => pedir("/login", { json: { correo, contrasena } });
export const registro = (nombre_usuario, correo, contrasena) => pedir("/registro", { json: { nombre_usuario, correo, contrasena } });
export const logout = () => pedir("/logout", { method: "POST", json: {} });

// publicaciones
export const getPublicaciones = () => pedir("/publicaciones");
export const crearPublicacion = (formData) => pedir("/publicaciones", { form: formData });
export const getArtistas = () => pedir("/artistas");

// eventos
export const getEventos = () => pedir("/eventos");
export const getMisEventos = () => pedir("/eventos/mis-eventos");
export const unirseAEvento = (id) => pedir(`/eventos/${id}/unirse`, { method: "POST" });
export const crearEvento = (datos) => pedir("/eventos/nuevo", { json: datos });
export const salirDeEvento = (id) => pedir(`/eventos/${id}/unirse`, { method: "DELETE" });

// foros
export const getForos = () => pedir("/foros");
export const getForo = (id) => pedir(`/foros/${id}`);
export const crearTema = (foroId, titulo, contenido) => pedir(`/foros/${foroId}/temas`, { json: { titulo, contenido } });
export const getTema = (foroId, temaId) => pedir(`/foros/${foroId}/temas/${temaId}`);
export const responder = (foroId, temaId, contenido) => pedir(`/foros/${foroId}/temas/${temaId}/respuestas`, { json: { contenido } });

// perfil
export const getPerfil = () => pedir("/perfil");
export const guardarPerfil = (nombre_usuario, biografia) => pedir("/perfil", { json: { nombre_usuario, biografia } });