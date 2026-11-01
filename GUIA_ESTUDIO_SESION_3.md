# Mis Apuntes: Sesión 3 · Agentes de IA, Bucle Agéntico y LangChain

Máster en IA · Bloque 4: Agentes y LLMs  
Caso práctico: Tostadero Retiro S.L.

---

## 1. Conceptos clave explicados con mis palabras

* **Agente de IA:**  
  Un modelo de lenguaje al que le damos un objetivo y herramientas, y él solito decide qué pasos dar, en qué orden, evalúa las respuestas que recibe y repite el proceso hasta que termina el trabajo.
* **Bucle Agéntico (*Agentic Loop*):**  
  El ciclo continuo que hace el agente: `Pensar -> Llamar a una herramienta -> Leer el resultado -> Pensar si necesita algo más o si ya puede contestar`.
* **Límite de pasos (*Max Steps / Circuit breaker*):**  
  Un tope de seguridad (`max_pasos=8`). Si el modelo entra en bucle o se lía, se corta de forma limpia para no quemar tokens ni quedarse colgado.
* **Aprobación Humana (*Human-in-the-Loop* o HITL):**  
  Frenar al agente antes de que haga algo delicado (como modificar datos en SQLite) y pedir confirmación por consola (`[s/N]`). Si el humano dice que no, la acción no se ejecuta.
* **Checkpointer / Estado del Grafo:**  
  Una "foto" que guarda la memoria del agente (`InMemorySaver`). Permite pausar la ejecución a la espera del humano y reanudarla justo donde se quedó usando un identificador (`thread_id`).
* **Enrutador (*Router*):**  
  Un desvío inteligente al principio del flujo. Clasifica el correo entrante: si es una pregunta simple, la responde un modelo rápido y barato; si es un problema técnico, lo manda al agente completo.

---

## 2. Diferencia entre la Sesión 2 y la Sesión 3

En la **Sesión 2** vimos *Function Calling* básico: el modelo pedía una función y se la ejecutábamos.  
En la **Sesión 3** construimos un **Agente real** porque tiene cuatro mejoras clave de control y seguridad:
1. **Herramientas declarativas con permisos:** Cada herramienta sabe si es de lectura o si requiere autorización previa (`requiere_aprobacion=True`).
2. **Errores devueltos como datos:** Si una función da error o el humano rechaza la acción, el programa no peta con una excepción: le pasa el texto del error al modelo con `is_error: True` para que razone y busque otra salida.
3. **Pausa y reanudación:** El flujo puede congelarse a la espera de confirmación y reanudarse después.
4. **Condición de parada segura:** Termina cuando el modelo da su respuesta final (`stop_reason != "tool_use"`) o cuando salta el límite de pasos.

---

## 3. Mi agente desde cero (`s3_agente.py`)

Estructura de la clase `Agente`:
- **`__init__`**: Guarda el cliente de Claude (`anthropic.Anthropic()`), el modelo (`claude-haiku-4.5`), el prompt del sistema, el límite de pasos y el diccionario de herramientas disponibles.
- **`_definiciones`**: Transforma las herramientas al formato JSON que pide la API de Messages de Claude (`name`, `description`, `input_schema`).
- **`_ejecutar`**: Comprueba si la herramienta requiere aprobación humana (`input(...)`). Si se rechaza, devuelve un aviso. Si se aprueba, la ejecuta dentro de un `try/except` para capturar cualquier fallo de la base de datos y devolvérselo al modelo como dato.
- **`ejecutar`**: El bucle `for paso in range(1, self.max_pasos + 1)`. Envía los mensajes al modelo, muestra el razonamiento visible, ejecuta las llamadas a herramientas que pida el modelo y las acumula en el historial hasta que llega la respuesta final.

---

## 4. Resultados de los 5 experimentos que probé (P2)

