$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location "$projectRoot/apps/api"
try {
    python -m ruff check .
    if ($LASTEXITCODE -ne 0) { throw 'Falló revisión de Python' }
    python -m pytest
    if ($LASTEXITCODE -ne 0) { throw 'Fallaron pruebas de API' }
} finally { Pop-Location }
Push-Location "$projectRoot/apps/web"
try {
    npm.cmd run typecheck
    if ($LASTEXITCODE -ne 0) { throw 'Falló TypeScript' }
    npm.cmd run build
    if ($LASTEXITCODE -ne 0) { throw 'Falló compilación web' }
} finally { Pop-Location }
