"""Pruebas del flujo validar -> consultar -> devolver JSON."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.agent import AgenteAcademico
from app.main import app
from app.tools import consultar_prerrequisitos

client = TestClient(app)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_ejemplos_json_son_validos_y_contienen_el_contrato():
    request = json.loads((DATA_DIR / "agent_request.json").read_text(encoding="utf-8"))
    response = json.loads((DATA_DIR / "agent_response.json").read_text(encoding="utf-8"))
    assert {"question", "student_id", "context"} <= request.keys()
    assert {"answer", "sources", "needs_approval"} <= response.keys()
    assert isinstance(response["sources"], list)
    assert isinstance(response["needs_approval"], bool)


def test_consulta_identifica_materias_disponibles_y_bloqueadas():
    resultado = consultar_prerrequisitos(["mat101", "pro101"])
    assert [materia["codigo"] for materia in resultado["materias_disponibles"]] == ["PRO201", "MAT201"]
    assert resultado["materias_bloqueadas"][0]["prerrequisitos_faltantes"] == ["PRO201"]


def test_agente_prepara_borrador_sin_enviarlo():
    resultado = AgenteAcademico().consultar("Ana Perez", ["MAT101", "PRO101"])
    assert resultado["solicitud"]["estado"] == "borrador_no_enviado"
    assert resultado["solicitud"]["materias_solicitadas"] == ["PRO201", "MAT201"]
    assert "No inscribe materias." in resultado["limites"]


def test_health():
    respuesta = client.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


def test_consulta_api_retorna_json_academico():
    respuesta = client.post(
        "/consulta",
        json={"estudiante": "Ana Perez", "materias_aprobadas": ["mat101", "pro101"]},
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["materias_aprobadas"] == ["MAT101", "PRO101"]
    assert datos["solicitud"]["estado"] == "borrador_no_enviado"


def test_consulta_api_rechaza_codigo_invalido():
    respuesta = client.post(
        "/consulta",
        json={"estudiante": "Ana Perez", "materias_aprobadas": ["PRO-101"]},
    )
    assert respuesta.status_code == 400


def test_agent_ask_retorna_respuesta_mock_con_aprobacion():
    respuesta = client.post(
        "/agent/ask",
        json={
            "question": "Que materias puedo tomar?",
            "student_id": "UAN-1042",
            "context": {"program": "Ingenieria de Sistemas", "semester": 5},
        },
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert "Ingenieria de Sistemas" in datos["answer"]
    assert datos["sources"] == ["plan_2026"]
    assert datos["needs_approval"] is True


def test_agent_ask_rechaza_question_faltante():
    respuesta = client.post("/agent/ask", json={"student_id": "UAN-1042"})
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Solicitud invalida."