import express, { Request, Response, NextFunction } from "express";

// ---------- Modelos y DTOs ----------
interface Evento {
  id: number;
  nombreEvento: string;
  fechaHora: string;
  ubicacionEscrita?: string;
  cuposDisponibles?: number;
  organizadorId: number;
}

interface CrearEventoDTO {
  nombreEvento: string;
  fechaHora: string;
  ubicacionEscrita?: string;
  cuposDisponibles?: number;
}

type ActualizarEventoDTO = Partial<CrearEventoDTO>;

// --- Ubicaciones (Punto 2) ---
export interface Ubicacion {
  id: number;
  nombre: string;
  direccion: string;
  latitud: number;
  longitud: number;
  categoria: string;
  creadorId: number;
}

export interface CrearUbicacionDTO {
  nombre: string;
  direccion: string;
  latitud: number;
  longitud: number;
  categoria: string;
}

export type ActualizarUbicacionDTO = Partial<CrearUbicacionDTO>;

// ---------- Datos en memoria (se borran al reiniciar) ----------
const eventos: Evento[] = [
  {
    id: 1,
    nombreEvento: "Mural colectivo en la calle 26",
    fechaHora: "2026-12-15T18:00:00.000Z",
    ubicacionEscrita: "Calle 26 con 7ma, Bogotá",
    cuposDisponibles: 30,
    organizadorId: 1,
  },
];
let siguienteIdEvento = 2;

const ubicaciones: Ubicacion[] = [
  {
    id: 1,
    nombre: "Plaza Central de Artes",
    direccion: "Carrera 7 #12-45",
    latitud: 4.60971,
    longitud: -74.08175,
    categoria: "Evento",
    creadorId: 1,
  },
  {
    id: 2,
    nombre: "Galería Urbana Norte",
    direccion: "Calle 85 #11-20",
    latitud: 4.66821,
    longitud: -74.05352,
    categoria: "Galería",
    creadorId: 2,
  },
];
let siguienteIdUbicacion = 3;

const TOKENS = new Map<string, number>([
  ["token-jill", 1],
  ["token-luna", 2],
]);

// ---------- Helpers ----------
function autenticar(req: Request, res: Response, next: NextFunction): void {
  const token = (req.headers.authorization ?? "").replace("Bearer ", "");
  const usuarioId = TOKENS.get(token);
  if (!usuarioId) {
    res.status(401).json({ error: "No autenticado" });
    return;
  }
  res.locals.usuarioId = usuarioId;
  next();
}

function leerId(req: Request): number | null {
  const id = Number(req.params.id);
  return Number.isInteger(id) && id > 0 ? id : null;
}

// Devuelve un mensaje de error si el DTO es inválido, o null si está bien
function validarCampos(dto: ActualizarEventoDTO, esCreacion: boolean): string | null {
  if (esCreacion || dto.nombreEvento !== undefined) {
    if (typeof dto.nombreEvento !== "string" || dto.nombreEvento.trim() === "") {
      return "nombreEvento es obligatorio";
    }
  }

  if (esCreacion || dto.fechaHora !== undefined) {
    const fecha = typeof dto.fechaHora === "string" ? Date.parse(dto.fechaHora) : NaN;
    if (Number.isNaN(fecha) || fecha <= Date.now()) {
      return "fechaHora debe ser una fecha válida en el futuro";
    }
  }

  if (dto.cuposDisponibles !== undefined) {
    if (!Number.isInteger(dto.cuposDisponibles) || dto.cuposDisponibles < 0) {
      return "cuposDisponibles debe ser un entero mayor o igual a 0";
    }
  }

  if (dto.ubicacionEscrita !== undefined && typeof dto.ubicacionEscrita !== "string") {
    return "ubicacionEscrita debe ser texto";
  }

  return null;
}

function validarCamposUbicacion(dto: ActualizarUbicacionDTO, esCreacion: boolean): string | null {
  if (esCreacion || dto.nombre !== undefined) {
    if (typeof dto.nombre !== "string" || dto.nombre.trim() === "") {
      return "nombre es obligatorio";
    }
  }

  if (esCreacion || dto.direccion !== undefined) {
    if (typeof dto.direccion !== "string" || dto.direccion.trim() === "") {
      return "direccion es obligatoria";
    }
  }

  if (esCreacion || dto.latitud !== undefined) {
    if (typeof dto.latitud !== "number" || isNaN(dto.latitud)) {
      return "latitud debe ser un número válido";
    }
  }

  if (esCreacion || dto.longitud !== undefined) {
    if (typeof dto.longitud !== "number" || isNaN(dto.longitud)) {
      return "longitud debe ser un número válido";
    }
  }

  if (esCreacion || dto.categoria !== undefined) {
    if (typeof dto.categoria !== "string" || dto.categoria.trim() === "") {
      return "categoria es obligatoria";
    }
  }

  return null;
}

