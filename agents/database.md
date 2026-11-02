# Base de datos

Responsabilidad: modelos, migraciones y restricciones en `apps/api/app/models.py`, `db.py`, `migrations/` y pruebas de persistencia. Acordar migraciones y contratos antes de editar.

Mantener tenant obligatorio, FK compuestas cuando un recurso apunta a otro recurso de empresa, índices por scope y dinero entero. Revisar transacciones y locks en PostgreSQL. No asumir que SQLite demuestra concurrencia. No reescribir migraciones ya distribuidas; agregar una nueva.

Entrega: DDL revisado, upgrade/check y reversión en una base desechable, tests de restricciones e impacto operativo. RLS, roles de mínimo privilegio y migración de fechas son trabajo futuro identificado; no reportarlos como implementados hasta probarlos.
