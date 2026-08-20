"""Herramientas locales y seguras del agente de soporte TI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_BASE_CONOCIMIENTO = Path(__file__).resolve().parent.parent / "data" / "conocimiento_soporte.json"


def cargar_base_conocimiento() -> list[dict[str, Any]]:
    """Carga los articulos de soporte versionados con la aplicacion."""
    with _BASE_CONOCIMIENTO.open(encoding="utf-8") as archivo:
        return json.load(archivo)["articulos"]


def buscar_conocimiento(problema: str) -> dict[str, Any] | None:
    """Encuentra el primer articulo cuyo conjunto de palabras clave coincida."""
    texto = problema.lower()
    for articulo in cargar_base_conocimiento():
        if any(palabra in texto for palabra in articulo["palabras_clave"]):
            return articulo
    return None


def crear_borrador_ticket(problema: str, usuario: str) -> dict[str, str]:
    """Prepara un borrador; no crea ni modifica tickets reales."""
    return {
        "estado": "borrador_pendiente_aprobacion",
        "titulo": f"Revision de soporte para {usuario}",
        "descripcion": problema,
    }