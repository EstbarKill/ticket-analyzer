# Uso de IA durante el desarrollo

## Herramienta

Todo el proyecto (diseño, código de backend y frontend, debugging,
documentación) se construyó con **Claude** (Anthropic), trabajando en una
sesión de chat con acceso a una terminal Linux.

## Cómo se usó

**1. Análisis de los datos antes de diseñar nada.** Antes de escribir
código, le pedí a Claude que inspeccionara `tickets.csv` directamente
(conteo de filas, duplicados por `Ticket ID`, distribución de valores de
`Ticket Priority` y `Ticket Type`, formatos de fecha, valores faltantes).
Eso cambió decisiones reales: por ejemplo, confirmar que había 9 `Ticket ID`
duplicados y al menos 4 formatos de fecha distintos (incluyendo texto en
español) antes de escribir la función de limpieza, en vez de adivinar.

**2. Negociación explícita del alcance.** El repositorio venía con dos
documentos de referencia con expectativas muy distintas: la prueba técnica
en sí (que pide explícitamente simplicidad y da 1 día de margen) y un
documento de tipo "AGENTS.md"/ROLE con una arquitectura de nivel enterprise
(Postgres + pgvector, Next.js con shadcn/TanStack, Clean Architecture en 4
capas, observabilidad completa). Le pedí a Claude que señalara esa tensión en
vez de construir a ciegas el documento más ambicioso, y juntos decidimos un
punto medio: tomar las ideas del documento ROLE (RAG real, proveedor de IA
intercambiable, base de conocimiento) pero implementarlas en un stack que se
levanta en minutos (SQLite en vez de Postgres+pgvector, TF-IDF local en vez
de un modelo de embeddings pesado).

**3. Escritura de todo el código, con pruebas reales en cada paso, no solo
generación.** Claude no solo escribió los archivos: después de cada bloque
importante (limpieza de datos, proveedores de IA, `/ask`) levantó el backend
real con `uvicorn`, importó el CSV real y revisó las respuestas. Eso permitió
encontrar y corregir bugs reales antes de entregar, por ejemplo:
- La heurística de prioridad del proveedor mock dejaba casi todo en `Low`
  porque ignoraba la prioridad original del CSV; se corrigió para usarla
  como punto de partida, lo que dio una distribución realista.
- El endpoint `/ask` devolvía siempre los mismos 8 tickets sin importar la
  pregunta cuando ningún filtro de texto coincidía (por ejemplo, "esta
  semana" no encuentra nada porque el dataset es de 2020-2023); se agregó un
  fallback explícito y agregados (conteos por producto/categoría) para
  preguntas tipo ranking.
- Al revisar un checklist generado por otra IA sobre el estado del proyecto,
  varias afirmaciones no correspondían al código real (mencionaba un modelo
  de embeddings que no se usó, un error 500 que no se reproducía, un
  dashboard "inexistente" que ya estaba construido). Se verificó cada punto
  contra el repositorio real en vez de aceptarlo, incluyendo probar en vivo
  el proveedor de Gemini con una API key inválida para confirmar que el
  manejo de errores no rompe la importación.
- Next.js se instaló inicialmente en una versión con una vulnerabilidad de
  seguridad conocida; se detectó por el warning de `npm install` y se
  actualizó a la última versión parcheada de la misma rama.

**4. Documentación.** Este `README.md` y este mismo archivo se escribieron
con Claude, pero describiendo decisiones y resultados verificados
realmente (no descripciones genéricas de "buenas prácticas").

## Qué se validó manualmente (no solo "Claude dijo que funciona")

- Importación del CSV real completo: 409 filas → 400 importadas, 9
  duplicados detectados, 0 errores de enriquecimiento.
- `GET /tickets` con cada filtro (categoría, prioridad, estado, producto).
- `GET /dashboard/summary`: se revisaron los números devueltos (totales,
  distribución por prioridad/categoría/equipo, satisfacción y tiempo de
  resolución promedio) para confirmar que tenían sentido frente al dataset.
- `POST /ask` con las dos preguntas de ejemplo del enunciado de la prueba.
- `npm run build` del frontend sin errores de tipos, y las 3 rutas (`/`,
  `/tickets`, `/assistant`) respondiendo `200`.
- El proveedor real de Gemini (`GeminiLLMProvider`) con una API key inválida,
  para confirmar que un fallo de red/autenticación no tumba la API.

## Configuración de agentes / prompts reutilizables

No se usó un archivo `AGENTS.md` propio para este desarrollo (sí existía uno
provisto por la empresa como documento de referencia de arquitectura, descrito
arriba). Los prompts del sistema usados en producción por el propio producto
(no para desarrollarlo, sino los que el backend le envía a Gemini en
runtime) están versionados como código en
`backend/app/services/providers/gemini_llm.py`
(`ENRICHMENT_SYSTEM_PROMPT` y `ASK_SYSTEM_PROMPT`), para que sean revisables
y no estén hardcodeados sueltos en el medio de la lógica de negocio.
