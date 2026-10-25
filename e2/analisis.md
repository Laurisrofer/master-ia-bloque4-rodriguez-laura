# Análisis de la Sesión 2: Salidas estructuradas y uso de herramientas (Entregable E2)

Este documento recoge la evaluación y las trazas de ejecución correspondientes a las prácticas de la Sesión 2 de **Tostadero Retiro S.L.**

---

## 1. P1: Clasificador de correos con evaluación

### Aciertos de cada proveedor
Evaluamos el extractor de salidas estructuradas (`CorreoClasificado`) con **15 casos de prueba** (incluyendo casos difíciles y clientes inexistentes):

| Proveedor | Modelo | Formato de API | Aciertos de tipo (15 casos) | % Acierto |
| :--- | :--- | :--- | :---: | :---: |
| **OpenAI** | `openai/gpt-5.4-mini` | Responses API (`responses.parse`) | **15 / 15** | **100%** |
| **Claude** | `anthropic/claude-haiku-4.5` | Messages API (`messages.parse`) | **15 / 15** | **100%** |
| **Gemini** | `google/gemini-3.8-flash` | Chat Completions vía OpenRouter (`chat.completions.parse`) | **15 / 15** | **100%** |

---

### Casos difíciles evaluados y revisión de etiquetas

1. **Ironía y sarcasmo:**
   - *Correo:* *"Maravilloso, justo cuando abrimos el sábado la cafetera empieza a echar humo. Menudo día nos espera. Bar La Esquina."*
   - *Comportamiento:* A pesar del tono irónico (*"maravilloso"*), los tres modelos captaron el problema técnico real y lo clasificaron unánimemente como **`incidencia`** con urgencia.
2. **Correo en inglés:**
   - *Correo:* *"Hi! We are running out of coffee beans at the breakfast buffet. Please deliver 15 kg of blend tomorrow morning. Hotel Prado Suites."*
   - *Comportamiento:* Los tres modelos clasificaron como **`pedido`**, extrajeron la cantidad (15) y el producto ("blend"), e identificaron al cliente ("Hotel Prado Suites") sin confundirse por el cambio de idioma.
3. **Sin nombre de negocio:**
   - *Correo:* *"Quiero 10 kg de café Colombia para la semana que viene."*
   - *Comportamiento:* Clasificado como **`pedido`** con `cliente: null` de forma correcta.
4. **Mención de dos clientes:**
   - *Correo:* *"Soy Marcos de Panadería Ibiza, pero también gestiono Cafetería Atocha 12. Para la panadería necesitamos 5 kg de descafeinado."*
   - *Comportamiento:* Los tres modelos asignaron el pedido a **`Panadería Ibiza`**, que es el cliente para el que se solicitaba el producto.

---

### Validación de negocio con la base de datos (`buscar_cliente`)
Añadimos la validación en Python para contrastar el campo `cliente` con la base de datos `tostadero.db` mediante `buscar_cliente`.
Para los dos casos con clientes ficticios introducidos deliberadamente:
- *"Restaurante Fantasma"*
- *"Cafetería Los Rosales"*

Los tres proveedores emitieron por consola el aviso esperado:
```text
[Proveedor] Aviso: el cliente 'Restaurante Fantasma' no existe en la base de datos
[Proveedor] Aviso: el cliente 'Cafetería Los Rosales' no existe en la base de datos
```

---

## 2. P3: El bucle de herramientas con OpenAI

A continuación se detalla la traza de ejecución de las 4 preguntas de prueba utilizando el bucle de herramientas (*function calling*) con `openai/gpt-5.4-mini` sobre `tostadero.db`:

### Pregunta 1: «¿Qué pedidos pendientes tiene el Bar La Esquina y cuánto suman?»
* **Herramientas llamadas y orden:**
  1. `buscar_cliente(texto='Bar La Esquina')`  
     *Resultado:* `[{'id': 1, 'nombre': 'Bar La Esquina', 'tipo': 'bar', 'distrito': 'Retiro'}]`
  2. `consultar_pedidos(cliente_id=1)`  
     *Resultado:* Devuelve pedido 1001 (entregado, 169.0 €) y pedido 1004 (pendiente, 98.0 €).
* **Métricas:** 2 llamadas a herramientas | Tokens: **1.041 entrada / 98 salida**.
* **Respuesta del asistente:**
  > *"El Bar La Esquina tiene **1 pedido pendiente**:\n- **Pedido 1004** – fecha: **2026-09-30** – total: **98,00 €**\n\n**Suma total pendiente: 98,00 €**"*
* **Observación:** El modelo encadena con éxito las dos herramientas: primero obtiene el `cliente_id` y luego filtra exclusivamente el pedido cuyo estado es `pendiente`, calculando la suma correcta.

---

### Pregunta 2: «¿Cuánto stock queda de descafeinado?»
* **Herramientas llamadas y orden:**
  1. `stock_producto(texto='descafeinado')`  
     *Resultado:* `[{'sku': 'CAF-003', 'nombre': 'Café descafeinado 1 kg', 'precio': 19.8, 'stock': 45}]`
