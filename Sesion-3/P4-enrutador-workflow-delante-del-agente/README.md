<!-- Generado desde sesion-1.html con tools/sync_exercises.py. No editar a mano. -->

# P4. Enrutador: workflow delante del agente

No todo correo necesita un agente. Combina el clasificador de la sesión 2 con el agente para que solo los casos complejos usen el camino caro:

```python
from llm_client import LLM                 # copia de la sesión 1
from s2_extraer_correo import con_openai   # copia de la sesión 2

SISTEMA_CONSULTAS = "..."                  # lo escribes tú

def atender(correo: str) -> str:
    clasificacion = con_openai(correo)        # sesión 2: salida estructurada
    if clasificacion.tipo == "consulta":      # camino barato y predecible
        return LLM("gemini").responder(SISTEMA_CONSULTAS, correo).texto
    return agente.ejecutar(correo)            # camino agéntico para lo complejo
```

---

## Implementación y análisis del enrutador (`s3_enrutador.py`)

- **Estrategia híbrida:**  
  1. El clasificador rápido (`con_openai`) categoriza el correo entrante con una salida estructurada.
  2. Si es una **`consulta`**, se deriva directamente a un modelo rápido y económico (`LLM("openai")` o `LLM("gemini")`) sin herramientas ni memoria multi-paso.
  3. Si es un **`pedido`**, **`incidencia`** o **`mixto`**, se activa el **agente técnico completo** con bucle de herramientas, aprobación humana y acceso a SQLite.
- **Ahorro de recursos:**  
  Permite resolver consultas informativas y frecuentes con una sola llamada simple (~30 tokens de salida), reservando el bucle agéntico caro (que consume varios miles de tokens y múltiples llamadas encadenadas) solo para los casos que realmente requieren interactuar con la base de datos de la empresa.
