from tools import buscar_conocimiento, crear_borrador_ticket

# Preguntas demasiado cortas o con frases genericas no traen suficiente informacion
# para diagnosticar: el agente debe pedir contexto (RF07) en vez de adivinar.
_FRASES_VAGAS = ("falla", "no funciona", "no sirve", "no anda", "esta mal", "no prende", "se dano")


def es_pregunta_vaga(texto):
    if len(texto.split()) <= 4:
        return True
    return any(frase in texto for frase in _FRASES_VAGAS)


def personalizar(answer, contexto):
    """Usa el contexto opcional (device, operating_system) para especializar la respuesta (RF04)."""
    dispositivo = (contexto or {}).get("device")
    sistema = (contexto or {}).get("operating_system")
    if not dispositivo and not sistema:
        return answer
    detalle = dispositivo or "tu equipo"
    if sistema:
        detalle = f"{detalle} ({sistema})"
    return f"Para {detalle}: {answer}"


def diagnosticar(question, user_id, contexto=None):
    """Analiza la pregunta y decide: responder, pedir_contexto o escalar_a_humano (RF06)."""
    texto = question.lower()

    articulo = buscar_conocimiento(question)
    if articulo is not None:
        pasos = " ".join(f"{indice}. {paso}" for indice, paso in enumerate(articulo["pasos"], start=1))
        return {
            "answer": personalizar(pasos, contexto),
            "source": articulo["id"],
            "next_action": "responder",
        }

    if es_pregunta_vaga(texto):
        return {
            "answer": (
                "Necesito algunos datos adicionales para continuar con el diagnostico: "
                "Que mensaje de error aparece? El equipo esta lento, se reinicia o deja de "
                "responder? Que sistema operativo utiliza?"
            ),
            "next_action": "pedir_contexto",
        }

    return {
        "answer": (
            "No encontre un procedimiento autorizado para resolver este caso. Se recomienda "
            "revision por parte del equipo de soporte."
        ),
        "source": "fallback",
        "next_action": "escalar_a_humano",
        "ticket_borrador": crear_borrador_ticket(question, user_id),
    }
