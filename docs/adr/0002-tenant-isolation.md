# ADR 0002 · Base compartida con scope explícito

Estado: aceptado. Fecha: 2026-11-02.

Contexto: varias empresas requieren datos separados con una base operable para el MVP.

Decisión: `tenant_id` obligatorio en recursos, resuelto desde una sesión de servidor; filtros explícitos en toda lectura/escritura; 404 para recursos ajenos; claves compuestas en relaciones de producto y campaña. PostgreSQL como referencia, SQLite para desarrollo.

Consecuencias: simplicidad de migraciones y tests. No hay aislamiento contra consultas privilegiadas ni errores futuros que omitan filtros. Se exige test de acceso cruzado por endpoint nuevo y RLS con roles restringidos antes de producción. No aceptar `tenant_id` del navegador como autoridad.
