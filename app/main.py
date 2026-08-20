"""API HTTP para consulta de prerrequisitos academicos."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from app.agent import AgenteAcademico, responder_pregunta_mock
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


class AgentAskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    student_id: str = Field(..., min_length=3, max_length=50)
    context: dict[str, Any] | None = None


class AgentAskResponse(BaseModel):
    answer: str
    sources: list[str]
    needs_approval: bool


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError) -> JSONResponse:
    """Convierte entradas JSON invalidas en un error HTTP 400 legible."""
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder({"detail": "Solicitud invalida.", "errors": exc.errors()}),
    )


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


@app.post("/agent/ask", response_model=AgentAskResponse)
def ask_agent(req: AgentAskRequest) -> AgentAskResponse:
    """Valida una pregunta y devuelve la primera respuesta mock del agente."""
    return AgentAskResponse(**responder_pregunta_mock(req.question, req.student_id, req.context))