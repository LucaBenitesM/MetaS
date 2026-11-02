# Producto y criterios de aceptación

## Problema

Una pequeña empresa dispone de anuncios y presupuesto pero carece de un proceso consistente para elegir estructura, revisar resultados y controlar cambios. El producto reúne contexto comercial, biblioteca creativa, propuestas y revisión de optimizaciones. No promete una estrategia óptima universal ni rentabilidad garantizada.

## Usuarios

- Owner: administra catálogo, carga anuncios, genera planes, cambia límites y revisa acciones.
- Viewer: consulta únicamente los recursos de su empresa.
- En el demo los accesos son públicos y compartidos; no representan identidad real.

## Alcance de v0.1

Dos empresas sembradas sin credenciales; sesión persistida en una pestaña; dashboard de ejemplo; alta y edición de productos; carga privada de anuncios; análisis técnico; propuestas ABO/CBO explicadas; revisión y simulación de optimizaciones; eventos de auditoría; evaluación periódica opcional. Persistencia PostgreSQL en Compose y alternativa SQLite local.

## Historias y aceptación

1. Como administrador, puedo cargar un anuncio y asociarlo solo a un producto de mi empresa. Un archivo ilegible devuelve 422; otro tenant recibe 404 al intentar descargarlo. La interfaz informa qué se analizó.
2. Como administrador, puedo proponer una campaña con uno a veinte anuncios de un producto. Ninguno queda fuera ni se duplica; los presupuestos ABO suman exactamente el diario en centésimos. CBO conserva un único presupuesto de campaña.
3. Como anunciante, veo por qué se propone ABO/CBO y puedo rechazarlo. Aprobar una propuesta solo registra la decisión. La publicación real devuelve 403.
4. Como administrador, evalúo campañas sin modificarlas. Dos evaluaciones de la misma revisión no duplican recomendaciones.
5. Para simular una recomendación, debo aprobarla primero. Aplicarla dos veces no duplica el cambio. Un aumento fuera del límite agregado devuelve 409. Cambiar reglas invalida revisiones anteriores.
6. Como lector, no puedo mutar por interfaz ni API. Como integrante de otra empresa, no puedo acceder a recursos ajenos aunque conozca sus UUID.
7. Como equipo, podemos seguir la actividad de nuestra empresa. Las decisiones registran actor, recurso, fecha y detalle local.
8. Como desarrollador, puedo levantar el proyecto, ejecutar pruebas e importarlo como carpeta o repositorio Git en Orca.

## Reglas iniciales, configurables parcialmente

- No sugerir acciones sobre campañas pausadas, con menos de tres días o menos de 100 UYU gastados.
- Pausa: cero compras y gasto de al menos dos presupuestos diarios.
- Aumento: al menos diez compras y ROAS de al menos 3; incremento máximo de 20%, configurable entre 1 y 20%.
- La suma de presupuestos diarios activos simulados no debe superar el límite de la empresa al aplicar aumentos.
- Estas condiciones son heurísticas de producto para el demo. No son recomendaciones de Meta ni evidencia de significancia estadística. No descuentan retrasos de atribución ni devoluciones.

## Fuera de alcance

Autenticación comercial, altas de empresas reales, cobros, manejo de tokens Meta, envío de campañas, sincronización de Insights, catálogo externo, atribución real, análisis semántico de videos, optimización autónoma, inteligencia competitiva y recomendaciones basadas en tendencias actuales.

## Medición futura

Evaluar tasa de propuestas útiles según revisión humana, rechazos explicados, errores de atribución, incidentes de presupuesto, aislamiento y tiempo hasta la primera propuesta. Medir rendimiento publicitario mediante experimentos, sin atribuir a la herramienta mejoras no demostradas. En v0.1 no se recolecta telemetría externa.
