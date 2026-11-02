# UrbanARTE - API REST (Taller 3)

API REST en **Node.js + TypeScript + Express** para el módulo de **eventos artísticos y ubicaciones** de UrbanARTE, una app para ubicar murales de arte urbano y organizar eventos en la ciudad.

Los datos se guardan **en memoria (arrays)**: no hay base de datos y todo se reinicia al reiniciar el servidor.

**Integrantes:** Jillian Sofia Caicedo Buitrago, Luna Camila Acosta Sierra

---

## Requisitos

- [Node.js](https://nodejs.org/) 18 o superior
- npm (viene con Node)
- [Postman](https://www.postman.com/downloads/) (para probar la colección)

## Cómo correr el proyecto

Desde la raíz del repositorio:

```bash
cd taller3
npm install
npm run dev
```

Debe aparecer:

```
Servidor listo en http://localhost:3000
```

Prueba rápida en el navegador: <http://localhost:3000/api/v1/eventos> o <http://localhost:3000/api/v1/ubicaciones>

## Scripts npm

| Script | Qué hace |
|---|---|
| `npm run dev` | Arranca el servidor con `tsx watch` (se reinicia solo al guardar) |
| `npm run build` | Compila TypeScript a JavaScript en `dist/` |
| `npm start` | Corre la versión compilada (`dist/server.js`); primero hay que ejecutar `npm run build` |

## Dependencias

**Producción**
- `express`: servidor HTTP

**Desarrollo**
- `typescript`: lenguaje y compilador
- `tsx`: ejecuta TypeScript directamente
- `@types/express`, `@types/node`: tipos

## Estructura

```
taller3/
├── src/
│   └── server.ts                              # Modelos, DTOs, datos en memoria y endpoints
├── UrbanARTE_Taller3.postman_collection.json  # Colección de Postman
├── package.json
├── tsconfig.json
└── README.md
```

## Autenticación

Los endpoints que modifican datos (POST, PATCH, DELETE) requieren el header:

```
Authorization: Bearer <token>
```

Tokens de prueba (fijos, solo para el taller):

| Token | Usuario |
|---|---|
| `token-jill` | 1 |
| `token-luna` | 2 |

Solo el **organizador** de un evento o creador de una ubicación (quien lo creó) puede editarlo o borrarlo.

---

## Endpoints

### Implementados (10)

Base URL: `http://localhost:3000/api/v1`

| Método | Ruta | Token | Respuestas |
|---|---|---|---|
| GET | `/eventos?page=1&limit=10` | No | 200, 400 |
| GET | `/eventos/:id` | No | 200, 400, 404 |
| POST | `/eventos` | Sí | 201, 400, 401 |
| PATCH | `/eventos/:id` | Sí | 200, 400, 401, 403, 404 |
| DELETE | `/eventos/:id` | Sí | 204, 400, 401, 403, 404 |
| GET | `/ubicaciones` | No | 200 |
| GET | `/ubicaciones/:id` | No | 200, 404 |
| POST | `/ubicaciones` | Sí | 201, 400, 401 |
| PATCH | `/ubicaciones/:id` | Sí | 200, 400, 401, 403, 404 |
| DELETE | `/ubicaciones/:id` | Sí | 204, 400, 401, 403, 404 |

**Body para crear un evento (POST):**

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `nombreEvento` | string | Sí | No puede estar vacío |
| `fechaHora` | string (ISO 8601) | Sí | Debe ser una fecha futura |
| `ubicacionEscrita` | string | No | - |
| `cuposDisponibles` | number | No | Entero mayor o igual a 0 |

**Body para crear una ubicación (POST):**

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `nombre` | string | Sí | No puede estar vacío |
| `direccion` | string | Sí | No puede estar vacío |
| `latitud` | number | Sí | Coordenada válida |
| `longitud` | number | Sí | Coordenada válida |
| `categoria` | string | No | Ej. Galería, Mural, Parque |

**Body para editar (PATCH):** cualquiera de los campos anteriores, mínimo uno.

### Solo documentados (no implementados en el código)

Están descritos en el inventario de endpoints del documento de entrega, pero no están programados en este servidor:

- `GET /publicaciones`, `GET /publicaciones/:id`, `POST /publicaciones`, `DELETE /publicaciones/:id`
- `POST /eventos/:id/asistentes`
- `POST /auth/login`

_(Las publicaciones existen hoy en la app Flask del proyecto, app.py, conectada a Supabase.)_


## Ejemplos con curl

> En Windows, usa **Git Bash** para estos comandos. En PowerShell, `curl` es otro comando; usa `curl.exe` y comillas escapadas, o prueba con Postman.

### Eventos

**Listar eventos**
```bash
curl http://localhost:3000/api/v1/eventos
```

**Ver un evento**
```bash
curl http://localhost:3000/api/v1/eventos/1
```

**Crear un evento**
```bash
curl -X POST http://localhost:3000/api/v1/eventos \
  -H "Authorization: Bearer token-jill" \
  -H "Content-Type: application/json" \
  -d '{"nombreEvento":"Taller de grafiti","fechaHora":"2026-12-20T15:00:00Z","ubicacionEscrita":"Parque de la 93","cuposDisponibles":20}'
```

**Editar un evento**
```bash
curl -X PATCH http://localhost:3000/api/v1/eventos/1 \
  -H "Authorization: Bearer token-jill" \
  -H "Content-Type: application/json" \
  -d '{"cuposDisponibles":40}'
```

**Eliminar un evento**
```bash
curl -X DELETE http://localhost:3000/api/v1/eventos/1 \
  -H "Authorization: Bearer token-jill"
```

**Error esperado: crear sin token (401)**
```bash
curl -X POST http://localhost:3000/api/v1/eventos \
  -H "Content-Type: application/json" \
  -d '{"nombreEvento":"Sin token","fechaHora":"2026-12-20T15:00:00Z"}'
```
### Ubicaciones

**Listar ubicaciones**
```bash
curl http://localhost:3000/api/v1/ubicaciones
```
**Ver una ubicación**
```bash
curl http://localhost:3000/api/v1/ubicaciones/1
```
**Crear una ubicación**
```bash
curl -X POST http://localhost:3000/api/v1/ubicaciones \
  -H "Authorization: Bearer token-luna" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Galería Luna","direccion":"Carrera 7 #12-34","latitud":4.6012,"longitud":-74.0721,"categoria":"Galería"}'
```
**Editar una ubicación**
```bash
curl -X PATCH http://localhost:3000/api/v1/ubicaciones/3 \
  -H "Authorization: Bearer token-luna" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Galería Luna (Actualizado)"}'
```
**Eliminar una ubicación**
```bash
curl -X DELETE http://localhost:3000/api/v1/ubicaciones/3 \
  -H "Authorization: Bearer token-luna"
```

## Colección de Postman

El archivo `UrbanARTE_Taller3.postman_collection.json` tiene 14 requests (casos exitosos y de error).

1. En Postman: **Import** y selecciona el archivo (o pega su contenido).
2. Si usas Postman en el navegador, activa el **Desktop Agent** (la web no puede llegar a `localhost`).
3. Con el servidor corriendo, ejecuta los requests en orden.
4. Para repetir las pruebas, reinicia el servidor (los datos vuelven al estado inicial).

## Notas

- El evento con `id: 1` viene precargado para poder probar sin crear datos.
- Los datos viven en memoria: se pierden al apagar el servidor.
- El servidor corre en el puerto `3000`.
