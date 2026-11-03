# Meta Ads AI

MVP ejecutable de un SaaS multiempresa para organizar anuncios, planificar campañas y revisar optimizaciones. Interfaz en español con Next.js, API FastAPI, PostgreSQL, migraciones Alembic y pruebas automatizadas.

**Estado: demo funcional v0.1. No está conectado a Meta. No publica anuncios ni genera gasto.** El motor actual usa reglas determinísticas explicables; no consulta un LLM, tendencias actuales ni datos reales. La conexión OAuth, la IA generativa y la operación comercial siguen pendientes.

## Arranque recomendado: Docker

Requisitos: Docker Desktop con Docker Compose v2, puertos 3000 y 8000 libres y conexión a Internet para descargar imágenes y dependencias la primera vez.

Desde la carpeta raíz `meta-ads-ai`:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

En macOS/Linux, el primer comando es `cp .env.example .env`.

- Aplicación: http://localhost:3000
- API interactiva: http://localhost:8000/docs
- Salud: http://localhost:8000/health

La API espera a PostgreSQL, aplica migraciones y crea los datos ficticios al iniciar. Elegí Cristal o Norte y el rol administrador o lector. El seed es idempotente: reiniciar conserva los cambios. Los datos y archivos persisten en volúmenes separados. PostgreSQL no se expone al host; la web y API solo se publican en loopback.

Para detenerlo sin borrar datos:

```text
docker compose down
```

Para ver errores:

```text
docker compose logs --tail=100 api web db
```

El perfil opcional genera recomendaciones cada 15 minutos. Nunca aprueba ni aplica cambios:

```text
docker compose --profile optimizer up --build -d
```

Si cambiás usuario, contraseña o nombre de PostgreSQL, actualizá también `DATABASE_URL`. Los valores de `.env.example` son exclusivos del demo local. No uses credenciales reales. No abras esta demo a Internet.

## Desarrollo sin Docker

Requisitos: Python 3.12+, Node.js 24 LTS y npm. PostgreSQL 17 recomendado; SQLite está soportado para explorar y ejecutar las pruebas rápidas. Docker no estaba disponible en el entorno de entrega: se probaron el frontend, la API y PostgreSQL directamente; la composición de contenedores se comprueba también en CI.

En PowerShell, desde la raíz:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r apps/api/requirements-dev.txt
Set-Location apps/api
..\..\.venv\Scripts\python.exe -m alembic upgrade head
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Esto usa `apps/api/demo.db` (SQLite) si no hay `DATABASE_URL`. En una segunda terminal, desde la raíz:

```powershell
Set-Location apps/web
npm ci
npm run dev
```

Abrí http://localhost:3000. En macOS/Linux, usá `.venv/bin/python` y rutas con `/`. Para PostgreSQL configurá, en la terminal de la API y antes de las migraciones:

```powershell
$env:DATABASE_URL='postgresql+psycopg://usuario:clave@127.0.0.1:5432/meta_ads'
```

La base debe existir. No hacen falta Redis, claves de Meta ni OpenAI. La API puede leer un `.env` en su directorio actual; Compose lee el `.env` de la raíz. No copies a la API el `DATABASE_URL` de Compose que contiene el hostname `db` si ejecutás fuera de Docker.

Si usás otro puerto web, ajustá `CORS_ORIGINS` en la API. Ejemplo: `http://localhost:3001,http://127.0.0.1:3001`. La URL pública de la API se fija con `NEXT_PUBLIC_API_URL` **antes** de compilar Next.js. No se usan fuentes ni imágenes externas.

## Recorrido de demostración

1. Entrá como administrador en Cristal. Revisá las tres campañas y los indicadores ficticios de siete días.
2. Abrí Productos. Agregá nombre, descripción, precio en UYU y margen declarado; también podés editar un producto.
3. Abrí Anuncios. Cargá un JPEG, PNG, WEBP, MP4 o WEBM de hasta 25 MiB y vinculalo a un producto. El servidor ignora el MIME declarado y revisa el archivo. Para imágenes verifica decodificación, dimensiones y proporción; para videos solo reconoce la cabecera del contenedor. El análisis indica sus límites.
4. En Planificador, elegí producto, anuncios, país, edades adultas, presupuesto diario y CPA objetivo. Los importes del formulario están en UYU; la API guarda centésimos enteros. El motor sugiere ABO/CBO, distribuye cada anuncio una vez y explica su hipótesis. No predice ventas.
5. Aprobá o rechazá una propuesta. Aprobar guarda tu decisión; no crea campañas ni reserva gasto.
6. En Optimización, evaluá las campañas. La muestra produce una propuesta de pausa y una de aumento. Primero aprobá y después aplicá la simulación. El dashboard cambia sus datos locales y Actividad conserva la evidencia.
7. En Configuración, ajustá el límite agregado y el aumento máximo (hasta 20%). Se invalidan revisiones anteriores y se requiere evaluar de nuevo.
8. Salí y entrá a Norte: los productos, archivos, propuestas y eventos son independientes. El rol lector no puede escribir aunque llame directamente a la API.

Las seis creatividades iniciales son **fichas sin archivo**: tres imágenes y tres videos. No se presentan como material real analizado. Las métricas históricas son fijas: simular una pausa no borra el gasto ficticio del período.

## Qué incluye

