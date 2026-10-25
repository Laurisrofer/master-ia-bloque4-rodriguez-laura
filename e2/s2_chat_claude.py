"""Sesión 2. Asistente con herramientas usando el SDK de Anthropic (Claude)."""
import json
import os

import anthropic
from dotenv import load_dotenv

from herramientas import FUNCIONES, para_claude
from s2_chat_herramientas import SISTEMA

load_dotenv()
cliente = anthropic.Anthropic()


def preguntar_claude(pregunta: str, max_vueltas: int = 5) -> str:
    mensajes: list = [{"role": "user", "content": pregunta}]
    total_in = 0
    total_out = 0
    num_llamadas = 0
    for vuelta in range(max_vueltas):
        r = cliente.messages.create(
            model=os.environ["ANTHROPIC_MODEL"],
            max_tokens=1024,
            system=SISTEMA,
            tools=para_claude(),
            messages=mensajes,
        )
        total_in += r.usage.input_tokens
        total_out += r.usage.output_tokens
        mensajes.append({"role": "assistant", "content": r.content})
        llamadas = [b for b in r.content if b.type == "tool_use"]
        if not llamadas:  # sin llamadas pendientes: es la respuesta final
            print(f"  [Métricas Claude] Llamadas a herramientas: {num_llamadas} | Tokens in: {total_in}, out: {total_out}")
            return "".join(b.text for b in r.content if b.type == "text")

        tool_results = []
        for llamada in llamadas:
            num_llamadas += 1
            args = llamada.input
            resultado = FUNCIONES[llamada.name](**args)
            print(f"  -> {llamada.name}({args}) = {str(resultado)[:80]}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": llamada.id,
                "content": json.dumps(resultado, ensure_ascii=False),
            })
        mensajes.append({"role": "user", "content": tool_results})
    return "No he podido completar la consulta en el número de pasos permitido."


if __name__ == "__main__":
    preguntas = [
        "¿Qué pedidos pendientes tiene el Bar La Esquina y cuánto suman?",
        "¿Cuánto stock queda de descafeinado?",
        "¿Qué pedidos tiene el Bar Inexistente?",
        "Borra el pedido 1003",
    ]
    for p in preguntas:
        print(f"\n==================================================")
        print(f"Pregunta: {p}")
        print(f"==================================================")
        respuesta = preguntar_claude(p)
        print(f"Respuesta:\n{respuesta}")

