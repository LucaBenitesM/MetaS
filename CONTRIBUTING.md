# Desarrollo

La base se entrega como demo privado para continuar. Usar una rama por cambio y revisar los invariantes de AGENTS.md. No se requiere una plataforma concreta de agentes.

Antes de un cambio de contrato, acordar ejemplos de entrada/salida, permisos, estados, errores y alcance de migración. El PR debe explicar el problema, comportamiento resultante y validación realizada. No incluir secretos ni datos reales.

Ejecutar los controles del README. Las pruebas de navegador simulan cambios y deben usar un demo desechable. Para probar PostgreSQL crear una base dedicada con sufijo `_test`; no usar una base de trabajo. Los tests no hacen llamadas a Meta.

Las mejoras de IA deben conservar esquemas y límites determinísticos. Las mejoras de Meta comienzan en lectura. Publicación real necesita una especificación separada, permisos verificados y revisión explícita; no convertir la simulación en escritura real por una variable de entorno.
