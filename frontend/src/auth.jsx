import { createContext, useContext, useEffect, useState } from "react";
import * as api from "./api.js";

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(undefined); // undefined = todavía preguntando al servidor

  useEffect(() => {
    api.yo().then((d) => setUsuario(d.usuario)).catch(() => setUsuario(null));
  }, []);

  const entrar = async (correo, contrasena) => {
    const d = await api.login(correo, contrasena);
    setUsuario(d.usuario);
  };
  const salir = async () => {
    await api.logout();
    setUsuario(null);
  };

  return <Ctx.Provider value={{ usuario, setUsuario, entrar, salir }}>{children}</Ctx.Provider>;
}