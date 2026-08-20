"""
main.py — API HTTP del agente SoporteTI.

Endpoints:
  POST /iniciar        — inicia una nueva sesion con el problema del usuario.
  POST /responder      — continua la conversacion en una sesion existente.
  POST /escalar        — escala el caso creando un ticket de soporte.
  GET  /ticket/{id}    — consulta el estado de un ticket.
  GET  /health         — verificacion de salud del servicio.
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.agent import SoporteTIAgent
from app.tools import obtener_ticket

app = FastAPI(
    title="SoporteTI-Agent API",
    description="Agente de soporte tecnico impulsado por IA.",
    version="0.1.0",
)

# Almacenamiento en memoria de sesiones activas {session_id: SoporteTIAgent}
_sesiones: dict[str, SoporteTIAgent] = {}


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class IniciarRequest(BaseModel):
    session_id: str = Field(..., description="Identificador unico de la sesion.")
    problema: str = Field(..., min_length=5, description="Descripcion del problema tecnico.")
    usuario: str = Field(default="anonimo", description="Nombre o ID del usuario.")


class IniciarResponse(BaseModel):
    session_id: str
    respuesta: str


class ResponderRequest(BaseModel):
    session_id: str = Field(..., description="Identificador de la sesion activa.")
    mensaje: str = Field(..., min_length=1, description="Nuevo mensaje del usuario.")


class ResponderResponse(BaseModel):
    session_id: str
    respuesta: str


class EscalarRequest(BaseModel):
    session_id: str = Field(..., description="Identificador de la sesion activa.")
    descripcion_adicional: str = Field(default="", description="Informacion extra para el ticket.")


class EscalarResponse(BaseModel):
    ticket: dict[str, Any]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> dict[str, str]:
    """Verificacion de salud del servicio."""
    return {"status": "ok"}


@app.post("/iniciar", response_model=IniciarResponse)
def iniciar(req: IniciarRequest) -> IniciarResponse:
    """Inicia una nueva sesion de soporte."""
    agente = SoporteTIAgent()
    respuesta = agente.iniciar(problema=req.problema, usuario=req.usuario)
    _sesiones[req.session_id] = agente
    return IniciarResponse(session_id=req.session_id, respuesta=respuesta)


@app.post("/responder", response_model=ResponderResponse)
def responder(req: ResponderRequest) -> ResponderResponse:
    """Continua la conversacion en una sesion existente."""
    agente = _sesiones.get(req.session_id)
    if agente is None:
        raise HTTPException(status_code=404, detail="Sesion no encontrada. Inicia una nueva sesion.")
    respuesta = agente.responder(req.mensaje)
    return ResponderResponse(session_id=req.session_id, respuesta=respuesta)


@app.post("/escalar", response_model=EscalarResponse)
def escalar(req: EscalarRequest) -> EscalarResponse:
    """Escala el caso creando un ticket de soporte (borrador)."""
    agente = _sesiones.get(req.session_id)
    if agente is None:
        raise HTTPException(status_code=404, detail="Sesion no encontrada. Inicia una nueva sesion.")
    ticket = agente.escalar(req.descripcion_adicional)
    return EscalarResponse(ticket=ticket)


@app.get("/ticket/{ticket_id}")
def consultar_ticket(ticket_id: str) -> dict[str, Any]:
    """Consulta el estado de un ticket de soporte."""
    ticket = obtener_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado.")
    return ticket
