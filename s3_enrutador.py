"""Sesión 3. Enrutador: workflow predecible y barato delante del agente caro."""
import os
from dotenv import load_dotenv

from herramientas import DEFINICIONES, FUNCIONES
from llm_client import LLM
from s2_extraer_correo import con_openai
from s3_agente import Agente, Herramienta, SISTEMA

load_dotenv()

SISTEMA_CONSULTAS = (
    "Eres el asistente de atención al cliente de Tostadero Retiro S.L. "
    "Responde a consultas generales de clientes de forma breve, amable y en español."
)

herramientas = [
    Herramienta(d["name"], d["description"], d["parameters"], FUNCIONES[d["name"]],
                requiere_aprobacion=(d["name"] == "crear_incidencia"))
    for d in DEFINICIONES
]
agente = Agente(SISTEMA, herramientas)


def atender(correo: str) -> str:
    clasificacion = con_openai(correo)
    print(f"  [Enrutador] Tipo detectado: '{clasificacion.tipo}'")
    if clasificacion.tipo == "consulta":
        # Camino directo y económico (1 sola llamada simple sin herramientas)
        print("  -> Derivado al camino directo/económico (sin agente)")
        return LLM("openai").responder(SISTEMA_CONSULTAS, correo).texto
    # Camino agéntico completo para casos complejos (pedidos, averías, mixto)
    print("  -> Derivado al Agente técnico (bucle multi-paso con herramientas)")
    return agente.ejecutar(correo)


if __name__ == "__main__":
    print("=== Caso A: Consulta simple (camino barato) ===")
    print(atender("Buenas, ¿la factura de septiembre ya está emitida?"))

    print("\n=== Caso B: Avería técnica (camino agéntico) ===")
    print(atender("Os escribo de Restaurante Lumbre: la cafetera no calienta y no podemos dar desayunos."))