// ---------- App ----------
const app = express();
app.use(express.json());

// 1. GET /eventos (sin token)
app.get("/api/v1/eventos", (req: Request, res: Response) => {
  const page = Number(req.query.page ?? 1);
  const limit = Number(req.query.limit ?? 10);
  if (!Number.isInteger(page) || page < 1 || !Number.isInteger(limit) || limit < 1) {
    res.status(400).json({ error: "page y limit deben ser enteros positivos" });
    return;
  }

  const ordenados = [...eventos].sort(
    (a, b) => Date.parse(a.fechaHora) - Date.parse(b.fechaHora)
  );
  const data = ordenados.slice((page - 1) * limit, page * limit);
  res.status(200).json({ data, total: eventos.length });
});

// 2. GET /eventos/:id (sin token)
app.get("/api/v1/eventos/:id", (req: Request, res: Response) => {
  const id = leerId(req);
  if (id === null) {
    res.status(400).json({ error: "id debe ser un entero positivo" });
    return;
  }

  const evento = eventos.find((e) => e.id === id);
  if (!evento) {
    res.status(404).json({ error: "Evento no encontrado" });
    return;
  }
  res.status(200).json(evento);
});

// 3. POST /eventos (requiere token)
app.post("/api/v1/eventos", autenticar, (req: Request, res: Response) => {
  const dto: Partial<CrearEventoDTO> = req.body ?? {};

  const error = validarCampos(dto, true);
  if (error) {
    res.status(400).json({ error });
    return;
  }

  const nuevo: Evento = {
    id: siguienteIdEvento++,
    nombreEvento: dto.nombreEvento!.trim(),
    fechaHora: new Date(dto.fechaHora!).toISOString(),
    ubicacionEscrita: dto.ubicacionEscrita,
    cuposDisponibles: dto.cuposDisponibles,
    organizadorId: res.locals.usuarioId,
  };
  eventos.push(nuevo);
  res.status(201).json(nuevo);
});

// 4. PATCH /eventos/:id (requiere token, solo el organizador)
app.patch("/api/v1/eventos/:id", autenticar, (req: Request, res: Response) => {
  const id = leerId(req);
  if (id === null) {
    res.status(400).json({ error: "id debe ser un entero positivo" });
    return;
  }

  const evento = eventos.find((e) => e.id === id);
  if (!evento) {
    res.status(404).json({ error: "Evento no encontrado" });
    return;
  }
  if (evento.organizadorId !== res.locals.usuarioId) {
    res.status(403).json({ error: "Solo el organizador puede editar este evento" });
    return;
  }

  const dto: ActualizarEventoDTO = req.body ?? {};
  if (Object.keys(dto).length === 0) {
    res.status(400).json({ error: "Envía al menos un campo para actualizar" });
    return;
  }

  const error = validarCampos(dto, false);
  if (error) {
    res.status(400).json({ error });
    return;
  }

  if (dto.nombreEvento !== undefined) evento.nombreEvento = dto.nombreEvento.trim();
  if (dto.fechaHora !== undefined) evento.fechaHora = new Date(dto.fechaHora).toISOString();
  if (dto.ubicacionEscrita !== undefined) evento.ubicacionEscrita = dto.ubicacionEscrita;
  if (dto.cuposDisponibles !== undefined) evento.cuposDisponibles = dto.cuposDisponibles;

  res.status(200).json(evento);
});

// 5. DELETE /eventos/:id (requiere token, solo el organizador)
app.delete("/api/v1/eventos/:id", autenticar, (req: Request, res: Response) => {
  const id = leerId(req);
  if (id === null) {
    res.status(400).json({ error: "id debe ser un entero positivo" });
    return;
  }

  const indice = eventos.findIndex((e) => e.id === id);
  if (indice === -1) {
    res.status(404).json({ error: "Evento no encontrado" });
    return;
  }
  if (eventos[indice].organizadorId !== res.locals.usuarioId) {
    res.status(403).json({ error: "Solo el organizador puede eliminar este evento" });
    return;
  }

  eventos.splice(indice, 1);
  res.status(204).send();
});


