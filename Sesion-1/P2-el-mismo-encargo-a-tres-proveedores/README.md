<!-- Generado desde sesion-1.html con tools/sync_exercises.py. No editar a mano. -->

# P2. El mismo encargo a tres proveedores

**Qué haces:** ejecutar un script y responder unas preguntas en equipo. **No hay que programar** y no se entrega: lo comentamos en la puesta en común.

El script manda el mismo encargo a tres modelos distintos, cada uno con un formato de API diferente: OpenAI con la Responses API, Claude con la Messages API y Gemini con Chat Completions a través de OpenRouter (o con su Interactions API nativa si has puesto `GEMINI_API_KEY`). Léelo con calma: en P3 tendrás que reutilizar estas llamadas.

Código: [`s1_hola_tres.py`](s1_hola_tres.py)

Ejecuta `python s1_hola_tres.py` dos veces y responde en equipo:

- **¿Qué proveedor responde antes? ¿La diferencia se mantiene entre ejecuciones?**
  - **Respuesta:** **Claude y OpenAI** son los más rápidos (~2 segundos) y se alternan el primer puesto. **Gemini** es claramente el más lento (tarda entre 5 y 7 segundos), una diferencia que se mantiene en ambas ejecuciones.

- **Para el mismo texto, ¿por qué no coinciden los tokens de entrada? (Pista: cada proveedor usa un tokenizador distinto.)**
  - **Respuesta:** Porque cada proveedor utiliza su propio **tokenizador y tamaño de vocabulario**. Unos modelos (como Gemini) empaquetan mejor el español en menos tokens y otros (como Claude) dividen el texto en más partes. Además, cada API añade etiquetas internas de formato distintas.

- **El correo es mixto: incidencia y pedido. ¿Lo clasifican bien los tres?**
  - **Respuesta:** **Sí, los tres lo clasifican correctamente como "mixto".** Todos identifican que hay una avería técnica (incidencia) y a la vez una consulta por el pedido 1004 (pedido).

- **¿Cambia la redacción entre la primera y la segunda ejecución?**
  - **Respuesta:** **Sí, varía un poco la redacción.** Aunque la conclusión y la respuesta son equivalentes, cambian algunas palabras porque los modelos aplican cierta variabilidad por defecto (temperatura > 0).
