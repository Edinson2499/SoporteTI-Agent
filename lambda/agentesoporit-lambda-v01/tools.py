import json
import os
import re

_KB_PATH = os.path.join(os.path.dirname(__file__), "conocimiento_soporte.json")
_REQUIRED_FIELDS = ["request_id", "user_id", "question", "channel"]


def validar_evento(payload):
    """Verifica que el payload tenga los campos obligatorios (RF02). Devuelve la lista de faltantes."""
    if not isinstance(payload, dict):
        return list(_REQUIRED_FIELDS)
    return [campo for campo in _REQUIRED_FIELDS if not payload.get(campo)]


def cargar_base_conocimiento():
    """Carga los articulos autorizados desde conocimiento_soporte.json (RF05)."""
    with open(_KB_PATH, encoding="utf-8") as archivo:
        return json.load(archivo)["articulos"]


_BASE_CONOCIMIENTO = cargar_base_conocimiento()


def buscar_conocimiento(question):
    """Encuentra el primer articulo cuyas palabras clave coincidan con la pregunta, o None."""
    texto = question.lower()
    for articulo in _BASE_CONOCIMIENTO:
        if any(re.search(rf"\b{re.escape(palabra)}\b", texto) for palabra in articulo["palabras_clave"]):
            return articulo
    return None


def crear_borrador_ticket(question, user_id):
    """Prepara un borrador para revision humana; no crea ni cierra tickets reales (RF09)."""
    return {
        "estado": "borrador_pendiente_aprobacion",
        "titulo": f"Revision de soporte para {user_id}",
        "descripcion": question,
    }