// 6. GET /ubicaciones (sin token, con paginación y filtro opcional por categoría)
app.get("/api/v1/ubicaciones", (req: Request, res: Response) => {
  const page = Number(req.query.page ?? 1);
  const limit = Number(req.query.limit ?? 10);
  const categoria = req.query.categoria as string | undefined;

  if (!Number.isInteger(page) || page < 1 || !Number.isInteger(limit) || limit < 1) {
    res.status(400).json({ error: "page y limit deben ser enteros positivos" });
    return;
  }

  let resultado = [...ubicaciones];
  if (categoria) {
    resultado = resultado.filter((u) => u.categoria.toLowerCase() === categoria.toLowerCase());
  }

  const data = resultado.slice((page - 1) * limit, page * limit);
  res.status(200).json({ data, total: resultado.length });
});

// 7. GET /ubicaciones/:id (sin token)
app.get("/api/v1/ubicaciones/:id", (req: Request, res: Response) => {
  const id = leerId(req);
  if (id === null) {
    res.status(400).json({ error: "id debe ser un entero positivo" });
    return;
  }

  const ubicacion = ubicaciones.find((u) => u.id === id);
  if (!ubicacion) {
    res.status(404).json({ error: "Ubicación no encontrada" });
    return;
  }
  res.status(200).json(ubicacion);
});

// 8. POST /ubicaciones (requiere token)
app.post("/api/v1/ubicaciones", autenticar, (req: Request, res: Response) => {
  const dto: Partial<CrearUbicacionDTO> = req.body ?? {};

  const error = validarCamposUbicacion(dto, true);
  if (error) {
    res.status(400).json({ error });
    return;
  }

  const nueva: Ubicacion = {
    id: siguienteIdUbicacion++,
    nombre: dto.nombre!.trim(),
    direccion: dto.direccion!.trim(),
    latitud: dto.latitud!,
    longitud: dto.longitud!,
    categoria: dto.categoria!.trim(),
    creadorId: res.locals.usuarioId,
  };

  ubicaciones.push(nueva);
  res.status(201).json(nueva);
});

// 9. PATCH /ubicaciones/:id (requiere token, solo el creador)
app.patch("/api/v1/ubicaciones/:id", autenticar, (req: Request, res: Response) => {
  const id = leerId(req);
  if (id === null) {
    res.status(400).json({ error: "id debe ser un entero positivo" });
    return;
  }

  const ubicacion = ubicaciones.find((u) => u.id === id);
  if (!ubicacion) {
    res.status(404).json({ error: "Ubicación no encontrada" });
    return;
  }
  if (ubicacion.creadorId !== res.locals.usuarioId) {
    res.status(403).json({ error: "Solo el creador puede editar esta ubicación" });
    return;
  }

  const dto: ActualizarUbicacionDTO = req.body ?? {};
  if (Object.keys(dto).length === 0) {
    res.status(400).json({ error: "Envía al menos un campo para actualizar" });
    return;
  }

  const error = validarCamposUbicacion(dto, false);
  if (error) {
    res.status(400).json({ error });
    return;
  }

  if (dto.nombre !== undefined) ubicacion.nombre = dto.nombre.trim();
  if (dto.direccion !== undefined) ubicacion.direccion = dto.direccion.trim();
  if (dto.latitud !== undefined) ubicacion.latitud = dto.latitud;
  if (dto.longitud !== undefined) ubicacion.longitud = dto.longitud;
  if (dto.categoria !== undefined) ubicacion.categoria = dto.categoria.trim();

  res.status(200).json(ubicacion);
});

// 10. DELETE /ubicaciones/:id (requiere token, solo el creador)
app.delete("/api/v1/ubicaciones/:id", autenticar, (req: Request, res: Response) => {
  const id = leerId(req);
  if (id === null) {
    res.status(400).json({ error: "id debe ser un entero positivo" });
    return;
  }

  const indice = ubicaciones.findIndex((u) => u.id === id);
  if (indice === -1) {
    res.status(404).json({ error: "Ubicación no encontrada" });
    return;
  }
  if (ubicaciones[indice].creadorId !== res.locals.usuarioId) {
    res.status(403).json({ error: "Solo el creador puede eliminar esta ubicación" });
    return;
  }

  ubicaciones.splice(indice, 1);
  res.status(204).send();
});

// ---------- Errores ----------
// JSON mal formado en el body
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  if (err instanceof SyntaxError) {
    res.status(400).json({ error: "JSON inválido" });
    return;
  }
  console.error(err);
  res.status(500).json({ error: "Error interno del servidor" });
});

const PORT = 3000;
app.listen(PORT, () => console.log(`Servidor listo en http://localhost:${PORT}`));
