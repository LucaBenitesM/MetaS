# Verificación de la entrega

Fecha local: 2026-11-02, America/Montevideo. Entorno: Windows, Python 3.12.10, Node 24.16.0, npm 12.2.0, PostgreSQL 17.11 y Chrome local. Los servicios y bases de validación se crearon aisladamente dentro del espacio de trabajo; no se usaron cuentas de Meta ni anuncios reales.

## Resultados

| Control | Resultado |
| --- | --- |
| API en PostgreSQL real | 40 pruebas aprobadas |
| API en SQLite en memoria | 39 aprobadas; una omitida porque requiere locks PostgreSQL |
| Concurrencia presupuestaria | Dos aumentos simultáneos: solo uno permitido si ambos superarían el límite agregado |
| Revisión de Python | `ruff check` aprobado |
| Dependencias Python | `pip check`: sin requisitos incompatibles |
| Migraciones PostgreSQL | Upgrade → downgrade base → upgrade y `alembic check` aprobados sobre base desechable |
| Migraciones SQLite | Upgrade y `alembic check` aprobados |
| Worker | Una ejecución completa evaluó los dos espacios; no aplicó cambios |
| Frontend | TypeScript y build de producción Next.js aprobados |
| Navegador | Cuatro recorridos aprobados: flujo administrador y lector, en escritorio y móvil |
| Dependencias web de producción | `npm audit --omit=dev --audit-level=high`: cero vulnerabilidades reportadas al verificar |
| OpenAPI | Snapshot generado desde la aplicación |
| Interfaz | Captura de dashboard inspeccionada visualmente |

La suite API cubre sesión ausente/inválida/vencida, revocación, lectura y escritura por tenant, autorización viewer, claves compuestas, catálogo persistente, archivos privados, MIME no confiable, archivos ilegibles y tamaño máximo, reconocimiento limitado de video, presupuestos y edades, reparto ABO/CBO, anuncios duplicados o de otro producto, revisión sin publicación, evaluación sin mutación, deduplicación, aprobación previa, aplicación idempotente, pausas, rechazo, cambios de reglas y concurrencia PostgreSQL.

Los tests de navegador cargan una imagen real de fixture, crean un producto y una propuesta, la aprueban, evalúan campañas, aprueban y aplican una pausa simulada, comprueban el dashboard, recargan la sesión y verifican la consulta del otro espacio con rol lector. Usan datos desechables: escritorio en Cristal y móvil en Norte.

## Comandos de referencia

Desde apps/api, con Python del entorno de desarrollo:

```text
python -m ruff check .
python -m pytest
python -m alembic upgrade head
python -m alembic check
python -m app.worker --once
```

Para PostgreSQL, configurar `TEST_DATABASE_URL` con una base dedicada terminada en `_test`. Se ejecutó la misma suite en ambos motores; la prueba concurrente se omite únicamente en SQLite. La reversión de migraciones se ejecutó en otra base vacía creada para ese fin.

Desde apps/web:

```text
npm run typecheck
npm run build
npm run test:e2e
npm audit --omit=dev --audit-level=high
```

En esta máquina se usó `E2E_WEB_URL=http://localhost:3001` y `PLAYWRIGHT_CHROME_PATH` para un Chrome instalado; el puerto 3000 ya estaba ocupado y se conservó su servicio. La API de prueba se configuró para esos orígenes. Los valores del proyecto entregado mantienen los puertos convencionales 3000/8000.

## Límites de la verificación

- Docker no estaba disponible: no se ejecutó Compose ni se construyeron las imágenes localmente. Se incluyen los Dockerfiles, healthchecks y un job de CI para construir/arrancar el stack; no se presenta ese job como ya ejecutado.
- GitHub CLI estaba instalado pero su token era inválido. No hay repositorio remoto creado, push ni ejecución de CI remota. El código tiene commit Git local y se entrega en ZIP limpio.
- No se verificó una instalación de Orca. La importación documentada usa carpeta o Git convencional, sin afirmar compatibilidad con menús de una versión específica.
- No se probó OAuth, Insights, escritura publicitaria, IA generativa, transcodificación de video ni autenticación comercial porque no están implementados.
- Starlette emite un aviso de deprecación por su adaptador de tests con HTTPX. Las pruebas pasan; el aviso no implica un adaptador HTTPX2 ya migrado.
- Un audit de dependencias sin avisos es una observación de esa fecha, no una certificación de seguridad.
- No se hicieron pruebas de carga, auditoría externa, RLS, backup/restore, accesibilidad formal ni despliegue público. La demo solo debe utilizar datos ficticios en un entorno local.

## Correcciones realizadas durante la validación

Se corrigieron nombres accesibles de controles, espera de hidratación del login, aislamiento de los datos de cada recorrido de navegador, invalidación de revisiones al cambiar reglas, auditoría del presupuesto anterior, límites de archivos, rutas de importación y configuración de dependencias para las imágenes. Las restricciones de creación de temporales y archivos de build de Windows se resolvieron ejecutando las comprobaciones autorizadas con sus permisos necesarios; el resultado final no depende de omitir pruebas fallidas.
