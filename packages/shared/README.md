# Contratos compartidos

`openapi.json` es el snapshot generado desde `app.main.app.openapi()` en la entrega. El contrato vivo se sirve en `/openapi.json`. Regenerarlo después de cambiar rutas/esquemas y revisar el diff.

Desde apps/api:

```text
python ../../scripts/export_openapi.py
```

Los tipos de presentación están en `apps/web/lib/types.ts`. No se comparten modelos ORM con el navegador. Una futura generación de cliente debe partir de OpenAPI y conservar los tests de errores y permisos.
