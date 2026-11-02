# Orquestador

Leer AGENTS.md y documentos de producto antes de asignar tareas. Confirmar alcance y demo. Preparar una lista de tareas con criterio de aceptación, rutas de propiedad, contrato de API y dependencias. Asignar ramas/worktrees separados si la herramienta de agentes lo permite.

Roles disponibles: backend, frontend, database, meta-api, ai-strategy, optimization y qa. No permitir que dos agentes editen simultáneamente el mismo archivo. `app/main.py` y `app/schemas.py` deben tener un único dueño por integración; los especialistas entregan módulos o un diff acotado al dueño.

Integrar primero migraciones y contratos, luego backend y web. Resolver conflictos con pruebas, sin sobrescribir trabajo de otra tarea. Cada entrega incluye rutas cambiadas, decisiones, controles ejecutados y pendientes. Revisar diferencias de Git antes del commit. No habilitar publicación real ni producción por el hecho de que un especialista cree un adaptador.

Puertas de salida: aislamiento/roles, reglas monetarias, migraciones, tests pertinentes, build y recorrido UI si cambia un flujo. Reportar limitaciones comprobadas en VALIDATION.md.
