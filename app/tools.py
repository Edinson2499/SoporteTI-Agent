"""Servicios deterministas para consultar prerrequisitos academicos."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CATALOGO_PATH = Path(__file__).resolve().parent.parent / "data" / "catalogo_materias.json"


def cargar_catalogo() -> list[dict[str, Any]]:
    """Carga el catalogo de materias versionado con la aplicacion."""
    with _CATALOGO_PATH.open(encoding="utf-8") as archivo:
        return json.load(archivo)["materias"]


def consultar_prerrequisitos(materias_aprobadas: list[str]) -> dict[str, list[dict[str, Any]]]:
    """Clasifica las materias del catalogo segun el historial aprobado."""
    aprobadas = {codigo.upper() for codigo in materias_aprobadas}
    disponibles: list[dict[str, Any]] = []
    bloqueadas: list[dict[str, Any]] = []

    for materia in cargar_catalogo():
        codigo = materia["codigo"]
        if codigo in aprobadas:
            continue

        faltantes = [requisito for requisito in materia["prerrequisitos"] if requisito not in aprobadas]
        if faltantes:
            bloqueadas.append({**materia, "prerrequisitos_faltantes": faltantes})
        else:
            disponibles.append(materia)

    return {"materias_disponibles": disponibles, "materias_bloqueadas": bloqueadas}


def crear_borrador_solicitud(estudiante: str, materias: list[dict[str, Any]]) -> dict[str, Any]:
    """Prepara, sin enviar, una solicitud para revision del coordinador."""
    codigos = [materia["codigo"] for materia in materias]
    nombres = [materia["nombre"] for materia in materias]
    return {
        "destinatario": "Coordinacion Academica",
        "asunto": "Solicitud de revision de inscripcion",
        "estado": "borrador_no_enviado",
        "materias_solicitadas": codigos,
        "mensaje": (
            f"Cordial saludo. Soy {estudiante} y solicito revisar mi posible inscripcion "
            f"en: {', '.join(nombres)}. He verificado los prerrequisitos con el sistema."
        ),
    }
