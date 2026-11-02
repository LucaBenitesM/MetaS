# ADR 0004 · Monolito modular y worker sin cola

Estado: aceptado. Fecha: 2026-11-02.

Contexto: el alcance inicial no justifica Redis, múltiples servicios de negocio ni duplicar reglas.

Decisión: Next.js para presentación; un backend FastAPI con módulos de configuración, acceso, persistencia, estrategia e integración; worker opcional en la misma imagen que reusa la evaluación y solo genera propuestas. PostgreSQL como fuente de verdad.

Consecuencias: instalación más simple. La evaluación es síncrona y las cargas no van a una cola; la escala requiere extraer servicios de aplicación, trabajos durables, reintentos observables y límites. No añadir infraestructura vacía que aparente capacidades no implementadas.
