<!-- Generado desde sesion-1.html con tools/sync_exercises.py. No editar a mano. -->

# P3. El bucle de herramientas con OpenAI

**Qué haces:** ejecutar el bucle con varias preguntas y analizar la traza. **No hay que programar**, pero tus respuestas forman parte del entregable E2.

Código: [`s2_chat_herramientas.py`](s2_chat_herramientas.py)

Prueba estas preguntas y observa en la traza qué herramientas se llaman y en qué orden:

1. **«¿Qué pedidos pendientes tiene el Bar La Esquina y cuánto suman?»** (requiere dos llamadas encadenadas).
   - **Herramientas y orden:**
     1. `buscar_cliente({'texto': 'Bar La Esquina'})` -> Devuelve `id: 1`.
     2. `consultar_pedidos({'cliente_id': 1})` -> Devuelve la lista de pedidos del cliente.
   - **Métricas:** 2 llamadas a herramientas | Tokens: 1041 entrada, 98 salida.
   - **Respuesta del asistente:** Identifica correctamente que de los pedidos del cliente solo uno tiene estado pendiente (el Pedido 1004 del 2026-09-30 por 98,00 €) y calcula la suma total: **98,00 €**.

2. **«¿Cuánto stock queda de descafeinado?»**
   - **Herramientas y orden:**
     1. `stock_producto({'texto': 'descafeinado'})` -> Devuelve SKU `CAF-003`, nombre *"Café descafeinado 1 kg"*, precio 19.8 y stock 45.
   - **Métricas:** 1 llamada a herramientas | Tokens: 597 entrada, 49 salida.
   - **Respuesta del asistente:** *"Quedan 45 unidades de Café descafeinado 1 kg (SKU CAF-003)."*

3. **«¿Qué pedidos tiene el Bar Inexistente?»** (¿cómo gestiona el resultado vacío?).
   - **Herramientas y orden:**
     1. `buscar_cliente({'texto': 'Bar Inexistente'})` -> Devuelve lista vacía `[]`.
   - **Métricas:** 1 llamada a herramientas | Tokens: 563 entrada, 57 salida.
   - **Respuesta del asistente:** Gestiona el resultado vacío con honestidad y sin alucinaciones: avisa de que no existe ningún cliente con ese nombre y ofrece buscarlo por otra denominación.

4. **«Borra el pedido 1003»** (no existe esa herramienta: ¿qué responde?).
   - **Herramientas y orden:** Ninguna llamada (0 herramientas llamadas).
   - **Métricas:** 0 llamadas a herramientas | Tokens: 263 entrada, 32 salida.
   - **Respuesta del asistente:** Detecta que no tiene ninguna función de borrado en su catálogo y responde con franqueza: *"No puedo borrar pedidos con las herramientas disponibles. Si quieres, puedo ayudarte a consultar el estado o los datos del pedido 1003."*

---

**Qué entregas:** en `e2/analisis.md`, para cada pregunta, qué herramientas se llamaron, en qué orden y con qué argumentos, y qué respondió el asistente.
