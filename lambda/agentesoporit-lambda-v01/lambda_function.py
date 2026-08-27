import json


def build_response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(payload, ensure_ascii=False),
    }


def clasificar_pregunta(question):
    """Devuelve (answer, source, next_action) segun palabras clave del soporte IT."""
    texto = question.lower()
    if any(palabra in texto for palabra in ("internet", "wifi", "red", "conexion")):
        return (
            "Verifica que el WiFi este activo, reinicia el adaptador de red y prueba con otro "
            "dispositivo. Si el problema continua, escala al soporte.",
            "guia-soporte-internet-v0.1",
            "responder",
        )
    if any(palabra in texto for palabra in ("lento", "lenta", "rendimiento", "bloqueado")):
        return (
            "Cierra aplicaciones sin uso, revisa espacio en disco y reinicia el equipo si lleva "
            "mucho tiempo encendido.",
            "guia-soporte-rendimiento-v0.1",
            "responder",
        )
    if any(palabra in texto for palabra in ("impresora", "imprime", "impresion")):
        return (
            "Confirma que la impresora este encendida, con papel y sin trabajos atascados en cola.",
            "guia-soporte-impresora-v0.1",
            "responder",
        )
    return (
        "No encontre una respuesta autorizada; revisa la pregunta con un agente de soporte IT.",
        "fallback-no-encontrado",
        "escalar_a_humano",
    )


def lambda_handler(event, context):
    print("Request ID:", context.aws_request_id)

    payload = event
    # Permite probar desde la consola o desde una Function URL.
    if isinstance(event, dict) and "body" in event:
        payload = event["body"]
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                return build_response(400, {"status": "error", "message": "JSON invalido."})

    required = ["request_id", "user_id", "question", "channel"]
    missing = [field for field in required if not isinstance(payload, dict) or not payload.get(field)]
    if missing:
        return build_response(400, {"status": "error", "missing_fields": missing})

    answer, source, next_action = clasificar_pregunta(payload["question"])

    return build_response(
        200,
        {
            "status": "ok",
            "request_id": payload["request_id"],
            "answer": answer,
            "source": source,
            "next_action": next_action,
        },
    )
