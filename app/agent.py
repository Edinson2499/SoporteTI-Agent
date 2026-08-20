"""
agent.py — Ciclo de decision del agente SoporteTI.

El agente sigue el ciclo:
  Objetivo → Contexto → Decision → Herramienta → Resultado → Limite
"""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

from app.tools import buscar_conocimiento, consultar_diagnostico, crear_ticket

# ---------------------------------------------------------------------------
# Limites del agente (lo que NO puede hacer)
# ---------------------------------------------------------------------------
_ACCIONES_PROHIBIDAS = [
    "eliminar archivos",
    "ejecutar comandos administrativos",
    "cambiar contrasena",
    "modificar configuraciones criticas",
    "instalar software",
    "cerrar ticket",
    "borrar ticket",
]

_SYSTEM_PROMPT = """Eres SoporteTI-Agent, un asistente de soporte tecnico.

Tu ciclo de operacion es:
1. Recibir el problema del usuario.
2. Analizar el contexto.
3. Decidir si necesitas mas informacion, consultar la base de conocimiento o crear un ticket.
4. Recomendar pasos claros y ordenados.
5. Si no puedes resolver el problema, crear un ticket de soporte.

LIMITES ESTRICTOS — nunca puedes:
- Eliminar archivos del usuario.
- Ejecutar comandos administrativos.
- Cambiar contrasenas directamente.
- Modificar configuraciones criticas del sistema.
- Instalar software de forma automatica.
- Cerrar o borrar tickets sin aprobacion humana.

Cuando la informacion de la base de conocimiento te sea proporcionada, usala
para fundamentar tu recomendacion. Responde siempre en español, de forma clara
y paso a paso."""


def _verificar_limites(texto: str) -> bool:
    """Retorna True si el texto solicita una accion prohibida."""
    texto_lower = texto.lower()
    return any(accion in texto_lower for accion in _ACCIONES_PROHIBIDAS)


def _construir_contexto_herramientas(problema: str) -> str:
    """
    Ejecuta las herramientas de consulta y construye un bloque de contexto
    para inyectar en el prompt del modelo.
    """
    partes: list[str] = []

    # Tool 1: knowledge base
    resultado_kb = buscar_conocimiento(problema)
    if resultado_kb["encontrado"] and resultado_kb["datos"]:
        datos = resultado_kb["datos"]
        partes.append("=== BASE DE CONOCIMIENTO ===")
        partes.append(f"Problema: {datos.get('problema', '')}")
        causas = datos.get("causas", [])
        if causas:
            partes.append("Causas posibles:\n" + "\n".join(f"  - {c}" for c in causas))
        soluciones = datos.get("soluciones", [])
        if soluciones:
            partes.append("Soluciones sugeridas:\n" + "\n".join(f"  - {s}" for s in soluciones))
        preguntas = datos.get("preguntas_diagnostico", [])
        if preguntas:
            partes.append("Preguntas de diagnostico:\n" + "\n".join(f"  - {p}" for p in preguntas))

    # Tool 2: reglas de diagnostico
    resultado_diag = consultar_diagnostico(problema)
    if resultado_diag["encontrado"]:
        partes.append("=== DIAGNOSTICO AUTOMATICO ===")
        partes.append("Pasos recomendados:\n" + "\n".join(f"  {i+1}. {p}" for i, p in enumerate(resultado_diag["pasos"])))
        if resultado_diag.get("escalar"):
            partes.append(f"Si no se resuelve: {resultado_diag['escalar']}")

    return "\n".join(partes)


class SoporteTIAgent:
    """
    Agente de soporte tecnico.

    Parametros
    ----------
    modelo : str
        Modelo de lenguaje a usar (por defecto gpt-4o-mini).
    max_iteraciones : int
        Numero maximo de turnos de conversacion por sesion.
    """

    def __init__(self, modelo: str = "gpt-4o-mini", max_iteraciones: int = 10) -> None:
        self.modelo = modelo
        self.max_iteraciones = max_iteraciones
        self._cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        self.historial: list[dict[str, str]] = []
        self._problema_inicial: str = ""
        self._iteraciones: int = 0
        self._ticket_creado: dict[str, Any] | None = None

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    def iniciar(self, problema: str, usuario: str = "anonimo") -> str:
        """
        Inicia una nueva sesion con el problema del usuario.

        Parametros
        ----------
        problema : str  Descripcion inicial del problema.
        usuario  : str  Identificador del usuario.

        Retorna
        -------
        str — primera respuesta del agente.
        """
        if _verificar_limites(problema):
            return (
                "Lo siento, no puedo realizar esa accion. "
                "Por favor describe el problema tecnico para que pueda ayudarte."
            )

        self.historial = [{"role": "system", "content": _SYSTEM_PROMPT}]
        self._problema_inicial = problema
        self._iteraciones = 0
        self._ticket_creado = None
        self._usuario = usuario

        contexto_herramientas = _construir_contexto_herramientas(problema)

        mensaje_usuario = problema
        if contexto_herramientas:
            mensaje_usuario = (
                f"{problema}\n\n"
                f"[Contexto obtenido por las herramientas del agente]\n{contexto_herramientas}"
            )

        self.historial.append({"role": "user", "content": mensaje_usuario})
        return self._llamar_modelo()

    def responder(self, mensaje: str) -> str:
        """
        Continua la conversacion con un nuevo mensaje del usuario.

        Parametros
        ----------
        mensaje : str  Nuevo mensaje del usuario.

        Retorna
        -------
        str — respuesta del agente.
        """
        if not self.historial:
            return "Por favor inicia la sesion describiendo tu problema primero."

        if self._iteraciones >= self.max_iteraciones:
            return self._escalar_a_ticket()

        if _verificar_limites(mensaje):
            return (
                "Lo siento, esa accion esta fuera de mis limites. "
                "Por favor describe el problema tecnico."
            )

        self.historial.append({"role": "user", "content": mensaje})
        return self._llamar_modelo()

    def escalar(self, descripcion_adicional: str = "") -> dict[str, Any]:
        """
        Escala el caso creando un ticket de soporte (borrador).

        Retorna
        -------
        dict — datos del ticket creado.
        """
        if self._ticket_creado:
            return self._ticket_creado

        descripcion = self._problema_inicial
        if descripcion_adicional:
            descripcion += f"\n\nInformacion adicional: {descripcion_adicional}"

        self._ticket_creado = crear_ticket(
            problema=self._problema_inicial[:80],
            descripcion=descripcion,
            usuario=getattr(self, "_usuario", "anonimo"),
        )
        return self._ticket_creado

    # ------------------------------------------------------------------
    # Metodos internos
    # ------------------------------------------------------------------

    def _llamar_modelo(self) -> str:
        self._iteraciones += 1
        try:
            respuesta = self._cliente.chat.completions.create(
                model=self.modelo,
                messages=self.historial,  # type: ignore[arg-type]
                temperature=0.3,
                max_tokens=800,
            )
            contenido = respuesta.choices[0].message.content or ""
            self.historial.append({"role": "assistant", "content": contenido})
            return contenido
        except Exception as exc:  # noqa: BLE001
            return f"Error al contactar el modelo de IA: {exc}"

    def _escalar_a_ticket(self) -> str:
        ticket = self.escalar()
        return (
            f"Se ha alcanzado el limite de interacciones. "
            f"He creado un ticket de soporte:\n"
            f"  ID: {ticket['id']}\n"
            f"  Estado: {ticket['estado']}\n"
            f"Un tecnico revisara tu caso. El ticket requiere aprobacion humana antes de procesarse."
        )
