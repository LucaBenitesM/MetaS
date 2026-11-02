# ADR 0003 · Revisión y ejecución local separadas

Estado: aceptado. Fecha: 2026-11-02.

Contexto: aprobar una recomendación no debe producir efectos silenciosos y los límites pueden cambiar durante una revisión.

Decisión: estados explícitos, aprobación owner y segundo paso de simulación. Bloqueo por empresa y revisión de campaña en PostgreSQL, validación agregada del presupuesto al aplicar, aplicación idempotente y auditoría transaccional. Cambiar reglas invalida aprobaciones anteriores y habilita una nueva evaluación.

Consecuencias: las decisiones se pueden explicar y repetir de forma segura en el demo. SQLite no proporciona la misma semántica de bloqueo. Una ejecución real necesitará outbox, idempotencia externa, reconciliación y aprobaciones con hash/caducidad.
