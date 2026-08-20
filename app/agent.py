"""Orquestador del caso de uso de consulta academica."""

from __future__ import annotations

from typing import Any

from app.tools import consultar_prerrequisitos, crear_borrador_solicitud


class AgenteAcademico:
    """Consulta requisitos y prepara un borrador, sin modificar matriculas."""

    def consultar(self, estudiante: str, materias_aprobadas: list[str]) -> dict[str, Any]:
        resultado = consultar_prerrequisitos(materias_aprobadas)
        disponibles = resultado["materias_disponibles"]
        return {
            "estudiante": estudiante,
            "materias_aprobadas": sorted({codigo.upper() for codigo in materias_aprobadas}),
            **resultado,
            "solicitud": crear_borrador_solicitud(estudiante, disponibles) if disponibles else None,
            "limites": [
                "No inscribe materias.",
                "No modifica el historial academico.",
                "No envia la solicitud al coordinador.",
            ],
        }


def responder_pregunta_mock(question: str, student_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Coordina una respuesta de prueba sin consultar un modelo ni secretos."""
    programa = (context or {}).get("program", "tu programa academico")
    return {
        "answer": (
            f"{student_id}, puedes revisar las materias y sus prerrequisitos en el plan de "
            f"estudios de {programa}. Esta respuesta es una simulacion para validar el contrato."
        ),
        "sources": ["plan_2026"],
        "needs_approval": True,
    }