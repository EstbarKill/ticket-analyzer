# AI Support Ticket Analyzer

Analizador de tickets de soporte que ingiere un CSV real (con sus
inconsistencias), enriquece cada ticket con IA (categoría, prioridad,
resumen, sentimiento, urgencia, equipo responsable), expone esos datos vía
API y los muestra en un dashboard, además de un endpoint `/ask` con RAG sobre
los tickets y una base de conocimiento.

Stack: **FastAPI + SQLite** (backend) y **Next.js + TypeScript + Tailwind**
(frontend), separados, comunicándose por HTTP.

---

## 1. Instalación y ejecución

### Opción A — Docker Compose

```bash
docker compose up --build
```

- Backend: http://localhost:8000 (docs interactivos en `/docs`)
- Frontend: http://localhost:3000

Por defecto todo corre en **modo mock** (sin ninguna API key). Para usar
Gemini real, exporta las variables antes de levantar (ver sección de
variables de entorno) o crea un archivo `.env` en la raíz con
`GEMINI_API_KEY=...` antes de correr `docker compose up --build`.

> Nota técnica: Next.js incrusta las variables `NEXT_PUBLIC_*` en el bundle
> en tiempo de build, no en runtime. Si cambias `NEXT_PUBLIC_API_URL` debes
> reconstruir la imagen del frontend (`docker compose build frontend`).

### Opción B — Comandos directos (sin Docker)

**Backend:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # ajusta si quieres usar Gemini real
uvicorn app.main:app --reload --port 8000
```

**Frontend** (en otra terminal):

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Frontend en http://localhost:3000, backend en http://localhost:8000.

---

## 2. Cómo probarlo

1. Abre http://localhost:3000 (Dashboard). Si es la primera vez, los KPIs
   saldrán vacíos: dale clic a **"Reimportar tickets"** (esto llama a
   `POST /tickets/import`, que lee `backend/dataset/tickets.csv`, limpia los
   datos, los enriquece con IA y los guarda).
2. Ve a la pestaña **Tickets**: tabla completa con filtros por categoría,
   prioridad, estado y producto. Clic en una fila para ver el detalle.
3. Ve a **Asistente IA** y prueba las preguntas sugeridas, por ejemplo:
   - "¿Cuáles son los problemas más críticos esta semana?"
   - "¿Qué producto genera más quejas?"
   - "¿Cuál es el SLA para tickets críticos?"

También puedes probar la API directamente en `http://localhost:8000/docs`
(Swagger autogenerado por FastAPI), o con `curl`:

```bash
curl -X POST http://localhost:8000/tickets/import
curl "http://localhost:8000/tickets?priority=Critical&limit=5"
curl http://localhost:8000/dashboard/summary
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "¿qué producto genera más quejas?"}'
```

---

## 3. Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio y proveedores activos. |
| POST | `/tickets/import` | Lee `dataset/tickets.csv`, limpia, enriquece con IA y persiste (reemplaza los datos existentes). |
| GET | `/tickets` | Lista tickets enriquecidos. Filtros: `category`, `priority`, `status`, `team`, `product`. Paginación: `limit`, `offset`. |
| GET | `/tickets/{id}` | Detalle de un ticket (id interno, no el `Ticket ID` original). |
| GET | `/dashboard/summary` | KPIs y agregados (totales, por prioridad, categoría, equipo, sentimiento, top productos, promedios de satisfacción y resolución). |
| POST | `/ask` | `{"question": "..."}` → RAG sobre tickets + base de conocimiento. |

---

## 4. Variables de entorno

### Backend (`backend/.env`, ver `backend/.env.example`)

| Variable | Default | Descripción |
|---|---|---|
| `LLM_PROVIDER` | `mock` | `mock` (heurística local, gratis) o `gemini` (real). |
| `EMBEDDING_PROVIDER` | `mock` | `mock` (TF-IDF local) o `gemini` (embeddings reales). |
| `GEMINI_API_KEY` | _(vacío)_ | Requerida si usas `gemini` en cualquiera de los dos anteriores. Se obtiene en https://aistudio.google.com/apikey |
| `GEMINI_MODEL` | `gemini-3.5-flash` | Modelo de chat de Gemini. |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-001` | Modelo de embeddings de Gemini. |
| `CORS_ORIGINS` | `http://localhost:3000` | Orígenes permitidos, separados por coma. |

Si `LLM_PROVIDER=gemini` pero no hay `GEMINI_API_KEY`, el sistema cae
automáticamente a `mock` (ver `app/core/config.py`, propiedad
`active_llm_provider`) — nunca se rompe por falta de key.

### Frontend (`frontend/.env.local`, ver `frontend/.env.local.example`)

| Variable | Default | Descripción |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | URL del backend. |

---

## 5. Decisiones técnicas

**SQLite en vez de Postgres.** Para el volumen de este ejercicio (cientos de
tickets) un archivo SQLite es suficiente y elimina toda la fricción de
levantar un servicio de base de datos aparte. Se usa SQLAlchemy como ORM, así
que migrar a Postgres en el futuro es cambiar `DATABASE_URL`, no reescribir
código.

