<!-- Generado desde sesion-1.html con tools/sync_exercises.py. No editar a mano. -->

# P2. Herramientas como funciones Python

**Qué haces:** leer `herramientas.py` en equipo. **No hay que programar** y no se entrega, pero lo usarás en P3 y P4.

Las funciones de negocio se definen una vez, con su esquema en formato neutro, y se traducen al dialecto de cada proveedor. La función auxiliar `_obj` produce esquemas compatibles con el modo estricto de OpenAI (todas las propiedades obligatorias y sin propiedades adicionales), que los demás proveedores también aceptan.

Código: [`herramientas.py`](herramientas.py)

---

## Resumen explicativo de `herramientas.py`

1. **La analogía del camarero y la cocina:**
   - **El modelo de IA (OpenAI, Claude, Gemini):** Es el "camarero". Atiende al cliente con lenguaje natural, pero **no ejecuta código Python directamente ni accede a la base de datos** por motivos de seguridad.
   - **Nuestras funciones Python:** Son la "cocina". Tienen acceso real a `tostadero.db` a través de SQLite (`_consulta`).
   - **Las descripciones (esquemas JSON):** Son la "carta" que le dice al modelo qué herramientas existen y qué parámetros necesitan.

2. **Las 4 herramientas de negocio:**
   - `buscar_cliente(texto)`: Busca en la tabla `clientes` por nombre (`LIKE %texto%`). Devuelve `id`, `nombre`, `tipo` y `distrito`.
   - `consultar_pedidos(cliente_id)`: Consulta los pedidos asociados a un `cliente_id` (`id`, `fecha`, `estado`, `total`).
   - `stock_producto(texto)`: Consulta precio y stock de café o máquinas en la tabla `productos` por nombre o SKU.
   - `crear_incidencia(cliente_id, maquina, descripcion, prioridad)`: Inserta una avería en `incidencias` si el cliente existe.

3. **La lista `DEFINICIONES`:**
   - Describe cada función en formato JSON Schema neutro (`name`, `description`, `parameters`).
   - La IA lee la `description` para razonar cuándo usar cada herramienta (por ejemplo, deduce que para consultar pedidos necesita obtener primero el `cliente_id` llamando antes a `buscar_cliente`).
   - La función auxiliar `_obj` fuerza el modo estricto de OpenAI (`required` con todos los campos y `additionalProperties: False`).

4. **Adaptadores de dialecto (patrón Adapter):**
   - `para_openai()`: Genera formato `{"type": "function", "strict": True, ...}`.
   - `para_claude()`: Genera formato `{"name": ..., "description": ..., "input_schema": ...}`.
   - `para_chat()`: Genera formato `{"type": "function", "function": ...}` para OpenRouter / Chat Completions.

