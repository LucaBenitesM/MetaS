# Roadmap y entrega

## Entregado · v0.1 demo

- [x] Repositorio y documentación en español; guía para Orca y agentes.
- [x] Next.js, FastAPI, PostgreSQL y alternativa SQLite.
- [x] Sesiones demo, roles y separación de empresas comprobada.
- [x] Catálogo, carga privada, análisis técnico y biblioteca de anuncios.
- [x] Dashboard ficticio, propuestas ABO/CBO y briefs heurísticos.
- [x] Reglas de optimización, aprobación, aplicación simulada y auditoría.
- [x] Worker opcional que solo propone; límites agregados e idempotencia.
- [x] Migraciones, Compose, pruebas API/navegador y CI preparado.

## Etapa 1 · Base comercial

Prioridad alta: identidad OIDC real, registro e invitaciones, membership por usuario y empresa, eliminación de login público de demo, sesiones con cookies HttpOnly o BFF, recuperación, RLS y pruebas de bypass. Límites de petición en proxy, cuotas, paginación, antivirus/transcodificación y almacenamiento privado gestionado. Jobs únicos de migración; registros estructurados, métricas, alertas y backups con restauración ensayada.

Criterio de salida: revisión de amenazas, pruebas de aislamiento y concurrencia, restauración verificada y ninguna ruta demo pública habilitada en producción.

## Etapa 2 · Meta en lectura

Registrar aplicación y negocio, confirmar requisitos vigentes, permisos y revisión; implementar OAuth con state de un solo uso, almacenamiento cifrado de tokens, revocación, selección de cuentas autorizadas, importadores idempotentes y normalización de zona horaria/moneda/atribución. Mantener datos demo separados de fuentes reales. Gestionar expiración, errores y rate limits sin perder trazabilidad.

Criterio de salida: una cuenta autorizada sincroniza campañas e Insights, con procedencia visible y sin permisos de escritura innecesarios.

## Etapa 3 · IA evaluable

Proveedor multimodal/LLM configurable con esquemas estrictos y evaluación de calidad; citas de evidencia por recomendación; contexto de producto y marca; neutralizar instrucciones inyectadas en copys o archivos; presupuestos de coste de inferencia. Mantener reglas de presupuesto fuera del modelo. Instrumentar experimentos y evaluación humana antes de afirmar mejoras.

Criterio de salida: conjunto de evaluación versionado, revisión de errores y utilidad documentada. Una respuesta inválida nunca origina ejecución.

## Etapa 4 · Escrituras supervisadas

Permisos y revisión de Meta; prevalidación y creación inicial en PAUSED; preview de payload; aprobación vinculada a hash inmutable, monto, cuenta y caducidad; claves de idempotencia y reconciliación; outbox y cola durable; límite diario/total, cooldown, kill switch, registro antes/después y recuperación parcial. No reutilizar el endpoint de simulación para publicar sin un nuevo diseño y pruebas.

Criterio de salida: pruebas en entorno autorizado sin gasto, aprobación del responsable y evaluación operacional de incidentes.

## Etapa 5 · SaaS

Facturación, límites por plan, equipos, múltiples cuentas y monedas, soporte, retención y eliminación de datos, reporting, observabilidad y pruebas de carga. Automatización limitada por políticas individuales, con alertas y reversión, solo después de demostrar la calidad de las sugerencias supervisadas.

Las etapas no tienen fechas comprometidas. No se han realizado App Review, alta de negocio, despliegue cloud ni contratación de servicios.
