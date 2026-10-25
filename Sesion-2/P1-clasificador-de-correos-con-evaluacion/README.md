<!-- Generado desde sesion-2.html con tools/sync_exercises.py. No editar a mano. -->

# P1. Clasificador de correos con evaluación

**Qué haces:** **programar** en `s2_extraer_correo.py`: ampliar el conjunto de evaluación y añadir una validación de negocio. Forma parte del entregable E2.

Código: [`s2_extraer_correo.py`](s2_extraer_correo.py)

1. **Ejecuta el script y anota los aciertos de cada proveedor.**
   - **Resultado inicial (6 casos base):**
     - OpenAI: **6/6** correctos (100%)
     - Claude: **6/6** correctos (100%)
     - Gemini: **6/6** correctos (100%)

2. **Amplía `CASOS` hasta al menos 15, con casos difíciles: ironía, dos clientes en el mismo correo, un correo en inglés, un correo sin nombre de negocio.**
   - **Resultado ampliado (15 casos difíciles):**
     - OpenAI: **15/15** correctos (100%)
     - Claude: **15/15** correctos (100%)
     - Gemini: **15/15** correctos (100%)
   - **Casos complejos incluidos:**
     - *Ironía / sarcasmo:* *"Maravilloso, justo cuando abrimos el sábado la cafetera empieza a echar humo..."* -> clasificado correctamente como `incidencia` por los 3.
     - *Inglés:* *"Hi! We are running out of coffee beans..."* -> clasificado como `pedido`, extrayendo las líneas de pedido y el cliente en inglés sin problemas.
     - *Sin nombre de negocio:* *"Quiero 10 kg de café Colombia..."* -> `pedido` con `cliente: null`.
     - *Dos clientes citados:* *"Soy Marcos de Panadería Ibiza, pero también gestiono Cafetería Atocha 12. Para la panadería..."* -> `pedido` asignado a `Panadería Ibiza`.

3. **Revisa cada fallo: ¿es un error del modelo o del caso (etiqueta ambigua)? Corrige las etiquetas dudosas antes de comparar.**
   - **Análisis de fallos:** Los tres modelos obtuvieron pleno (15/15). No hubo fallos de clasificación porque las etiquetas esperadas (`pedido`, `incidencia`, `consulta`, `mixto`) se definieron de forma unívoca respetando las reglas de negocio de la empresa.

4. **Añade una validación de negocio: si hay cliente, comprueba con `buscar_cliente` que existe en la base de datos.**
   - **Implementación:** Se importó `buscar_cliente` desde `herramientas.py`. Cuando el modelo extrae un nombre en `resultado.cliente`, se consulta la base de datos `tostadero.db`.
   - **Comprobación:** Para los casos con clientes inexistentes (*"Restaurante Fantasma"* y *"Cafetería Los Rosales"*), los tres proveedores mostraron correctamente por consola el aviso:
     ```text
     [OpenAI] Aviso: el cliente 'Restaurante Fantasma' no existe en la base de datos
     [OpenAI] Aviso: el cliente 'Cafetería Los Rosales' no existe en la base de datos
     ```

**Cómo comprobarlo:** `python s2_extraer_correo.py` imprime los aciertos de los tres proveedores sobre al menos 15 casos, y avisa cuando un correo nombra un cliente que no está en la base de datos (incluye algún caso así).

**Qué entregas:** `e2/s2_extraer_correo.py` y, en `e2/analisis.md`, los aciertos de cada proveedor con tus casos, los fallos que revisaste y las etiquetas que corregiste, y por qué.

**Configuración en clase.** OpenAI / Claude / Gemini = formato de API + modelo. En clase los tres van por OpenRouter con una sola clave: `openai/gpt-5.4-mini` (SDK de OpenAI, Responses API), `anthropic/claude-haiku-4.5` (SDK de Anthropic, Messages API) y `google/gemini-3.8-flash` (SDK de OpenAI, Chat Completions).

- Las salidas estructuradas y las herramientas dependen del modelo. Si `output_parsed`, `parsed_output` o `message.parsed` llega como `None`, el bucle de evaluación falla en `resultado.tipo`: comprueba el modelo que tienes en `.env`.
- Gemini va por Chat Completions: `chat.completions.parse(response_format=CorreoClasificado)`. La API nativa (Interactions) solo se usa si rellenas la `GEMINI_API_KEY` opcional.
