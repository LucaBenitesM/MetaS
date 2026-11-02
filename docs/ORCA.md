# Continuar en Orca

Este proyecto es código fuente convencional. No contiene ni requiere credenciales de Orca. No se utilizó una API de Orca ni se comprobó una versión específica de su interfaz.

## Importación local

1. Descargá y extraé `meta-ads-ai.zip`. Conservá la estructura completa y los archivos ocultos `.github`, `.gitignore` y `.env.example`.
2. En Orca usá su opción de abrir una carpeta/proyecto local y seleccioná la raíz que contiene `README.md`, `AGENTS.md` y `compose.yaml`.
3. Abrí una terminal en esa raíz. Para confirmar la carpeta:

```text
git status
```

Si el ZIP no tiene `.git`, inicializalo:

```text
git init -b main
git add .
git commit -m "feat: MVP demo de Meta Ads AI"
```

4. Ejecutá el arranque Docker del README. Si no tenés Docker, seguí el arranque con Python/Node. El demo no pide claves externas.
5. Dales al agente los archivos de contexto y una tarea acotada. No hace falta pegar la conversación original: el PRD, roadmap y ADR representan el alcance final.

## Importación por GitHub

Si tu instalación trabaja solo con remotos, autenticá GitHub y creá el repositorio privado con los comandos del README. Importá su URL privada desde Orca con tu cuenta autorizada. No se inventó ni reservó una URL remota en esta entrega.

## Mensaje inicial para el agente

```text
Trabajás en meta-ads-ai, un MVP multiempresa de Meta Ads en modo demo.
Primero leé AGENTS.md, README.md, docs/PRD.md, docs/ARCHITECTURE.md,
docs/SECURITY.md, docs/ROADMAP.md y docs/VALIDATION.md.
El estado implementado está en esos documentos; no asumas integración activa con Meta.
Instalá las dependencias y ejecutá los checks del README antes de modificar.
Mantené el modo demo y la publicación real bloqueada. No uses credenciales,
no crees campañas externas y no gastes presupuesto.
Para la siguiente etapa empezá por proponer el contrato y las pruebas de
identidad real y memberships multiempresa. Conservá las pruebas de aislamiento.
Explicá el cambio, ejecutá las pruebas pertinentes y actualizá los documentos.
Si coordinás varios agentes, seguí agents/orchestrator.md y asigná rutas exclusivas.
```

## Varios agentes

La carpeta `agents/` contiene responsabilidades, rutas sugeridas y criterios de entrega. El orquestador asigna una tarea por rama/worktree, acuerda contratos antes de cambios cruzados y integra después de pruebas. No son agentes persistentes ya desplegados ni una configuración propietaria de Orca: son instrucciones portables para el sistema de agentes que elijas.

Primera tarea sugerida: identidad real y memberships, sin habilitar todavía Meta. Segunda: almacenamiento gestionado y procesamiento seguro de archivos. Tercera: OAuth y sincronización únicamente en lectura, tras validar requisitos de Meta. Evitar desarrollar publicación y autenticación a la vez sin un contrato y revisión de amenazas.
