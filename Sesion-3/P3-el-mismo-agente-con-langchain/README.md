<!-- Generado desde sesion-1.html con tools/sync_exercises.py. No editar a mano. -->

# P3. El mismo agente con LangChain

Con `create_agent`, el bucle lo pone el framework y el control se añade con middleware. La aprobación humana necesita un *checkpointer*, porque pausar consiste en guardar el estado del grafo y reanudarlo después.

Código: [`s3_agente_langchain.py`](s3_agente_langchain.py)

---

## Comparativa entre ambas versiones

- **Líneas de código:**  
  - Agente desde cero: ~94 líneas.  
  - Con LangChain: ~59 líneas (35% menos de código).
- **Qué viene resuelto:**  
  - Pausa y reanudación asíncrona mediante grafos de estado (LangGraph) y un *checkpointer* (`InMemorySaver`).
  - Límite de llamadas con un middleware estándar (`ModelCallLimitMiddleware`).
  - Cambio de proveedor con una sola cadena (`anthropic:...` o `openai:...`).
  - Decorador `@tool` que infiere esquemas JSON directamente a partir del tipado de Python.
- **Qué se pierde:**  
  - **Visibilidad del bucle:** El proceso interno es una caja negra; no se puede inspeccionar fácilmente el razonamiento paso a paso con un simple `print`.
  - **Control fino:** El formato interno de mensajes y eventos queda supeditado a las abstracciones de LangChain, aumentando la dificultad de depuración ante errores inesperados.

---

Para cambiar de proveedor basta la cadena del modelo: `"openai:google/gemini-3.8-flash"` (u otro modelo de OpenRouter con herramientas) funciona con la misma clave, porque `langchain-openai`, incluido en `requirements.txt`, lee `OPENAI_BASE_URL` del `.env`. El prefijo `google_genai:` necesitaría instalar `langchain-google-genai` (no está en `requirements.txt`) y una clave propia de Gemini.
