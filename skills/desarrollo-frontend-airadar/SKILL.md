---
name: desarrollo-frontend-airadar
description: Use when building, editing, reviewing, or validating the AI Radar frontend, dashboard, UI, HTML, CSS, JavaScript, reader mode, operator mode, signal ranking, filters, evidence views, or visual product screens.
---

# Desarrollo Frontend AI Radar

## Principio

El frontend de AI Radar debe ser una interfaz tecnica usable, conectada a datos reales o fixtures declarados. No presentar datos inventados como si vinieran del sistema.

## Reglas Obligatorias

1. Inspeccionar el repo antes de editar.
2. Declarar la fuente de datos de cada pantalla:
   - API real server-side;
   - SQLite/JSON local mediante script o endpoint;
   - fixture versionado y explicitamente marcado como fixture.
3. No usar datos mock inline si no existe una razon clara. Si se usan fixtures, guardarlos en una ruta visible como `codex/data/fixtures/` y rotular la UI como demo/fixture cuando aplique.
4. Implementar estados completos:
   - loading;
   - empty;
   - error;
   - success;
   - stale/cache/fallback cuando aplique;
   - guardado/validacion en progreso si hay acciones.
5. Mantener responsive real:
   - desktop;
   - tablet;
   - mobile;
   - sin overflow horizontal accidental;
   - tablas convertidas a lista o layout escaneable en pantallas pequenas.
6. Cumplir accesibilidad basica:
   - labels en inputs;
   - foco visible;
   - botones con nombre accesible;
   - contraste legible;
   - navegacion por teclado en controles principales;
   - `aria-live` para errores o cambios async importantes.
7. Verificar consola limpia:
   - sin errores;
   - sin warnings evitables;
   - sin requests fallidos no explicados.
8. Tomar capturas de verificacion antes de finalizar:
   - desktop;
   - mobile;
   - estado relevante adicional si hubo error/loading/empty.

## Datos Permitidos

Priorizar en este orden:

1. API server-side local que lea SQLite o JSON snapshots.
2. Scripts existentes:
   - `codex/scripts/query_saved_signals.py`
   - `codex/scripts/query_daily_signals.py`
3. JSON snapshots:
   - `codex/data/daily/YYYY-MM-DD-ai-signals.json`
4. Fixtures declarados:
   - `codex/data/fixtures/*.json`

Si una pantalla muestra ranking por importancia, usar `importance_score` real. Si falta, mostrar `Sin puntaje` y no fabricar score.

## UI Esperada

AI Radar es una herramienta de trabajo, no una landing page.

Debe priorizar:

- ranking de senales;
- filtros por fecha, fuente, estado y texto;
- evidencia visible;
- estado de fuentes;
- modo lector;
- modo operador;
- persistencia JSON/SQLite;
- trazas de validacion.

Evitar:

- heroes de marketing;
- tarjetas decorativas innecesarias;
- paletas de un solo color;
- texto explicando como usar la UI dentro de la app;
- elementos que se solapen en mobile.

## Verificacion

Antes de cerrar una tarea frontend:

1. Ejecutar el servidor local si la app lo requiere.
2. Abrir la UI en navegador.
3. Probar al menos:
   - busqueda;
   - filtros;
   - cambio lector/operador;
   - estado empty o error si existe forma simple de provocarlo.
4. Revisar consola.
5. Capturar desktop y mobile.
6. Reportar:
   - URL local;
   - datos usados: API, JSON o fixture;
   - estados verificados;
   - capturas tomadas;
   - problemas pendientes.

## Criterio De Bloqueo

No declarar terminado si:

- la pantalla depende de datos inventados;
- no hay estado de error;
- la UI rompe en mobile;
- hay errores de consola;
- no se tomaron capturas;
- no se puede explicar de donde salen las senales.