1. **Caso Lumbre (avería + pedido):**  
   El agente busca primero al cliente (ID 2), razona que al estar la cafetera rota la avería es urgente (prioridad alta), se frena a pedirme confirmación por consola, guarda la incidencia (#4), consulta los pedidos pendientes (#1003 por 496,40 €) y responde a ambas cosas de forma clara.
2. **Límite de pasos forzado (`max_pasos=2`):**  
   Usa el paso 1 para buscar el cliente y el paso 2 para ejecutar las herramientas. Como se le agota el bucle antes de redactar el mensaje final, salta el mensaje de seguridad: *"He alcanzado el límite de pasos sin terminar. Paso el caso a una persona."*. Evita que se quede en un bucle infinito.
3. **Rechazar la aprobación humana (`n`):**  
   Le devolví el mensaje `"Un operador humano ha rechazado esta acción. No la repitas."`. El modelo lo leyó, no insistió en crear la avería, respondió a la duda del pedido pendiente y avisó de que un técnico contactaría manualmente.
4. **Quitar la advertencia en `crear_incidencia`:**  
   Al preguntar *"¿Revisáis las máquinas en agosto?"*, el modelo no creó ninguna avería porque supo distinguir entre una duda de mantenimiento y una rotura real. Aun así, relajar las descripciones en modelos más pequeños suele provocar falsos positivos.
5. **Quitar el paso 1 en `SISTEMA`:**  
   Al quitar la orden explícita de buscar primero al cliente, el agente no se inventó identificadores: se detuvo a pedir datos o recurrió a la descripción de la herramienta como salvavidas.

---

## 5. El agente con LangChain (`s3_agente_langchain.py`)

Cómo cambia la implementación con el framework:
- Se usa **`create_agent(...)`** de LangChain y el decorador **`@tool`**, que saca los esquemas automáticamente a partir del tipado de Python (`texto: str`, `cliente_id: int`).
- El control de pasos y la pausa se meten mediante **middleware**:
  - `HumanInTheLoopMiddleware(interrupt_on={"crear_incidencia": True})`: Interrumpe el flujo cuando el modelo quiere registrar una avería.
  - `ModelCallLimitMiddleware(run_limit=8)`: Pone el tope de 8 pasos.
- **`InMemorySaver()`**: El checkpointer que guarda el estado de la conversación. Cuando el grafo se interrumpe (`__interrupt__`), me pide la aprobación y se reanuda con `Command(resume={"decisions": ...})` usando el `thread_id`.

---

## 6. Comparativa: Agente desde cero vs LangChain

| Característica | Desde cero (`s3_agente.py`) | Con LangChain (`s3_agente_langchain.py`) |
| :--- | :--- | :--- |
| **Líneas de código** | ~94 líneas | ~59 líneas |
| **Transparencia** | **Total:** Ves cada vuelta del bucle con un simple print. | **Caja negra:** El bucle corre dentro del motor de LangGraph. |
| **Control de pausas** | Básico: un `if` con `input()` síncrono por consola. | Profesional: grafos de estado con pausas y reanudaciones mediante checkpoints. |
| **Dependencias** | Mínimas: solo la librería oficial de Anthropic. | Muchas: `langchain`, `langgraph`, `langchain-core`... |
| **Cuándo usar cada uno** | Para prototipos, aprender y tener control milimétrico. | Para aplicaciones web reales con miles de usuarios y aprobaciones asíncronas. |

---

## 7. El enrutador híbrido y ahorro de costes (`s3_enrutador.py`)

No todos los correos necesitan un agente. Un agente tarda varios segundos y gasta miles de tokens porque manda todas las herramientas en cada vuelta.

Para resolverlo, monté el enrutador en `s3_enrutador.py`:
- Si entra una **`consulta` simple**, se desvía al camino barato (1 sola llamada con `gpt-5.4-mini` sin herramientas).
- Si entra una **`avería` o `pedido`**, se activa el agente técnico completo con acceso a SQLite y aprobación humana.

### Datos reales medidos con los 15 casos de la Sesión 2:
- De los 15 correos de prueba, **4 eran consultas sencillas** (el 26,7% del total).
- Por el camino barato gastaron **44 tokens de entrada y 29 de salida** (~73 tokens por consulta, menos de 1 segundo).
- Si hubieran pasado por el agente, habrían gastado **~2.700 tokens** en 2 vueltas.
- **Ahorro:** Un **97% de tokens** en las consultas simples, reduciendo en más de un 25% el gasto total de la empresa.

---

## 8. Preguntas clave para repasar antes de clase

### ¿Por qué en `_ejecutar()` devolvemos una tupla `(resultado, es_error)` en vez de lanzar un error con `raise`?
Porque si lanzo un `raise Exception`, el programa de Python se cae y se corta la conversación. Al devolverlo como dato con `is_error: True`, el error viaja al historial de Claude. Así el modelo se entera de lo que ha fallado (o de que he rechazado la acción) y puede reaccionar con sentido común sin romper nada.

### ¿Para qué sirve el parámetro `max_pasos`?
Es un interruptor de seguridad (*circuit breaker*). Si el agente se confunde y entra en un bucle repitiendo la misma herramienta, `max_pasos` evita que se quede colgado gastando saldo. Cuando llega al tope, se para limpiamente y avisa de que el caso pasa a un humano.

### ¿Qué diferencia hay entre la pausa humana de `s3_agente.py` y la de LangChain?
En `s3_agente.py` es un `input()` síncrono de consola: el programa se queda congelado esperando a que yo pulse una tecla. En LangChain se usa un grafo con un *checkpointer* (`InMemorySaver`): cuando llega a la herramienta sensible se pausa y guarda todo el estado bajo un `thread_id`. Eso permite reanudarlo más tarde, algo imprescindible en una web real donde la aprobación puede tardar horas.

### ¿Cómo sabe el modelo qué herramientas necesitan aprobación?
El modelo no lo sabe; lo controlamos en Python. En la clase `Herramienta` marcamos `requiere_aprobacion=True` solo para `crear_incidencia`. Cuando Claude pide ejecutar esa función, nuestro método `_ejecutar()` la intercepta y me pide confirmación antes de tocar la base de datos.

### ¿Qué pasa si quitas el paso 1 del procedimiento en el prompt?
Comprobé que Claude no se inventa identificadores a lo loco: si le faltan datos para llamar a la herramienta, se para y pide aclaraciones al cliente, o usa la descripción de la propia herramienta como red de seguridad para buscar el cliente primero.

### ¿Por qué poner un enrutador delante del agente?
Por pura eficiencia. Un agente multi-paso tarda más y consume miles de tokens. Si un cliente solo pregunta una duda básica de horarios o facturas, el enrutador lo resuelve en un segundo con una sola llamada barata de 70 tokens, reservando el agente caro solo para averías y pedidos complejos.

### ¿Qué archivos forman mi entrega E3?
En la carpeta `e3/` están los 4 archivos completos:
1. `s3_agente.py`: el agente desde cero en Python puro.
2. `s3_agente_langchain.py`: el agente montado con LangChain y LangGraph.
3. `s3_enrutador.py`: el enrutador híbrido para optimizar costes.
4. `analisis.md`: la comparación razonada de una página con los experimentos, la tabla comparativa y la medición real de ahorro.
