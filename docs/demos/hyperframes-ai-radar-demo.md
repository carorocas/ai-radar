# Demo visual AI Radar para HyperFrames

Fecha: 2026-06-17
Duracion objetivo: 60-75 segundos
Formato: 16:9, demo tecnica, dark theme, ritmo ejecutivo
URL desplegada: https://ai-radar-rlljqomx4-seifer121-9965s-projects.vercel.app/

## Objetivo

Mostrar que AI Radar convierte noticias recientes de inteligencia artificial en senales accionables, respaldadas por evidencia real y visibles en un dashboard tecnico.

## Mensaje central

AI Radar no solo lista noticias. Toma fuentes oficiales, repositorios tecnicos, comunidad y medios secundarios; las normaliza en un contrato JSON; guarda snapshots diarios; y las presenta en un ranking con evidencia, impacto, accion y estado.

## Assets disponibles

- `frontend/ai-radar-desktop-dark.png`: vista principal desktop en dark theme.
- `frontend/ai-radar-mobile-dark.png`: vista responsive movil en dark theme.
- `data/daily/2026-06-17-ai-signals.json`: snapshot diario con 7 senales.
- `contracts/ai-radar-daily-signals.schema.json`: contrato de datos.
- URL publica Vercel: `https://ai-radar-rlljqomx4-seifer121-9965s-projects.vercel.app/`.

## Escenas

### 1. Apertura: problema

Visual: fondo oscuro con captura desktop del dashboard ligeramente ampliada.

Texto en pantalla:
`Demasiadas noticias de IA. Pocas senales accionables.`

Narracion:
`AI Radar ayuda a separar ruido de senales utiles en inteligencia artificial.`

Duracion: 7 segundos

### 2. Que hace la aplicacion

Visual: zoom a las metricas superiores y ranking de senales.

Texto en pantalla:
`Noticias recientes -> senales estructuradas`

Narracion:
`Cada busqueda se transforma en un conjunto diario de senales con fuente, evidencia, impacto, accion y estado.`

Duracion: 9 segundos

### 3. Frontend

Visual: captura `frontend/ai-radar-desktop-dark.png`, resaltando filtros, ranking y modo lector/operador.

Texto en pantalla:
`Dashboard tecnico: ranking, filtros y modos de trabajo`

Narracion:
`El frontend muestra un ranking tecnico con filtros por fecha, fuente y estado. El modo lector prioriza claridad; el modo operador expone mas trazabilidad.`

Duracion: 10 segundos

### 4. Datos usados

Visual: split screen entre dashboard y fragmento del JSON `2026-06-17-ai-signals.json`.

Texto en pantalla:
`Snapshot diario: 2026-06-17`

Narracion:
`La pagina consume un snapshot JSON versionado. En esta corrida hay siete senales generadas desde busqueda paralela por fuentes oficiales, repos tecnicos, comunidad y medios secundarios.`

Duracion: 10 segundos

### 5. Evidencia real

Visual: tarjetas con logos/nombres de fuentes: AP News, OpenAI News, The Verge, GitHub, Hacker News.

Texto en pantalla:
`Respaldado por fuentes verificables`

Narracion:
`Cada senal conserva su fuente original. Por ejemplo: AP News sobre soberania de IA en el G7, OpenAI News sobre adopcion empresarial, The Verge sobre computo de Google y SpaceX, GitHub para radar tecnico y Hacker News para percepcion comunitaria.`

Duracion: 13 segundos

### 6. Persistencia y despliegue

Visual: flujo horizontal `Busqueda paralela -> JSON -> SQLite local -> GitHub -> Vercel`.

Texto en pantalla:
`Persistencia local + snapshots versionados + despliegue en Vercel`

Narracion:
`Las senales se validan contra contrato, se guardan en SQLite local y se publican como snapshots versionados. Al hacer push, Vercel actualiza la demo.`

Duracion: 12 segundos

### 7. Cierre

Visual: dashboard en pantalla completa con ranking visible.

Texto en pantalla:
`AI Radar: inteligencia para decidir que vigilar, probar o escalar`

Narracion:
`El resultado es un radar operativo: evidencia visible, impacto resumido y acciones concretas para equipos que trabajan con IA.`

Duracion: 8 segundos

## Evidencia real incluida

- AP News: `https://apnews.com/article/7d783c6de4356962e338b8b8563d48ea`
- AP News: `https://apnews.com/article/0a87a0f7773255419936af053ad8bdef`
- AP News: `https://apnews.com/article/afeb5279eef406980dffa46ff91495e0`
- OpenAI News: `https://openai.com/news/`
- The Verge: `https://www.theverge.com/tech/944569/google-follows-anthropic-in-signing-a-compute-deal-with-spacex`
- GitHub: `https://github.com/GetStream/awesome-ai-news`
- Hacker News: `https://news.ycombinator.com/item?id=48446893`

## Prompt sugerido para HyperFrames

Crear una demo visual tecnica de 60 a 75 segundos para AI Radar, una aplicacion web en dark theme que convierte noticias recientes de IA en senales accionables. Usar estilo sobrio, dashboard tecnico, overlays limpios, zooms suaves y transiciones tipo producto SaaS. Mostrar el frontend desplegado, el snapshot JSON del 17 de junio de 2026, el contrato de datos y un flujo de persistencia local con SQLite, GitHub y Vercel. Enfatizar que las senales estan respaldadas por fuentes reales: AP News, OpenAI News, The Verge, GitHub y Hacker News. El tono debe ser claro, profesional y orientado a builders.

