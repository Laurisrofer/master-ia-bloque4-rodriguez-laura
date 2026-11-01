<!-- Generado desde sesion-3.html con tools/sync_exercises.py. No editar a mano. -->

# P2. Experimentos con el agente

| Experimento | Qué observar | Resultado real observado |
| --- | --- | --- |
| **1. Ejecuta el correo de ejemplo** | Secuencia de herramientas, prioridad elegida y respuesta final. | Ejecuta `buscar_cliente` (ID: 2), asigna prioridad `alta` por tener el servicio de café parado, pide aprobación humana, crea la incidencia (#4), consulta pedidos (#1003 por 496,40 €) y responde a ambas consultas cordialmente. |
| **2. Fija `max_pasos=2`** | Cómo se corta y qué mensaje recibe el cliente. | Tras ejecutar las herramientas del paso 2, se agota el límite antes de redactar la respuesta final y devuelve la salvaguarda de seguridad: *"He alcanzado el límite de pasos sin terminar. Paso el caso a una persona."*. |
| **3. Rechaza la aprobación** | Cómo reacciona el modelo: ¿lo reintenta, lo explica, propone otra cosa? | Recibe el mensaje `"Un operador humano ha rechazado esta acción. No la repitas."` como dato de error. No reintenta la herramienta, respeta la decisión, contesta sobre el pedido y avisa de que el equipo técnico contactará manualmente. |
| **4. Quita «Úsala solo si el cliente describe una avería» de `crear_incidencia`** y pregunta «¿Revisáis las máquinas en agosto?» | Si crea incidencias innecesarias. | Busca al cliente pero no llega a crear la avería; distingue que es una consulta de mantenimiento preventivo y responde ofreciendo coordinar fechas con el servicio técnico. |
| **5. Quita el paso 1 del procedimiento en `SISTEMA`** | Si se inventa identificadores de cliente. | Si faltan datos no se inventa IDs; pide aclaraciones al cliente o se apoya en la descripción de la herramienta (`DEFINICIONES`) para acabar invocando `buscar_cliente`. |
