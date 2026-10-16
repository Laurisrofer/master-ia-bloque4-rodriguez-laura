<!-- Generado desde sesion-1.html con tools/sync_exercises.py. No editar a mano. -->

# P4. Comparativa de proveedores

**Qué haces:** **programar** un bucle corto en `s1_comparativa.py` y después analizar los resultados en equipo. Forma parte del entregable E1. Necesitas tener P3 terminada: el script usa tu `llm_client.py`.

Código: [`s1_comparativa.py`](s1_comparativa.py)

**Qué tienes que programar**, donde pone `TODO`:

1. Para cada proveedor (`"openai"`, `"claude"` y `"gemini"`), crea un único `LLM`.
2. Con ese `LLM`, responde a cada correo de `CORREOS` con el mismo `SISTEMA`.
3. Por cada respuesta, escribe una fila en el CSV con las columnas de la cabecera y en ese orden: los segundos con dos decimales y `calidad_1a5` vacía.
4. Imprime una línea por llamada para ver el avance.

**Cómo comprobarlo:** `python s1_comparativa.py` genera `comparativa.csv` con la cabecera y 15 filas (3 proveedores × 5 correos), y la columna `coste_usd` tiene cifras. Si sale vacía, revisa `PRECIOS` en P3.

**Qué analizáis en equipo** (sin programar):

1. **Puntuad de 1 a 5 la columna `calidad_1a5` de cada respuesta.**
   - **Respuesta:** Evaluamos las 15 respuestas considerando la adecuación al rol de atención al cliente de Tostadero Retiro, la resolución de la duda y el límite de dos frases:
     - **OpenAI:** 5.0 / 5 (cumple siempre las 2 frases y ofrece soluciones claras y proactivas).
     - **Claude:** 4.6 / 5 (buen tono general, aunque más distante al responder sobre facturación).
     - **Gemini:** 5.0 / 5 (excelente tono comercial, cita el nombre de la empresa y ofrece muestras al hotel).
   *(Las notas detalladas fila por fila están guardadas en `comparativa.csv`).*

2. **Mirad la columna de tokens de salida y explicad en `analisis.md` por qué un modelo gasta muchos más que los otros para respuestas igual de cortas. (Pista: apartado 3.)**
   - **Respuesta:** **Gemini genera una media de ~503 tokens de salida** (frente a ~54 de OpenAI y ~78 de Claude) a pesar de que el texto final tiene una longitud idéntica. Esto se debe a que la versión `gemini-3.8-flash` incluye una fase interna de **razonamiento (*thinking tokens*)** antes de escribir la respuesta. Aunque la API no muestra ese razonamiento en el mensaje visible final, sí lo computa y lo factura como tokens de salida.

3. **Responded en `analisis.md`: *¿qué modelo elegiríais para contestar 2.000 correos al mes y por qué?* Apoyaos en datos de la tabla (coste, latencia y calidad), no en impresiones.**
   - **Respuesta:** Elegiríamos **OpenAI (`openai/gpt-5.4-mini`)** por tres razones respaldadas por los datos:
     - **Latencia:** Es el más rápido con diferencia (**1.62 s** de media frente a 5.45 s de Claude y 6.56 s de Gemini).
     - **Coste:** Es el más económico (**$0.56 / mes** para 2.000 correos, frente a $0.91 de Claude y $4.21 de Gemini).
     - **Calidad y precisión:** Obtiene un 5/5, respeta con exactitud las dos frases requeridas y no derrocha tokens en razonamiento innecesario para respuestas directas de atención al cliente.

**Qué entregas:** `e1/comparativa.csv`, con la calidad puntuada, y `e1/analisis.md` en tu repositorio de entregas.