**Embeddings locales (TF-IDF) para la base de conocimiento, en vez de
pgvector o un modelo descargado.** La base de conocimiento son 5 documentos
markdown cortos: para ese tamaño, TF-IDF da una búsqueda semántica razonable
sin pagar por una API ni descargar un modelo de cientos de MB en el primer
arranque. La interfaz `EmbeddingProvider` es la misma para el modo mock y
para Gemini, así que cambiar de uno a otro es una variable de entorno, no un
cambio de arquitectura. Si la base de conocimiento creciera mucho, lo natural
sería migrar a embeddings reales + una base vectorial real.

**Retrieval híbrido en `/ask`.** Los tickets ya enriquecidos tienen campos
categóricos limpios (prioridad, categoría, sentimiento, equipo), así que
filtrar por esos campos da mejores resultados que buscar tickets por
similitud de texto libre, y es mucho más simple — por eso la recuperación
sobre tickets es estructurada (por fecha/prioridad/producto/sentimiento
mencionados en la pregunta) en vez de vectorial. La base de conocimiento sí
usa búsqueda semántica, porque es texto libre sin estructura. Para preguntas
tipo ranking ("qué producto/categoría genera más quejas") se calculan
agregados (conteos por producto/categoría/equipo) en vez de mostrarle al
modelo un puñado de tickets sueltos, porque la respuesta correcta depende de
contar sobre todo el dataset.

**Prioridad de IA con la prioridad original como punto de partida.** En vez
de ignorar el campo `Ticket Priority` del CSV, se usa como punto de partida
y se ajusta según el contenido del ticket (lenguaje urgente o muy negativo la
sube). Esto refleja mejor cómo funcionaría en producción: la prioridad
reportada suele ser una señal real, no ruido a descartar.

**Resistencia básica a contenido no confiable en los tickets.** El dataset
trae descripciones con texto repetitivo y algunas frases sueltas tipo
placeholder sin rellenar. El system prompt de Gemini deja explícito que el
texto del ticket es contenido de un cliente externo, no instrucciones para
el modelo, y que debe limitarse a clasificar. Es una buena práctica general
para cualquier sistema que mete texto de usuarios en un prompt, más allá de
si este dataset en particular tiene intención adversarial o no.

**Frontend separado, sin shadcn/ui ni TanStack Table.** Next.js + Tailwind +
Recharts es suficiente para 3 páginas con una tabla con filtros simples;
sumar más librerías de componentes no agregaba valor proporcional al tiempo
que costaba.

**Una sola tabla ancha (`tickets`) en vez de `tickets` + `ticket_analysis`
separadas.** Para este volumen, una tabla con todos los campos (originales +
`ai_*`) es más simple de consultar que un join constante, sin perder
trazabilidad de qué fue generado por IA (columna `ai_provider_used`).

**Supuestos sobre los datos** (documentados también en el código,
`app/services/data_cleaning.py`):
- Prioridades duplicadas por `Ticket ID`: se conserva la primera ocurrencia y
  se descartan las repetidas (se reportan en la respuesta de `/tickets/import`).
- Prioridades numéricas (`"1"`–`"4"`, `"P1"`–`"P4"`) se interpretan con la
  convención más común en sistemas de ticketing: 1/P1 = más urgente.
- Fechas en texto en español (`"19 de diciembre 2020"`) se parsean con una
  función dedicada, además de los formatos `YYYY-MM-DD`, `DD/MM/YYYY` y
  `MM/DD/YYYY`.
- Registros con `Ticket ID` inválido o vacío no se importan (no hay forma
  confiable de identificarlos ni de evitar colisiones).

---

## 6. Limitaciones conocidas y qué mejoraría con más tiempo

- El proveedor **mock** de sentimiento/urgencia usa una lista corta de
  palabras clave en inglés/español; detecta poco sentimiento negativo en
  este dataset en particular (textos repetitivos y poco expresivos). Con
  Gemini real (`LLM_PROVIDER=gemini`) la clasificación es mucho más rica —
  está probado que el provider real llega correctamente al endpoint de
  Google y maneja errores sin romper la importación (ver tests manuales
  abajo), aunque no se pudo correr una importación completa con key real
  durante el desarrollo en este entorno.
- `POST /tickets/import` reemplaza todos los tickets en cada corrida (no hay
  importación incremental). Para un dataset que crece todos los días, lo
  correcto sería un upsert por `Ticket ID`.
- Los embeddings de Gemini se piden uno por texto (no hay batching). Para 5
  documentos de la base de conocimiento no importa, pero si la base creciera
  mucho convendría usar `batchEmbedContents`.
- No hay autenticación en la API ni en el dashboard — fuera de alcance para
  esta prueba, pero sería lo primero a agregar antes de cualquier uso real.
- No hay tests automatizados (`pytest`); se validó manualmente cada endpoint
  end-to-end con el dataset real durante el desarrollo (importación,
  filtros, agregados, y las dos preguntas de ejemplo del enunciado).
- El cálculo de "tiempo de resolución" usa `First Response Time` →
  `Time to Resolution` porque es el único par de timestamps disponible en
  ambos extremos del ciclo de vida del ticket; los tickets sin esos dos
  campos (la mayoría de los `Open`/`Pending`, como es esperable) no entran
  en el promedio.

---

## 7. Uso de IA durante el desarrollo

Ver [`AI_USAGE.md`](./AI_USAGE.md).
