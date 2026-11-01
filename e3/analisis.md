# Comparación Razonada y Análisis del Agente (E3)

**Autora:** Laura Rodríguez  
**Asignatura:** Máster en IA · Bloque 4  
**Proyecto:** Tostadero Retiro S.L.  

---

## 1. Experimentos con el Agente desde cero (`s3_agente.py`)

Al probar el agente de atención técnica programado a mano, he analizado cómo se comporta ante situaciones límite cambiando sus parámetros y sus instrucciones:

### Experimento 1: Caso base (Restaurante Lumbre)
- **Situación:** El cliente nos envía un correo donde avisa de una avería grave (la máquina no calienta y hoy no pueden dar desayunos) y además pregunta por un pedido pendiente.
- **Lo que observé en la traza:**  
  1. En el **paso 1**, el modelo no intenta hacer nada a ciegas: primero llama a `buscar_cliente('Restaurante Lumbre')` para obtener su `id: 2`.
  2. En el **paso 2**, clasifica la avería como de prioridad **alta** (siguiendo la instrucción de que el bar no puede servir café) y prepara la llamada a `crear_incidencia`.
  3. Como esa herramienta tiene configurado `requiere_aprobacion=True`, el script se detiene y me pide confirmación en la consola: `¿Aprobar crear_incidencia(...) [s/N]?`.
  4. Al pulsar `s`, se registra la incidencia (#4) y en el mismo turno consulta `consultar_pedidos(cliente_id=2)`.
  5. Finalmente redacta una respuesta muy clara donde le da al cliente el número de incidencia urgente y le informa de que su pedido pendiente (#1003) de 496,40 € está registrado.

### Experimento 2: Límite de pasos forzado (`max_pasos=2`)
- **Situación:** Reduje el límite de vueltas del agente a solo 2 pasos con `Agente(SISTEMA, herramientas, max_pasos=2)`.
- **Lo que ocurrió:** El agente usó el paso 1 para buscar al cliente y el paso 2 para ejecutar las herramientas de avería y pedidos. Pero como el bucle `for` terminó ahí, no le quedó ningún paso disponible para redactar el mensaje de respuesta.
- **Resultado:** Saltó el mensaje de seguridad que dejamos programado: *"He alcanzado el límite de pasos sin terminar. Paso el caso a una persona."*.  
- **Mi conclusión:** Me parece una salvaguarda básica para cualquier aplicación real. Si no le pones un tope de pasos, un modelo confundido podría entrar en un bucle infinito llamando a herramientas una y otra vez y gastando saldo sin parar.

### Experimento 3: Rechazar la aprobación humana (`n`)
- **Situación:** Cuando el agente me pidió permiso para crear la incidencia, pulsé `n` para ver si insistía o se rompía el programa.
- **Lo que ocurrió:** El programa le devolvió a Claude el mensaje: `"Un operador humano ha rechazado esta acción. No la repitas."` marcado como error (`is_error: True`).
- **Comportamiento del modelo:** Me sorprendió para bien: el agente no se quedó pillado ni volvió a intentar llamar a la herramienta. Leyó el rechazo como un dato más, contestó con total normalidad a la duda del pedido pendiente y le explicó al cliente que la avería pasaría a revisión manual por parte de un técnico.
- **Mi conclusión:** Tratar los errores o rechazos como datos dentro del historial de la conversación es fundamental para que el agente sepa reaccionar con sentido común en lugar de lanzar una excepción y cerrarse.

### Experimento 4: Quitar la advertencia en `crear_incidencia`
- **Situación:** Quité de la descripción de la herramienta la frase *"Úsala solo si el cliente describe una avería concreta"* y le pregunté: *"¿Revisáis las máquinas en agosto?"*.
- **Lo que ocurrió:** El agente buscó la ficha del cliente, pero tuvo suficiente criterio para no crear ninguna avería. Se dio cuenta de que una pregunta sobre mantenimiento preventivo no es una avería y contestó explicando cómo pedir cita.
- **Mi conclusión:** Aunque Claude Haiku supo distinguir el contexto, tener descripciones sueltas o ambiguas es muy peligroso con modelos más pequeños, porque tienden a llamar a herramientas innecesarias a la mínima palabra clave que leen.

### Experimento 5: Quitar la regla de identificar al cliente en `SISTEMA`
- **Situación:** Quité del prompt la instrucción explícita de *"1. Identifica al cliente con buscar_cliente antes de usar su id"*.
- **Lo que ocurrió:** Si el correo no trae datos suficientes, el agente se para y pide aclaraciones al cliente por texto antes de lanzarse a la piscina. Y si el correo sí menciona el modelo de la máquina, se apoya en la descripción de la herramienta en `DEFINICIONES` como red de seguridad para buscar el cliente primero.
- **Mi conclusión:** El prompt del sistema y las descripciones de las herramientas se ayudan mutuamente. Aun así, dejar el procedimiento paso a paso bien marcado en el prompt del sistema ahorra muchas dudas y pasos en falso al modelo.

---

## 2. Comparación razonada: Agente desde cero frente a LangChain (P3)

Habiendo probado ambas implementaciones (`s3_agente.py` y `s3_agente_langchain.py`) sobre el mismo caso de atención técnica, esta es la comparativa entre los dos enfoques:

| Característica | Agente desde cero (`s3_agente.py`) | Agente con LangChain (`s3_agente_langchain.py`) |
| :--- | :--- | :--- |
| **Líneas de código** | ~94 líneas | ~59 líneas (un 35% menos) |
| **Transparencia del bucle** | **Total:** Ves cada iteración, puedes imprimir el razonamiento intermedio con un simple `print` y sabes exactamente qué pasa. | **Caja negra:** El bucle de ejecución está metido dentro de LangGraph. Sabes lo que entra y lo que sale, pero el proceso interno está oculto. |
| **Control de pausas y aprobación** | Muy manual y sencillo: un `if h.requiere_aprobacion:` que hace un `input()` directo en consola. | Arquitectura profesional: usa un grafo de estados que se interrumpe (`interrupt_on`) y un checkpointer (`InMemorySaver`) para guardar y reanudar el estado con un `thread_id`. |
| **Definición de herramientas** | Escribes a mano el esquema JSON o usas adaptadores por cada dialecto. | Mucho más cómodo: pones el decorador `@tool` encima de tu función Python y LangChain genera los esquemas automáticamente a partir del tipado. |
| **Cambio de proveedor** | Tienes que escribir el código del SDK de cada marca si cambias de OpenAI a Claude o Gemini. | Muy fácil: cambias una cadena de texto (ej: `"anthropic:..."` por `"openai:..."`). |
| **Dependencias y depuración** | **Mínimas:** Solo dependes de la librería oficial de Anthropic. Si algo falla, el error te lleva directo a tu línea de código. | **Muchas:** Arrastra muchas librerías (`langchain`, `langgraph`, `langchain-core`). Cuando sale un error interno, la traza de fallo tiene cientos de líneas y es más difícil de entender. |

### Mi valoración: ¿Cuál elegiría para un proyecto real?

Si tuviera que elegir uno para ponerlo en producción en una empresa como Tostadero Retiro:

1. **Para empezar o para proyectos sencillos:** Prefiero la versión **desde cero**. Me parece mucho más limpia y me da la seguridad de entender cada paso que da el modelo sin intermediarios. Además, si algo se rompe, sé exactamente qué línea de mi código ha sido sin tener que pelearme con la documentación de un framework que cambia de versión cada pocos meses.
2. **Para sistemas grandes con usuarios reales:** Elegiría **LangChain / LangGraph**. Aunque al principio cueste más entenderlo, el concepto de pausar el agente mediante un *checkpointer* (`InMemorySaver` o una base de datos) es indispensable en la vida real. En un entorno web real no puedes dejar un script de Python congelado esperando un `input()` de consola; necesitas guardar el estado en una base de datos, mandarle un aviso al operador humano y, cuando este apruebe la acción horas después desde una web, reanudar la ejecución desde ese mismo punto usando el `thread_id`.

---

## 3. Enrutador híbrido y medición de ahorro (P4)

En la práctica 4 comprobamos que **no todos los correos necesitan pasar por un agente**. Un agente es flexible pero muy caro y lento: requiere varias llamadas encadenadas, envía las definiciones de herramientas en cada turno y consume miles de tokens.

Para optimizar el sistema, monté un enrutador en `s3_enrutador.py` que combina el clasificador rápido de la sesión 2 con el agente de la sesión 3:
- Si el correo es una **`consulta`**, se deriva directamente a un modelo rápido y barato (`LLM("openai")` con `gpt-5.4-mini`) en una sola llamada simple sin herramientas.
- Si es un **`pedido`**, **`incidencia`** o **`mixto`**, se envía al agente completo para que use las herramientas y la base de datos.

### Medición real con los 15 casos de la Sesión 2:

Analicé el impacto de pasar los 15 casos de prueba de la sesión anterior por este enrutador:
- De los 15 correos, **4 fueron clasificados como `consulta` pura** (un 26,7% del volumen total).
- **Camino barato (por correo de consulta):** Gasta únicamente **44 tokens de entrada** y **29 tokens de salida** (73 tokens en total), respondiendo en menos de 1 segundo con 1 sola llamada.
- **Camino agéntico (si hubiéramos usado el agente para esas consultas):** Habría consumido de media **~2.500 tokens de entrada** y **~150 tokens de salida** a lo largo de 2 llamadas.

**Conclusión del ahorro:** En esas consultas simples, el enrutador reduce el consumo de tokens en un **97%**. Sobre el total de correos recibidos por el tostadero, poner este filtro delante reduce de golpe más de una cuarta parte del gasto total del sistema sin perder ni un ápice de calidad en la atención técnica.
