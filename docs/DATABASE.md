# Modelo de datos

Importes en centésimos de UYU, almacenados como enteros: 100000 = 1000 UYU. No se suman monedas diferentes. Cada empresa tiene una moneda (`UYU` en las dos muestras). País de destino de una propuesta es independiente de la moneda; no hay conversión automática.

| Tabla | Contenido | Relaciones / restricciones |
| --- | --- | --- |
| tenants | UUID, slug, nombre, moneda, país, límite diario, máximo aumento | Slug único; fila usada como bloqueo de cambios de presupuesto |
| members | UUID, tenant, nombre, rol | FK tenant; rol owner/viewer |
| sessions | Hash de token, member, vencimiento | Hash como PK; FK member; no guarda el token original |
| products | Nombre, descripción, precio, margen | FK tenant; precio positivo y margen 1–100 |
| creatives | Producto, tipo, texto, MIME, storage_key, análisis JSON | FK compuesta tenant/product; nombre original no forma ruta |
| campaigns | Métricas demo, presupuesto diario, estado, días, revisión | FK tenant; presupuesto positivo; datos históricos fijos |
| proposals | Título, plan JSON snapshot, estado | FK tenant; pending/approved/rejected |
| recommendations | Campaña, revisión, acción, motivo, presupuesto sugerido, estado | FK compuesta tenant/campaign; una por campaña y revisión |
| audit_events | Actor, acción, recurso, detalle JSON, fecha | FK tenant; índice tenant/fecha |

Los recursos propios de empresa heredan ID UUID y fecha ISO UTC. Las columnas `tenant_id` están indexadas. Hay restricciones UNIQUE sobre pares tenant/id donde las FKs compuestas lo requieren.

Los planes guardan referencias y un snapshot de presupuesto, audiencia, estrategia y razonamiento en JSON. No se convierten en objetos de Meta. Cambiar el catálogo no altera retroactivamente un plan guardado. No existe eliminación de recursos en el MVP; se evita romper referencias históricas por borrado. La API de edición solo cubre productos.

La primera migración explícita es `0001_initial_schema.py`. `alembic upgrade head` debe ejecutarse antes de iniciar la API. `alembic check` detecta diferencias entre esquema y modelos. Para nuevos cambios: crear revisión autogenerada, revisar DDL y migración de datos, probar upgrade/downgrade sobre una base desechable y registrar compatibilidad. No reescribir la migración inicial después de que existan usuarios.

El seed inserta únicamente empresas que no existen y no las reinicia. La suite de tests usa su propio motor y reconstruye sus tablas. `TEST_DATABASE_URL` solo se admite si el nombre termina en `_test`; aún así debe ser una base dedicada sin datos útiles.

Limitaciones: no hay RLS, soft delete, índices analíticos, snapshots diarios de Insights, cuentas de Meta, catálogo de variantes, usuarios reales multiempresa ni retención configurable. Las fechas son cadenas ISO comparables por UTC, no `timestamptz`; migrarlas al diseñar operación multizona. Ver ADR 0002 y SECURITY.md.
