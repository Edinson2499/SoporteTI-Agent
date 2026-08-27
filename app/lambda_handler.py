"""Punto de entrada AWS Lambda para API Gateway HTTP API."""

from __future__ import annotations

import base64
import json
from typing import Any

from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from app.agent import AgenteSoporteTI
from app.main import AgentAskRequest, AgentAskResponse


_agent = AgenteSoporteTI()


def _response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
	return {
		"statusCode": status_code,
		"headers": {"content-type": "application/json"},
		"body": json.dumps(body, ensure_ascii=False),
	}


def _request_body(event: dict[str, Any]) -> dict[str, Any]:
	raw_body = event.get("body") or "{}"
	if event.get("isBase64Encoded"):
		raw_body = base64.b64decode(raw_body).decode("utf-8")
	body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
	if not isinstance(body, dict):
		raise ValueError("El cuerpo debe ser un objeto JSON.")
	return body


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
	"""Procesa eventos v2 de API Gateway sin ejecutar cambios administrativos."""
	request_context = event.get("requestContext", {})
	http = request_context.get("http", {})
	method = (http.get("method") or event.get("httpMethod") or "").upper()
	path = event.get("rawPath") or event.get("path") or "/"

	if method == "GET" and path == "/health":
		return _response(200, {"status": "ok"})
	if method != "POST" or path != "/agent/ask":
		return _response(404, {"detail": "Ruta no encontrada."})

	try:
		request = AgentAskRequest.model_validate(_request_body(event))
	except (ValueError, json.JSONDecodeError, ValidationError) as exc:
		errors = exc.errors() if isinstance(exc, ValidationError) else []
		return _response(
			400,
			{"detail": "Solicitud invalida.", "errors": jsonable_encoder(errors)},
		)

	result = _agent.responder(request.question, request.user_id, request.context)
	return _response(200, AgentAskResponse(**result).model_dump())