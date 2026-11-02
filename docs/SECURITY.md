# Seguridad y límites de la demo

## Modelo de acceso

La demo permite seleccionar públicamente dos empresas y dos roles sembrados. Es una forma de probar autorización, **no de acreditar identidad**. Cualquier persona con acceso al servidor puede iniciar una sesión de cualquiera de esos espacios. Mantener el servicio en loopback y usar solo datos ficticios. El servidor rechaza `APP_MODE` distinto de `demo` para impedir confundir esta entrega con una configuración comercial.

Las sesiones son tokens aleatorios de 48 bytes, transportados en `Authorization: Bearer`. La DB guarda únicamente SHA-256 y vencimiento UTC (ocho horas por defecto). La pestaña conserva el token en `sessionStorage`. Cerrar sesión revoca todas las sesiones del mismo miembro de demo, pues ese miembro es compartido. No hay contraseña real que pueda filtrarse.

El token de cliente es accesible a JavaScript: una vulnerabilidad XSS podría robarlo. Antes de producción hay que incorporar identidad verificada, sesiones HttpOnly/BFF y política CSP adecuada. React escapa los textos; no se renderiza HTML de los anuncios. CORS admite solo los orígenes configurados y no habilita cookies ni comodines.

## Aislamiento

- La sesión determina miembro y empresa; ningún parámetro del navegador puede cambiar su autoridad.
- Todas las colecciones y recursos filtran `tenant_id`. UUID ajeno responde 404.
- Las escrituras exigen `owner` en la API, incluso si el navegador se altera.
- Las relaciones de creatividades y recomendaciones tienen claves foráneas compuestas con tenant.
- No hay RLS: una cuenta privilegiada de DB puede ver todas las empresas. Implementarlo antes de exponer datos reales.
- Las pruebas incluyen lecturas/escrituras cruzadas, descarga privada, viewer, token inválido y expiración.

## Archivos

Máximo lógico de 25 MiB por archivo después del procesamiento multipart. Imágenes admitidas: PNG/JPEG/WEBP decodificables y de hasta 40 millones de píxeles. El MIME aportado por el navegador no es autoridad. SVG/HTML no se aceptan. MP4/WEBM solo se reconocen por cabecera: **no hay transcodificación, análisis de códec/duración ni garantía de validez completa de video**. El usuario debe revisarlos manualmente.

El nombre original se conserva como texto, nunca como ruta. Las rutas se generan con UUID por empresa. No existe directorio público de uploads. Las descargas pasan por autorización y se entregan como attachment con `nosniff`. Los archivos se almacenan sin cifrado específico de aplicación, dentro de un volumen local protegido por el sistema operativo.

El límite no reemplaza un límite de cuerpo HTTP en proxy: Starlette puede recibir/spool el multipart antes de que el handler lo compruebe. Antes de producción agregar proxy con límite de tamaño, rate limit, cuotas, antivirus, validación/transcodificación de video, buckets privados, URLs firmadas cortas y limpieza de huérfanos. No se afirma que esto ya exista.

## Presupuesto y cambios

No se distribuye adaptador de escritura de Meta. El endpoint de publicación devuelve 403, conexión 501, el worker solo evalúa y las variables META no se consumen. La aprobación de propuesta no crea una campaña. Las recomendaciones solo cambian datos ficticios después de dos acciones humanas.

Al aplicar aumentos se toma un bloqueo por empresa en PostgreSQL, se verifican revisión y límite agregado y se guarda auditoría en la transacción. El cambio aplicado se puede repetir sin un segundo efecto. Modificar reglas invalida recomendaciones no aplicadas. SQLite no ofrece la misma protección concurrente; no usarlo para operación comercial.

Los eventos no son un registro inmutable contra administradores de DB. No se envían a un servicio externo. La retención y exportación a un sistema de auditoría protegido quedan pendientes.

## Secretos y operación

`.env`, DB, uploads, caches y dependencias quedan fuera de Git y del ZIP. `.env.example` solo contiene valores demo. Compose no expone PostgreSQL al host y limita web/API a loopback. Las imágenes de app corren sin root. No hay integración de cobros ni telemetría externa.

Pendiente: HTTPS público, autenticación real, MFA, gestión de secretos/cifrado, RLS y rol DB restringido, protección contra abuso, escaneo de dependencias continuo, alertas, procedimientos de incidentes, backup/restore, eliminación y retención por empresa. Las credenciales demo de Compose no sirven para un despliegue público.

## Aportes de agentes e IA futura

Copys, nombres de archivo, documentos importados y respuestas externas son datos no confiables. No se deben ejecutar instrucciones encontradas allí. Un futuro modelo no puede aprobar ni enviar presupuesto: debe devolver una propuesta estructurada validada por reglas y revisada por un humano. Ningún token debe entrar en prompts, logs o capturas.
