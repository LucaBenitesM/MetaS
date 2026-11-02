# API HTTP v0.1

Base local `http://localhost:8000`. OpenAPI interactivo `/docs`; JSON vivo `/openapi.json` y snapshot en `packages/shared/openapi.json`.

## Sesión de demo

```http
POST /api/auth/demo
Content-Type: application/json

{"tenant":"cristal-demo","role":"owner"}
```

Devuelve `access_token`, `token_type=bearer`, `expires_at`, `tenant`, `member`, `mode=demo`. Valores válidos: tenant `cristal-demo | norte-demo`; rol `owner | viewer`. No es identidad comercial. En el resto de rutas enviar:

```http
Authorization: Bearer <access_token>
```

## Rutas

| Método y ruta | Rol | Efecto |
| --- | --- | --- |
| GET /health | Público | Estado DB, demo y Meta desconectado |
| POST /api/auth/demo | Público demo | Crea sesión opaca de prueba |
| POST /api/auth/logout | Miembro | Revoca sesiones del miembro demo |
| GET /api/me | Miembro | Empresa y rol de la sesión |
| GET /api/dashboard | Miembro | Métricas ficticias agregadas y campañas |
| GET /api/products | Miembro | Catálogo de su empresa |
| POST /api/products | Owner | Alta de producto, 201 |
| PUT /api/products/{id} | Owner | Edición completa del producto |
| GET /api/creatives | Miembro | Biblioteca y análisis, sin rutas de almacenamiento |
| POST /api/creatives/upload | Owner | Multipart privado, análisis técnico, 201 |
| GET /api/creatives/{id}/file | Miembro | Descarga privada; fichas seed dan 404 |
| GET /api/proposals | Miembro | Planes guardados por fecha descendente |
| POST /api/proposals | Owner | Genera snapshot de plan, 201 |
| POST /api/proposals/{id}/decision | Owner | Aprueba/rechaza, sin crear campaña |
| POST /api/proposals/{id}/publish | Owner | Siempre 403 para recursos propios |
| GET /api/rules | Miembro | Límites y umbrales actuales |
| PUT /api/rules | Owner | Actualiza límites e invalida revisiones anteriores |
| GET /api/recommendations | Miembro | Recomendaciones de la empresa |
| POST /api/optimization/evaluate | Owner | Genera recomendaciones sin tocar campañas |
| POST /api/recommendations/{id}/decision | Owner | Aprueba/rechaza pendientes |
| POST /api/recommendations/{id}/apply | Owner | Aplica solo simulación aprobada; idempotente |
| GET /api/audit | Miembro | Últimos 100 eventos propios |
| GET /api/integrations/meta | Miembro | Conexión falsa no: informa desconectado explícitamente |
| POST /api/integrations/meta/connect | Owner | 501: OAuth pendiente |

## Cuerpos

Producto:

```json
{"name":"Olla","description":"Uso y beneficio verificable","price_minor":249000,"margin_pct":45}
```

Upload: `multipart/form-data` con `product_id`, `copy` opcional hasta 4000 caracteres y `file`. Máximo lógico 25 MiB. Formatos y límites de validación descritos en SECURITY.md. La respuesta incluye `has_file` y `analysis`, nunca `storage_key`.

Propuesta:

```json
{
  "product_id":"UUID de producto propio",
  "creative_ids":["UUID de anuncio de ese producto"],
  "daily_budget_minor":100000,
  "target_cpa_minor":25000,
  "country":"UY",
  "age_min":18,
  "age_max":65
}
```

Edades adultas 18–65; 65 representa 65+. País: dos letras mayúsculas, todavía no validado contra los destinos/categorías de la Marketing API. Uno a veinte anuncios distintos del mismo producto y empresa. Presupuesto <= límite de empresa. Los ID de otra empresa producen 404. No se valida elegibilidad publicitaria de productos/categorías especiales en esta etapa.

Decisión de propuesta o recomendación:

```json
{"decision":"approve"}
```

También acepta `reject`. Solo una transición desde pendiente. Aplicación de recomendación no lleva cuerpo. Aprobar no ejecuta el cambio. Aplicar devuelve `recommendation`, `campaign` y `simulated: true`.

Reglas:

```json
{"max_daily_minor":500000,"max_increase_pct":20}
```

El límite no puede quedar por debajo del presupuesto simulado activo. El aumento debe estar entre 1 y 20. Se invalidan recomendaciones pendientes/aprobadas y se incrementa revisión de campañas activas para nueva evaluación.

## Errores y consistencia

401 sesión ausente/inválida/expirada; 403 rol o publicación prohibida; 404 recurso inexistente o ajeno; 409 transición inválida, versión obsoleta o aumento fuera de límites; 413 archivo demasiado grande; 422 entrada inválida; 501 integración pendiente. El campo `detail` puede ser texto o una lista de errores Pydantic.

No enviar `tenant_id`: se resuelve desde la sesión. No hay paginación de las colecciones del demo, salvo límite de auditoría. La creación de productos/propuestas no implementa idempotency key y un reintento manual puede duplicarlos; la aplicación de recomendaciones sí es idempotente. Las escrituras reales y la API comercial versionada deberán incorporar contratos adicionales.
