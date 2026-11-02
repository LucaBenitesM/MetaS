# ADR 0001 · Demo aislada como primera entrega

Estado: aceptado. Fecha: 2026-11-02.

Contexto: se necesita un MVP ejecutable sin credenciales y está prohibido publicar anuncios o gastar presupuesto.

Decisión: solo `APP_MODE=demo`, datos ficticios explícitos, adaptador Meta inactivo y ausencia de llamadas externas. Login público permite elegir entre empresas y roles sembrados. Los cambios se limitan a la base local. El proveedor de estrategia actual es determinístico y muestra sus límites.

Consecuencias: el producto se puede explorar sin cuenta externa. El login no constituye autenticación comercial y no puede exponerse públicamente. OAuth y una futura IA generativa son trabajo real pendiente, no conexiones simuladas como activas.
