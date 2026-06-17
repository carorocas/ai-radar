# Guia de Agentes de AI Radar

AI Radar es el proyecto del curso para aprender Codex con una superficie de producto real.

El estado actual del repositorio es pequeno de forma intencional. Trata el README como direccion de producto, no como prueba de que el sistema completo ya existe.

## Estado Actual

- El proyecto actualmente tiene un README y reglas del repositorio.
- La implementacion se construye clase por clase.
- No asumas que existen archivos de app, scripts, bases de datos, skills, configuracion de despliegue o automatizaciones hasta que esten presentes en el repositorio.

## Direccion del Producto

AI Radar recopilara noticias, papers, repositorios, herramientas y lanzamientos de IA, y luego los convertira en senales verificables para builders.

El sistema final debe soportar:

- evidencia de fuentes;
- senales normalizadas;
- deteccion de duplicados;
- ranking;
- guias practicas de accion;
- una vista de operador;
- despliegue y automatizacion.

## Reglas de Trabajo

- Inspecciona el repositorio antes de editar.
- Manten los cambios acotados al objetivo de la clase actual.
- Prefiere archivos pequenos y reproducibles sobre estado que solo exista en el chat.
- No confirmes secretos, caches locales, snapshots semanales generados, salida de build, videos, capturas de pantalla ni reportes temporales.
- Cuando una clase cree un proceso reutilizable, prefiere una skill.
- Cuando una clase cree trabajo determinista, prefiere una herramienta o script.
- Al agregar ejemplos de datos, usa fixtures o contratos, salvo que la clase requiera explicitamente una semilla durable.

## Validacion

Para cada rama de clase, deja un estado claro:

- que se agrego;
- como verificarlo;
- que queda intencionalmente pendiente.

Si los comandos todavia no existen, no los inventes en la documentacion como si ya funcionaran.
