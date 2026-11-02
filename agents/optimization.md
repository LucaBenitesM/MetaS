# Optimización

Responsabilidad: reglas, revisiones, aplicación local e invariantes monetarias. Coordinar propiedad de `strategy.py`, `main.py` y `worker.py` con backend/ai-strategy.

Evaluar nunca modifica campañas. El worker solo propone. Aplicar exige owner, aprobación, versión vigente y presupuesto agregado validado bajo bloqueo de empresa en PostgreSQL. Aplicación repetida no puede duplicar efectos ni auditoría. Cambiar reglas invalida aprobaciones anteriores. Montos enteros y ninguna llamada externa.

Entrega: tests de datos insuficientes, límites, rechazo, idempotencia, revisión obsoleta y concurrencia PostgreSQL. Explicar por qué las señales no prueban rentabilidad ni significancia; documentar retrasos de atribución y cooldown como trabajo posterior.
