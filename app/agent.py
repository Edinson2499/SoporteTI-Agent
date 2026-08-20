"""Orquestador determinista del agente de soporte TI."""

from __future__ import annotations

from typing import Any

from app.tools import buscar_conocimiento, crear_borrador_ticket


class AgenteSoporteTI:
    """Analiza un problema, consulta conocimiento local y aplica limites seguros."""

    def responder(self, question: str, user_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        articulo = buscar_conocimiento(question)
        dispositivo = (context or {}).get("device", "el equipo")

        if articulo is None:
            borrador = crear_borrador_ticket(question, user_id)
            return {
                "answer": (
                    f"No encontre una guia segura para {dispositivo}. Se preparo un borrador para "
                    "revision humana; no se enviara ni se ejecutara ningun cambio automaticamente."
                ),
                "sources": ["protocolo_escalamiento"],
                "needs_approval": True,
                "next_action": borrador["estado"],
            }

        pasos = " ".join(f"{indice}. {paso}" for indice, paso in enumerate(articulo["pasos"], start=1))
        return {
            "answer": f"Para {dispositivo}: {pasos}",
            "sources": [articulo["id"]],
            "needs_approval": False,
            "next_action": "seguir_pasos_seguros",
        }