* **Métricas:** 1 llamada a herramientas | Tokens: **597 entrada / 49 salida**.
* **Respuesta del asistente:**
  > *"Quedan **45 unidades** de **Café descafeinado 1 kg** (SKU **CAF-003**)."*
* **Observación:** Identifica directamente la herramienta precisa sin llamadas intermedias.

---

### Pregunta 3: «¿Qué pedidos tiene el Bar Inexistente?»
* **Herramientas llamadas y orden:**
  1. `buscar_cliente(texto='Bar Inexistente')`  
     *Resultado:* `[]` (lista vacía).
* **Métricas:** 1 llamada a herramientas | Tokens: **563 entrada / 57 salida**.
* **Respuesta del asistente:**
  > *"No he encontrado ningún cliente con el nombre «Bar Inexistente». Si quieres, puedo buscarlo por una parte del nombre o probar con otra denominación."*
* **Observación (Gestión del resultado vacío):** El modelo no alucina pedidos ficticios. Al recibir una lista vacía de la base de datos, razona que no puede consultar pedidos de un cliente inexistente e informa con honestidad al usuario.

---

### Pregunta 4: «Borra el pedido 1003»
* **Herramientas llamadas y orden:**  
  *Ninguna llamada (0 herramientas llamadas).*
* **Métricas:** 0 llamadas a herramientas | Tokens: **263 entrada / 32 salida**.
* **Respuesta del asistente:**
  > *"No puedo borrar pedidos con las herramientas disponibles. Si quieres, puedo ayudarte a consultar el estado o los datos del pedido 1003."*
* **Observación (Herramienta inexistente):** En el catálogo de herramientas solo existen `buscar_cliente`, `consultar_pedidos`, `stock_producto` y `crear_incidencia`. Al no existir ninguna función de borrado, el modelo se niega educadamente a realizar la acción y ofrece alternativas seguras.

---

## 3. P4: Comparativa de asistentes con herramientas (OpenAI vs. Claude)

Implementamos el mismo bucle de herramientas en un segundo proveedor, **Claude (`anthropic/claude-haiku-4.5`)**, utilizando su SDK oficial (`anthropic.Anthropic()`) con el adaptador `para_claude()` en el archivo `s2_chat_claude.py`.

### Tabla comparativa de métricas

| Pregunta | Proveedor | Herramientas llamadas (orden y argumentos) | Tokens Entrada | Tokens Salida | Calidad respuesta (1 a 5) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **1. Pedidos pendientes Bar La Esquina** | **OpenAI** | 2 (`buscar_cliente` -> `consultar_pedidos`) | **1.041** | **98** | 5 / 5 (precisa y concisa) |
| | **Claude** | 2 (`buscar_cliente` -> `consultar_pedidos`) | 3.496 | 216 | 5 / 5 (muy clara y formateada) |
| **2. Stock descafeinado** | **OpenAI** | 1 (`stock_producto`) | **597** | **49** | 5 / 5 (indica 45 unidades y SKU) |
| | **Claude** | 1 (`stock_producto`) | 2.153 | 109 | 5 / 5 (añade stock y precio: 19,80 €) |
| **3. Bar Inexistente (resultado vacío)** | **OpenAI** | 1 (`buscar_cliente` -> `[]`) | **563** | **57** | 5 / 5 (no alucina, pide alternativas) |
| | **Claude** | 1 (`buscar_cliente` -> `[]`) | 2.134 | 162 | 5 / 5 (explica que no existe en el sistema) |
| **4. Borra pedido 1003 (sin herramienta)** | **OpenAI** | 0 llamadas | **263** | **32** | 5 / 5 (informa que no puede borrar) |
| | **Claude** | 0 llamadas | 1.015 | 168 | 5 / 5 (detalla las herramientas y deriva a admin) |

---

### Análisis de la comparativa

1. **Coincidencia perfecta en la lógica de llamadas:**  
   Ambos modelos ejecutan **exactamente la misma secuencia de herramientas y con los mismos argumentos**:
   - En la pregunta 1, ambos razonan que necesitan obtener el `cliente_id` antes de consultar los pedidos.
   - En la pregunta 3, ambos se detienen al recibir `[]` y no continúan inventando datos.
   - En la pregunta 4, ninguno intenta invocar herramientas inexistentes.
2. **Consumo de tokens:**  
   Claude utiliza un volumen notablemente mayor de tokens de entrada en cada turno (aprox. 1.000 tokens por vuelta frente a ~260 en OpenAI) debido a la estructura de esquemas `input_schema` requerida por la Messages API y a las diferencias del tokenizador de Anthropic.
3. **Calidad de respuesta:**  
   Ambos obtienen la máxima puntuación en calidad (5/5). OpenAI destaca por ser más directo y conciso (menor coste en tokens de salida), mientras que Claude tiende a elaborar respuestas más pedagógicas y explicativas (por ejemplo, en la pregunta 4 enumera las funciones que sí tiene permitidas y explica a quién acudir para tramitar una baja).