| Área | Implementado | Pendiente para producción |
| --- | --- | --- |
| Empresas y acceso | Dos espacios aislados, sesiones opacas con vencimiento y revocación, roles owner/viewer | Registro, invitaciones, identidad real, recuperación y MFA |
| Datos | SQLAlchemy, PostgreSQL, migración versionada, claves compuestas entre recursos de una empresa | RLS, credenciales de DB con mínimo privilegio, backups operados |
| Creatividades | Carga privada persistente, validación de imagen, reconocimiento básico de video, sugerencias técnicas | Transcodificación, antivirus, cuotas, análisis semántico multimodal |
| Catálogo | Alta y edición de productos, precio y margen | Inventario, variantes, importadores, Shopify |
| Dashboard | Métricas calculadas sobre campañas ficticias | Insights reales, ventanas de atribución, series diarias |
| Estrategia | Propuestas ABO/CBO por reglas, reparto de anuncios, briefs y explicación | LLM configurable, experimentos, medición del valor de las recomendaciones |
| Optimización | Reglas, revisión, aplicación local idempotente, límites agregados, auditoría y worker opcional | Ejecución externa, reconciliación, alertas, políticas avanzadas |
| Meta | Puerto de integración y endpoints explícitamente desconectados | OAuth completo, permisos, App Review, Marketing API y webhooks |
| Operación | Dockerfiles sin root, Compose, tests y CI | Hosting, facturación, observabilidad, soporte y recuperación |

## Pruebas y controles

Con el entorno Python instalado, desde `apps/api`:

Activá primero el entorno virtual (`.venv\Scripts\Activate.ps1` desde la raíz en PowerShell), o sustituí `python` por `..\..\.venv\Scripts\python.exe` en los comandos de este apartado. Las dependencias deben estar instaladas en ese entorno.

```text
python -m ruff check .
python -m pytest
python -m alembic upgrade head
python -m alembic check
```

Para repetir la suite sobre PostgreSQL, usá **una base vacía dedicada que termine en `_test`**:

```powershell
$env:TEST_DATABASE_URL='postgresql+psycopg://usuario:clave@127.0.0.1:5432/meta_ads_test'
python -m pytest
```

La suite elimina y reconstruye tablas dentro de esa base dedicada. Nunca apuntar a una base con datos útiles. Sin esa variable, usa SQLite en memoria. No usa ni limpia la base normal del desarrollador.

Desde `apps/web`:

```text
npm ci
npm run typecheck
npm run build
npx playwright install chromium
```

Para los tests de navegador, iniciá primero API y web con una base demo nueva (el test simula una pausa). Luego:

```text
npm run test:e2e
```

Se ejecuta el recorrido en escritorio y móvil. Podés fijar `E2E_WEB_URL` y `PLAYWRIGHT_CHROME_PATH` para usar otro puerto o un Chrome ya instalado. Para repetir sobre el mismo demo que ya fue modificado, crear una base demo nueva; no borrar datos de trabajo. Ver [VALIDATION.md](docs/VALIDATION.md) para los resultados efectivamente obtenidos y sus límites.

CI comprueba Python en SQLite/PostgreSQL, migraciones, tipos, build, navegador y el arranque de Compose. El archivo de CI está incluido; no se afirma que haya corrido en GitHub hasta que el repositorio se suba.

## Abrir en Orca

La entrega incluye la carpeta de código y un ZIP limpio. Descomprimí el ZIP y abrí **la carpeta `meta-ads-ai` completa** como proyecto local en Orca. No requiere una integración especial ni un formato propietario: es un repositorio Git convencional.

1. Leé [docs/ORCA.md](docs/ORCA.md), con comandos y un mensaje inicial listo para tu agente.
2. Indicá al agente que lea `AGENTS.md`, `README.md`, `docs/PRD.md` y `docs/ROADMAP.md`.
3. Para importar desde GitHub, usá `https://github.com/LucaBenitesM/MetaS` y la rama `main`.

No se modificó tu instalación de Orca y no se verificaron nombres de menús de una versión específica. Las instrucciones funcionan mediante carpeta local o URL Git según las opciones de tu instalación.

## Repositorio GitHub

El repositorio de trabajo elegido por el propietario es [LucaBenitesM/MetaS](https://github.com/LucaBenitesM/MetaS). El nombre del producto y de la carpeta de proyecto sigue siendo `meta-ads-ai`.

Para obtener una copia y trabajar desde Orca:

```text
git clone https://github.com/LucaBenitesM/MetaS.git meta-ads-ai
cd meta-ads-ai
```

Abrí esa carpeta en Orca, usá la rama `main` y seguí [docs/ORCA.md](docs/ORCA.md). Los archivos del proyecto se encuentran directamente en la raíz del repositorio, sin una carpeta contenedora adicional.

La entrega inicial también incluyó un ZIP sin `.git`, dependencias ni datos de ejecución. Nunca subir `.env`, bases de datos, tokens o archivos de clientes. La visibilidad y los permisos del repositorio se administran en GitHub por separado de la aplicación demo.

## Mapa del repositorio

```text
apps/api/app/          API, autenticación, modelos, reglas, seed, worker y puerto Meta
apps/api/migrations/  historial Alembic
apps/api/tests/       aislamiento, archivos, propuestas, presupuesto y estados
apps/web/app/         aplicación Next.js responsive
apps/web/lib/         cliente y tipos TypeScript
apps/web/tests/       recorrido Playwright en escritorio y móvil
packages/shared/      contrato OpenAPI exportado
agents/               responsabilidades y coordinación de agentes
docs/                 producto, arquitectura, ADR, seguridad, API y entrega
scripts/              arranque y controles para PowerShell
.github/workflows/    integración continua
```

La implementación se mantiene deliberadamente en un solo backend para no duplicar reglas entre servicios. No es un producto listo para vender: es una base ejecutable para continuar el proyecto con alcance, riesgos y contratos documentados.
