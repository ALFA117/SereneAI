"""
SereneAI — System Prompt e instrucciones para el LLM
Pega este contenido en tu main.py, reemplazando la función build_system_prompt()
"""

import re
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# KEYWORDS DE CRISIS — detección antes de llamar al LLM
# ─────────────────────────────────────────────────────────────────────────────

CRISIS_KEYWORDS = [
    # Ideación suicida
    "quiero morir", "quiero morirme", "prefiero estar muerto", "mejor muerto",
    "no quiero vivir", "no vale la pena vivir", "quitarme la vida",
    "acabar con todo", "hacerme daño", "hacerme algo",
    "suicidio", "suicidarme", "matarme", "me voy a matar",
    # Autolesión
    "cortarme", "lastimarme", "autolesión", "me corto",
    # Desesperanza severa
    "no hay salida", "nadie me va a extrañar", "todos estarían mejor sin mí",
    "soy una carga", "no sirvo para nada", "es mi culpa todo",
]

def detectar_crisis(texto: str) -> bool:
    """Devuelve True si el texto contiene señales de crisis."""
    texto_lower = texto.lower()
    return any(kw in texto_lower for kw in CRISIS_KEYWORDS)


# ─────────────────────────────────────────────────────────────────────────────
# LIMPIEZA DE RESPUESTA DEL LLM
# DeepSeek R1 añade <think>...</think> antes de responder.
# Esta función los elimina antes de devolver al usuario.
# ─────────────────────────────────────────────────────────────────────────────

def limpiar_respuesta(texto: str) -> str:
    """Elimina bloques <think>...</think> y limpia espacios."""
    texto = re.sub(r'<think>.*?</think>', '', texto, flags=re.DOTALL)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto.strip()


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def build_system_prompt(tecnicas_contexto: Optional[str] = None) -> str:
    """
    Construye el system prompt para SereneAI.
    
    Args:
        tecnicas_contexto: String con las 3 técnicas recuperadas por RAG.
                           Si es None, se omite el bloque de contexto.
    
    Returns:
        System prompt completo listo para enviar al LLM.
    """

    base = """Eres SereneAI, un companion de apoyo emocional desarrollado para acompañar a personas que atraviesan momentos difíciles. Tu rol es el de un acompañante empático y cálido, no el de un terapeuta ni médico.

## Tu personalidad

- Cálido, tranquilo y sin juicios
- Hablas en español, de forma natural y cercana (tuteo)
- Escuchas activamente antes de sugerir
- Eres conciso: respuestas de 3 a 5 párrafos máximo
- No usas lenguaje clínico ni tecnicismos
- No usas listas con bullets en tu respuesta — hablas como una persona, no como un manual

## Lo que SÍ haces

- Validas los sentimientos del usuario antes de cualquier sugerencia
- Propones una técnica de bienestar cuando es apropiado, explicándola de forma simple
- Mantienes el hilo de la conversación — recuerdas lo que el usuario ha compartido antes
- Terminas cada respuesta con una pregunta abierta que invite a continuar
- Si el usuario pregunta cómo estás, respondes brevemente y vuelves el foco a él

## Lo que NUNCA haces

- No diagnosticas ninguna condición (ansiedad, depresión, trastorno, etc.)
- No recomiendas medicamentos, dosis ni tratamientos médicos
- No dices frases vacías como "entiendo cómo te sientes" sin antes mostrar que realmente escuchaste
- No minimizas lo que el usuario siente ("eso no es para tanto", "otros están peor")
- No ofreces múltiples técnicas a la vez — una sola, bien explicada
- No repites la misma técnica dos veces en la misma sesión
- No mencionas que eres una IA a menos que el usuario te lo pregunte directamente

## Detección de crisis

Si el usuario expresa deseos de hacerse daño, ideas de suicidio o desesperanza severa, responde con calma y mucho cuidado. Valida su dolor, hazle saber que no está solo, y con mucha suavidad indícale que hay personas capacitadas para acompañarlo en este momento. No entres en pánico ni uses lenguaje alarmante."""

    contexto_bloque = ""
    if tecnicas_contexto:
        contexto_bloque = f"""

## Técnicas disponibles para esta conversación

El sistema ha identificado las siguientes técnicas como las más relevantes para lo que el usuario acaba de compartir. Puedes usar una de ellas si lo consideras apropiado, pero nunca las presentes como una lista — intégralas de forma natural en tu respuesta:

{tecnicas_contexto}

Recuerda: solo una técnica por respuesta, explicada de forma simple y humana."""

    cierre = """

## Formato de respuesta

- Longitud: entre 80 y 200 palabras
- Sin markdown, sin bullets, sin negritas
- Tono: como si hablaras en voz alta, con calma
- Termina siempre con una pregunta que invite al usuario a seguir hablando"""

    return base + contexto_bloque + cierre


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT PARA FRASE DE CIERRE (genera la tarjeta motivacional)
# ─────────────────────────────────────────────────────────────────────────────

