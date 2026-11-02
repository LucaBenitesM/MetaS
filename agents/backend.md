# Backend

Responsabilidad: API FastAPI, sesiones y operaciones de negocio. Rutas sugeridas: `apps/api/app/auth.py`, `schemas.py`, `main.py` y tests de workflows; coordinar propiedad de main/schemas con el orquestador.

Usar dependencias de sesión/rol, obtener tenant desde el servidor, devolver 404 para recursos ajenos y errores consistentes. No añadir llamadas a Meta ni alterar reglas presupuestarias sin acuerdo. Contratos explícitos de respuestas sin rutas de archivos, tokens ni secretos. Auditoría y estado en la misma transacción.

Entrega: implementación, snapshot OpenAPI, tests de autorización/aislamiento, documentación de API y migraciones si corresponden. Probar endpoints de éxito, entrada inválida, rol y acceso cruzado. No reutilizar DB del desarrollador para tests destructivos.
