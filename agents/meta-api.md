# Integración Meta

Responsabilidad: puerto `apps/api/app/meta.py`, futura capa de integración y `docs/META_API.md`. Consultar documentación primaria vigente antes de definir versiones, permisos o payloads. Actualmente el adaptador está deshabilitado y las rutas deben conservar 501/403.

La primera etapa autorizable de integración es lectura con OAuth seguro, cuentas verificadas y tokens cifrados. Diseñar state de un solo uso, vencimiento, revocación, paginación, rate limits, atribución y procedencia. No aceptar tenant del callback ni exponer tokens en logs/cliente.

Entrega: diseño de amenazas, contrato, pruebas con respuestas controladas y estado visible. No usar cuentas reales, crear campañas ni activar gasto como validación del demo. La publicación requiere una etapa y aprobación separadas; un archivo con métodos no equivale a integración completada.
