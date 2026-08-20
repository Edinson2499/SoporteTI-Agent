"""
tools.py — Herramientas disponibles para el agente SoporteTI.

Tool 1: buscar_conocimiento  — busca en la base de conocimiento local.
Tool 2: consultar_diagnostico — aplica reglas de diagnostico sencillas.
Tool 3: crear_ticket         — crea un borrador de ticket de soporte.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Ruta base de la knowledge base
# ---------------------------------------------------------------------------
_KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"

# Palabras clave que mapean texto libre a archivos JSON
_KEYWORD_MAP: dict[str, str] = {
    "internet": "internet",
    "red": "internet",
    "wifi": "internet",
    "conexion": "internet",
    "conectar": "internet",
    "lento": "rendimiento",
    "lenta": "rendimiento",
    "rendimiento": "rendimiento",
    "ram": "rendimiento",
    "disco": "rendimiento",
    "impresora": "impresoras",
    "imprimir": "impresoras",
    "impresion": "impresoras",
    "windows": "windows",
    "pantalla azul": "windows",
    "bsod": "windows",
    "error": "windows",
    "actualizacion": "windows",
    "contrasena": "cuentas",
    "cuenta": "cuentas",
    "password": "cuentas",
    "usuario": "cuentas",
    "sesion": "cuentas",
}


def buscar_conocimiento(problema: str) -> dict[str, Any]:
    """
    Busca en la base de conocimiento el articulo mas relevante para el
    problema descrito.

    Parametros
    ----------
    problema : str
        Descripcion libre del problema del usuario.

    Retorna
    -------
    dict con las claves: encontrado (bool), archivo (str), datos (dict | None)
    """
    problema_lower = problema.lower()
    archivo: str | None = None

    for keyword, nombre_archivo in _KEYWORD_MAP.items():
        if keyword in problema_lower:
            archivo = nombre_archivo
            break

    if archivo is None:
        return {"encontrado": False, "archivo": None, "datos": None}

    ruta = _KNOWLEDGE_DIR / f"{archivo}.json"
    if not ruta.exists():
        return {"encontrado": False, "archivo": archivo, "datos": None}

    with ruta.open(encoding="utf-8") as fh:
        datos = json.load(fh)

    return {"encontrado": True, "archivo": archivo, "datos": datos}


# ---------------------------------------------------------------------------
# Reglas de diagnostico
# ---------------------------------------------------------------------------

_REGLAS_DIAGNOSTICO: list[dict[str, Any]] = [
    {
        "condicion": lambda p: "internet" in p or "wifi" in p or "red" in p or "conexion" in p,
        "pasos": [
            "Verificar si otros dispositivos tienen Internet en la misma red.",
            "Revisar que el adaptador WiFi o cable de red este activo.",
            "Reiniciar el router desconectandolo 60 segundos.",
            "Ejecutar el solucionador de problemas de red de Windows.",
        ],
        "escalar": "Si ningun dispositivo tiene Internet, el problema puede ser del proveedor. Escalar al soporte de red.",
    },
    {
        "condicion": lambda p: "lento" in p or "lenta" in p or "rendimiento" in p,
        "pasos": [
            "Abrir el Administrador de Tareas y verificar el uso de CPU, RAM y disco.",
            "Cerrar aplicaciones que consuman muchos recursos.",
            "Revisar el espacio disponible en el disco C:.",
            "Reiniciar el equipo si lleva mucho tiempo encendido.",
        ],
        "escalar": "Si la lentitud persiste despues de reiniciar, escalar para revision de hardware.",
    },
    {
        "condicion": lambda p: "impresora" in p or "imprimir" in p,
        "pasos": [
            "Verificar que la impresora este encendida y conectada.",
            "Limpiar la cola de impresion desde Configuracion > Impresoras.",
            "Reiniciar el servicio de cola de impresion (Print Spooler).",
            "Reinstalar el driver de la impresora si el problema persiste.",
        ],
        "escalar": "Si la impresora muestra error fisico, escalar para revision de hardware.",
    },
    {
        "condicion": lambda p: "contrasena" in p or "cuenta" in p or "sesion" in p or "password" in p,
        "pasos": [
            "Usar la opcion '¿Olvidaste tu contrasena?' en la pantalla de inicio.",
            "Verificar que no haya activado el bloqueo de mayusculas.",
            "Si es cuenta Microsoft, recuperar desde account.microsoft.com.",
        ],
        "escalar": "Si la cuenta esta bloqueada por politica corporativa, escalar al administrador.",
    },
]


def consultar_diagnostico(problema: str) -> dict[str, Any]:
    """
    Aplica reglas de diagnostico sencillas y devuelve pasos sugeridos.

    Parametros
    ----------
    problema : str
        Descripcion libre del problema del usuario.

    Retorna
    -------
    dict con las claves: encontrado (bool), pasos (list[str]), escalar (str | None)
    """
    problema_lower = problema.lower()

    for regla in _REGLAS_DIAGNOSTICO:
        if regla["condicion"](problema_lower):
            return {
                "encontrado": True,
                "pasos": regla["pasos"],
                "escalar": regla["escalar"],
            }

    return {
        "encontrado": False,
        "pasos": [],
        "escalar": "No se encontro un diagnostico automatico. Escalar a soporte tecnico.",
    }


# ---------------------------------------------------------------------------
# Tickets (solo borrador — no modifica registros sin aprobacion humana)
# ---------------------------------------------------------------------------

# En produccion esto se guardaria en una BD. Para el prototipo usamos memoria.
_tickets_en_memoria: dict[str, dict[str, Any]] = {}


def crear_ticket(problema: str, descripcion: str, usuario: str = "anonimo") -> dict[str, Any]:
    """
    Crea un BORRADOR de ticket de soporte. El agente NO puede cerrarlo ni
    modificarlo; requiere aprobacion humana.

    Parametros
    ----------
    problema    : str  Titulo breve del problema.
    descripcion : str  Descripcion completa del caso.
    usuario     : str  Identificador del usuario (opcional).

    Retorna
    -------
    dict con los campos del ticket creado.
    """
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
    ticket = {
        "id": ticket_id,
        "usuario": usuario,
        "problema": problema,
        "descripcion": descripcion,
        "estado": "Pendiente",
        "creado_en": datetime.utcnow().isoformat() + "Z",
        "aprobado": False,
    }
    _tickets_en_memoria[ticket_id] = ticket
    return ticket


def obtener_ticket(ticket_id: str) -> dict[str, Any] | None:
    """Retorna el ticket con el id dado, o None si no existe."""
    return _tickets_en_memoria.get(ticket_id)