PROMPT_FRASE_CIERRE = """Basándote en la conversación que acabamos de tener, genera UNA sola frase corta (máximo 12 palabras) que resuma el aprendizaje o la fortaleza que el usuario mostró hoy. 

La frase debe:
- Estar en segunda persona ("Hoy demostraste...", "Tienes la fuerza para...", "Cada respiración te acerca a...")
- Ser cálida y real, no genérica
- Estar en español
- No contener signos de exclamación

Responde ÚNICAMENTE con la frase, sin comillas, sin explicaciones adicionales."""


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT PARA IMAGEN (Oxlo Image Pro)
# ─────────────────────────────────────────────────────────────────────────────

def build_image_prompt(frase: str) -> str:
    """
    Construye el prompt para Oxlo Image Pro.
    La imagen es el fondo de la tarjeta motivacional.
    """
    return (
        f"Serene minimalist landscape, soft warm colors, golden hour light, "
        f"calm atmosphere, watercolor style, no text, no people, "
        f"gentle nature scene — mountains or lake or forest at dusk, "
        f"soft pastel palette, peaceful mood. "
        f"The image will be used as background for the motivational phrase: '{frase}'"
    )


# ─────────────────────────────────────────────────────────────────────────────
# MENSAJE FIJO DE CRISIS (no generado por el LLM)
# Se muestra directamente en el frontend cuando detectar_crisis() == True
# ─────────────────────────────────────────────────────────────────────────────

MENSAJE_CRISIS = {
    "texto": (
        "Gracias por confiar en mí y por compartir algo tan difícil. "
        "Lo que sientes es real y merece atención de alguien especializado. "
        "No estás solo — hay personas preparadas para acompañarte ahora mismo."
    ),
    "lineas_ayuda": [
        {"nombre": "SAPTEL México", "numero": "55 5259-8121", "horario": "24 horas"},
        {"nombre": "Línea de la Vida", "numero": "800 911-2000", "horario": "24 horas"},
        {"nombre": "IMSS Salud Mental", "numero": "800 890-0024", "horario": "Lunes a viernes"},
    ],
    "es_crisis": True
}


# ─────────────────────────────────────────────────────────────────────────────
# EJEMPLO DE USO EN main.py
# ─────────────────────────────────────────────────────────────────────────────
"""
CÓMO INTEGRAR EN TU ENDPOINT /chat:

@app.post("/chat")
async def chat(req: ChatRequest):
    # 1. Detectar crisis ANTES de llamar al LLM
    if detectar_crisis(req.mensaje):
        return MENSAJE_CRISIS

    # 2. Obtener embedding del mensaje del usuario
    embedding_usuario = await get_embedding(req.mensaje)

    # 3. Buscar top-3 técnicas por similitud coseno
    tecnicas_top = buscar_tecnicas_similares(embedding_usuario, top_k=3)

    # 4. Formatear contexto RAG
    contexto = formatear_tecnicas(tecnicas_top)

    # 5. Construir system prompt enriquecido
    system_prompt = build_system_prompt(tecnicas_contexto=contexto)

    # 6. Llamar al LLM (DeepSeek R1 u Oxlo Claw)
    respuesta_raw = await llamar_llm(
        system=system_prompt,
        historial=req.historial,
        mensaje_usuario=req.mensaje
    )

    # 7. Limpiar tags <think> de DeepSeek
    respuesta_limpia = limpiar_respuesta(respuesta_raw)

    return {
        "respuesta": respuesta_limpia,
        "tecnicas_usadas": [t["nombre"] for t in tecnicas_top],
        "es_crisis": False
    }
"""
