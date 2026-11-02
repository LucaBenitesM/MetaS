# Preparación para Meta

## Estado exacto

No existe OAuth activo, no se leen cuentas, no se sincronizan métricas, no se publican campañas. `GET /api/integrations/meta` comunica ese estado. `/connect` responde 501 y `/publish` responde 403. El protocolo `MetaGateway` y su adaptador deshabilitado definen el punto de extensión. Las variables META de `.env.example` están reservadas y no se consumen.

No cargar un access token para intentar habilitarlo. No existe un interruptor oculto que habilite envío real.

## Trabajo de integración

1. Confirmar en documentación oficial de Meta la versión soportada, requisitos de negocio/aplicación, permisos por operación, nivel de acceso, revisión y políticas aplicables. No se fija una versión de Graph API sin esa verificación.
2. Implementar OAuth del lado servidor con state aleatorio, vínculo con la sesión y la empresa, vencimiento y consumo único; callback HTTPS autorizado. Validar selección de cuentas y activos accesibles. No derivar tenant del callback enviado por el navegador.
3. Guardar tokens cifrados con claves externas al repositorio, vencimiento, permisos, identidad de cuenta y revocación. Nunca logs de tokens. Añadir desconexión y eliminación de datos.
4. Empezar con lectura: ad accounts, campaigns, ad sets, ads e Insights. Guardar origen, moneda, zona horaria, ventana de atribución y fecha de extracción. Manejar paginación, rate limits, reintentos con backoff y errores permanentes.
5. Separar sincronización de recomendaciones. No tratar falta de datos o atribución incompleta como gasto sin ventas confirmado.
6. Para escrituras futuras diseñar aprobación vinculada al payload, cuenta, monto y vencimiento; crear en PAUSED, implementar idempotencia y reconciliación. Probar primero con activos y condiciones autorizadas sin gasto.

No utilizar el modelo para construir payloads arbitrarios ni aceptar identificadores de cuenta sin comprobar su pertenencia. Mantener el presupuesto y la elegibilidad como validaciones de servidor.

## Referencias oficiales

- [Marketing API: autorización](https://developers.facebook.com/docs/marketing-api/overview/authorization/)
- [Marketing API: documentación](https://developers.facebook.com/docs/marketing-apis/)
- [SDK oficial de Meta](https://github.com/facebook/facebook-python-business-sdk)
- [App Review](https://developers.facebook.com/docs/app-review/)

Las condiciones de acceso deben verificarse al implementar la integración. Esta entrega no afirma haber completado esos requisitos.
