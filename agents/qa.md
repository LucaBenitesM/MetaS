# Calidad

Responsabilidad: `apps/api/tests`, `apps/web/tests`, CI y `docs/VALIDATION.md`; coordinar para no editar tests ajenos activos. Usar bases desechables y archivos ficticios.

Probar el comportamiento, incluidos accesos cruzados, viewer por API, expiración, archivos inválidos, reparto de anuncios, límites agregados, transiciones y no publicación. Usar PostgreSQL para validar locks y concurrencia. Ejecutar navegador en escritorio/móvil y comprobar errores visibles y persistencia.

Reportar comandos, resultados y pruebas omitidas. Diferenciar build local, CI definida y CI efectivamente ejecutada. No marcar Docker como validado si solo se inspeccionó YAML. No hacer cambios en Meta, gastar presupuesto ni instalar integraciones con credenciales para aprobar QA del demo.
