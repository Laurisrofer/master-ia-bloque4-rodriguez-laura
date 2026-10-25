"""Sesión 2. Salidas estructuradas: de un correo libre a un objeto validado."""
import os
from typing import Literal

import anthropic
import openai
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

from herramientas import buscar_cliente

load_dotenv()


class Linea(BaseModel):
    producto: str = Field(description="Producto tal y como lo menciona el cliente")
    cantidad: int = Field(description="Unidades o kilos pedidos")


class CorreoClasificado(BaseModel):
    tipo: Literal["pedido", "incidencia", "consulta", "mixto"]
    cliente: str | None = Field(description="Nombre del negocio si aparece; si no, null")
    lineas: list[Linea] = Field(description="Vacía si no hay pedido")
    urgente: bool
    resumen: str = Field(description="Una sola frase en español")


SISTEMA = "Extraes información de correos de clientes de un distribuidor de café para hostelería."


def con_openai(correo: str) -> CorreoClasificado:
    r = openai.OpenAI().responses.parse(
        model=os.environ["OPENAI_MODEL"], instructions=SISTEMA, input=correo,
        text_format=CorreoClasificado,
    )
    return r.output_parsed


def con_claude(correo: str) -> CorreoClasificado:
    r = anthropic.Anthropic().messages.parse(
        model=os.environ["ANTHROPIC_MODEL"], max_tokens=1024, system=SISTEMA,
        messages=[{"role": "user", "content": correo}],
        output_format=CorreoClasificado,
    )
    return r.parsed_output


def con_gemini(correo: str) -> CorreoClasificado:
    if os.getenv("GEMINI_API_KEY"):  # opcional: API nativa de Gemini
        cliente = genai.Client()  # en una variable: si no, el SDK cierra el cliente antes de usarlo
        r = cliente.interactions.create(
            model=os.environ["GEMINI_MODEL"].removeprefix("google/"),
            system_instruction=SISTEMA, input=correo,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": CorreoClasificado.model_json_schema(),
            },
        )
        return CorreoClasificado.model_validate_json(r.output_text)
    # Por defecto, vía OpenRouter con Chat Completions
    cliente = openai.OpenAI(base_url="https://openrouter.ai/api/v1",
                            api_key=os.environ["OPENROUTER_API_KEY"])
    r = cliente.chat.completions.parse(
        model=os.environ["GEMINI_MODEL"],
        messages=[{"role": "system", "content": SISTEMA}, {"role": "user", "content": correo}],
        response_format=CorreoClasificado,
    )
    return r.choices[0].message.parsed


# Conjunto de evaluación ampliado a 15 casos (con casos difíciles y cliente inexistente)
CASOS = [
    ("Necesito 20 kg del blend de hostelería para el viernes. Bar La Esquina.", "pedido"),
    ("El molino hace un ruido raro desde ayer, ¿podéis venir?", "incidencia"),
    ("¿Tenéis café descafeinado de especialidad?", "consulta"),
    ("Mandadme 5 kg de Etiopía y, de paso, la cafetera gotea. Lumbre.", "mixto"),
    ("URGENTE: sin café para mañana, 10 kg de blend. Hotel Prado Suites", "pedido"),
    ("Buenas, ¿la factura de septiembre ya está emitida?", "consulta"),
    ("Maravilloso, justo cuando abrimos el sábado la cafetera empieza a echar humo. Menudo día nos espera. Bar La Esquina.", "incidencia"),
    ("Hi! We are running out of coffee beans at the breakfast buffet. Please deliver 15 kg of blend tomorrow morning. Hotel Prado Suites.", "pedido"),
    ("Quiero 10 kg de café Colombia para la semana que viene.", "pedido"),
    ("Soy Marcos de Panadería Ibiza, pero también gestiono Cafetería Atocha 12. Para la panadería necesitamos 5 kg de descafeinado.", "pedido"),
    ("¿A qué temperatura recomendáis calibrar la máquina para el tueste de Kenia y cuál es el pedido mínimo para envío gratis?", "consulta"),
    ("Hola, ¿podríais revisar si se cargó la factura del mes pasado? Cafetería Atocha 12.", "consulta"),
    ("Traednos urgentemente 30 kg de café arábica y mandad al técnico porque el agua no calienta. Restaurante Fantasma.", "mixto"),
    ("¿Podéis enviarme la ficha técnica del blend y además apuntarme 12 cajas de vasos para el lunes? Panadería Ibiza.", "mixto"),
    ("Si no viene nadie a arreglar la cafetera antes de las 12 cerramos el bar. Es la tercera vez que aviso. Cafetería Los Rosales.", "incidencia"),
]

if __name__ == "__main__":
    for nombre, extraer in [("OpenAI", con_openai), ("Claude", con_claude), ("Gemini", con_gemini)]:
        aciertos = 0
        print(f"\nEvaluando {nombre}...")
        for correo, esperado in CASOS:
            resultado = extraer(correo)
            es_correcto = resultado.tipo == esperado
            aciertos += es_correcto
            if not es_correcto:
                print(f"  [{nombre}] Fallo: predijo '{resultado.tipo}', se esperaba '{esperado}' en: {correo[:45]}...")
            # Validación de negocio 1: cantidades positivas
            if any(l.cantidad <= 0 for l in resultado.lineas):
                print(f"  [{nombre}] Cantidad no válida en: {correo[:40]}...")
            # Validación de negocio 2: comprobación de cliente en la base de datos
            if resultado.cliente:
                if not buscar_cliente(resultado.cliente):
                    print(f"  [{nombre}] Aviso: el cliente '{resultado.cliente}' no existe en la base de datos ({correo[:35]}...)")
        print(f"{nombre}: {aciertos}/{len(CASOS)} tipos correctos")
