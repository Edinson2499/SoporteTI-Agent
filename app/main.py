"""API HTTP para consulta de prerrequisitos academicos."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

from app.agent import AgenteAcademico
from app.tools import cargar_catalogo

app = FastAPI(
    title="Agente Academico API",
    description="Consulta prerrequisitos y prepara borradores de solicitud.",
    version="0.4.0",
)


class ConsultaRequest(BaseModel):
    estudiante: str = Field(..., min_length=2, max_length=100)
    materias_aprobadas: list[str] = Field(default_factory=list, max_length=80)

    @field_validator("materias_aprobadas")
    @classmethod
    def validar_codigos(cls, codigos: list[str]) -> list[str]:
        normalizados = [codigo.strip().upper() for codigo in codigos]
        if any(not codigo or not codigo.isalnum() for codigo in normalizados):
            raise ValueError("Cada codigo debe ser alfanumerico, por ejemplo PRO101.")
        return normalizados


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/materias")
def materias() -> list[dict[str, Any]]:
    """Expone el catalogo de consulta, sin datos de estudiantes."""
    return cargar_catalogo()


@app.post("/consulta")
def consulta(req: ConsultaRequest) -> dict[str, Any]:
    """Valida la entrada, consulta requisitos y devuelve el resultado JSON."""
    return AgenteAcademico().consultar(req.estudiante, req.materias_aprobadas)