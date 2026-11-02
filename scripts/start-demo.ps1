$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
if (-not (Test-Path -LiteralPath '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
docker compose up --build -d
if ($LASTEXITCODE -ne 0) { throw 'No se pudo iniciar Docker Compose. Verificá Docker Desktop y consultá README.md.' }
Write-Output 'Demo: http://localhost:3000 | API: http://localhost:8000/docs'
