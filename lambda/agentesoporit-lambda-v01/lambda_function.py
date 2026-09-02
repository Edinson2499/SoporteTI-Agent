import json
import logging

from agent import diagnosticar
from tools import validar_evento

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def build_response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(payload, ensure_ascii=False),
    }


def _extraer_payload(event):
    payload = event
    # Permite probar desde la consola, Function URL o API Gateway (RNF01, RNF05).
    if isinstance(event, dict) and "body" in event:
        payload = event["body"]
        if isinstance(payload, str):
            payload = json.loads(payload)
    if not isinstance(payload, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON.")
    return payload


def lambda_handler(event, context):
    print("Request ID:", getattr(context, "aws_request_id", "sin-contexto"))

    try:
        payload = _extraer_payload(event)
    except (ValueError, json.JSONDecodeError):
        return build_response(400, {"status": "error", "message": "JSON invalido."})

    missing = validar_evento(payload)
    if missing:
        return build_response(400, {"status": "error", "missing_fields": missing})

    try:
        decision = diagnosticar(payload["question"], payload["user_id"], payload.get("context"))

        # RF11 / RNF08: log estructurado sin contraseñas, tokens ni datos privados del usuario.
        print(json.dumps({
            "event": "agent_request",
            "request_id": payload["request_id"],
            "channel": payload["channel"],
            "action": decision["next_action"],
        }, ensure_ascii=False))

        respuesta = {
            "status": "ok",
            "request_id": payload["request_id"],
            "answer": decision["answer"],
            "next_action": decision["next_action"],
        }
        if decision.get("source"):
            respuesta["source"] = decision["source"]
        if "ticket_borrador" in decision:
            respuesta["ticket_borrador"] = decision["ticket_borrador"]

        return build_response(200, respuesta)
    except Exception:
        # RF10/RNF05: no se expone informacion interna al cliente ante errores inesperados.
        logger.exception("Error inesperado procesando request_id=%s", payload.get("request_id"))
        return build_response(500, {"status": "error", "message": "Error interno del agente."})
