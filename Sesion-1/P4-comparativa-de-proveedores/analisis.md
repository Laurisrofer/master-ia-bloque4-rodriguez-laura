# Análisis comparativo de proveedores de LLM (Entregable E1)

Este documento recoge el análisis y las conclusiones del experimento comparativo realizado sobre 5 correos de clientes de **Tostadero Retiro S.L.**, utilizando la interfaz unificada de `llm_client.py` con tres proveedores distintos: OpenAI (`openai/gpt-5.4-mini`), Claude (`anthropic/claude-haiku-4.5`) y Gemini (`google/gemini-3.8-flash`).

---

## 1. Tabla resumen de métricas

A partir de los datos registrados en `comparativa.csv` (15 llamadas en total), se obtienen los siguientes promedios por proveedor:

| Proveedor | Modelo evaluado | Latencia media (s) | Tokens entrada (med.) | Tokens salida (med.) | Coste medio / llamada ($) | Calidad media (1 a 5) | Coste proyectado (2.000 correos/mes) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **OpenAI** | `openai/gpt-5.4-mini` | **1.62 s** | 54.0 | **53.6** | **$0.000282** | **5.0 / 5** | **$0.56 / mes** |
| **Claude** | `anthropic/claude-haiku-4.5` | 5.45 s | 67.0 | 78.0 | $0.000456 | 4.6 / 5 | $0.91 / mes |
| **Gemini** | `google/gemini-3.8-flash` | 6.56 s | 42.4 | **503.0** | $0.002105 | 5.0 / 5 | $4.21 / mes |

---

## 2. Análisis del consumo de tokens de salida

### Pregunta:
> *¿Por qué un modelo gasta muchos más tokens de salida que los otros para respuestas igual de cortas?*

### Explicación:
Al observar la columna `tokens_salida`, destaca que **Gemini genera una media de 503 tokens de salida**, frente a los **54 tokens de OpenAI** y **78 tokens de Claude**, a pesar de que el texto final visible para el cliente tiene una longitud muy similar (dos frases breves).

Esto se debe a:
1. **Tokens de razonamiento interno (*thinking / reasoning tokens*):**  
   El modelo `google/gemini-3.8-flash` (a través de OpenRouter) incorpora una fase de pensamiento o razonamiento previo antes de emitir la respuesta visible. Estos tokens de cadena de pensamiento (*Chain-of-Thought*) no se entregan en el campo de texto final al usuario, pero la API los genera internamente y **se computan y facturan como tokens de salida**.
2. **Impacto en latencia y coste:**  
   Esta generación interna de tokens adicionales es la causante directa de que Gemini tenga la mayor latencia media (**6.56 s**) y un coste por llamada más de **7 veces superior** al de OpenAI ($0.002105 frente a $0.000282).
3. **Contraste con OpenAI y Claude:**  
   `gpt-5.4-mini` y `claude-haiku-4.5` operan directamente como modelos de chat rápidos sin generar cadenas de pensamiento extensas para este prompt, generando exclusivamente los tokens del texto redactado.

---

## 3. Selección del modelo para 2.000 correos al mes

### Pregunta:
> *¿Qué modelo elegiríais para contestar 2.000 correos al mes y por qué? Apoyaos en datos de la tabla (coste, latencia y calidad), no en impresiones.*

### Elección recomendada:
**OpenAI (`openai/gpt-5.4-mini`)**.

### Justificación basada en datos:

1. **Latencia (Tiempo de respuesta):**
   - **OpenAI:** **1.62 segundos** de media.
   - Claude: **5.45 segundos** (3.3 veces más lento). En la consulta del hotel llegó a tardar 12.17 s.
   - Gemini: **6.56 segundos** (4 veces más lento).
   - *Conclusión:* En un canal de atención al cliente, responder en menos de 2 segundos mejora sustancialmente la experiencia del usuario y permite integrar el modelo en flujos síncronos o de respuesta rápida sin degradar el rendimiento.

2. **Coste económico:**
   - Para responder 2.000 correos mensuales:
     - **OpenAI:** **$0.56 / mes** (56 céntimos de dólar).
     - Claude: **$0.91 / mes** (+62% respecto a OpenAI).
     - Gemini: **$4.21 / mes** (+650% respecto a OpenAI).
   - *Conclusión:* OpenAI es la opción más eficiente y barata, con una diferencia abrumadora frente a Gemini debida al sobrecoste de los tokens de razonamiento.

3. **Calidad y cumplimiento del encargo:**
   - Obtuvo una puntuación perfecta (**5.0 / 5**).
   - Cumple de manera exacta y consistente la restricción de *"máximo dos frases en español"*.
   - Muestra un tono cercano, educado y proactivo: no solo clasifica e informa, sino que ofrece los siguientes pasos lógicos (por ejemplo, propone revisar las facturas facilitando importes, ofrece un chequeo paso a paso para la avería de la cafetera o pregunta los detalles de entrega para los pedidos).

### Veredicto final:
**`openai/gpt-5.4-mini`** es la opción ganadora en todas las dimensiones: ofrece la **máxima velocidad** (1.62 s), el **menor coste** ($0.56/mes) y una **calidad y adherencia a las instrucciones impecable** (5/5).
