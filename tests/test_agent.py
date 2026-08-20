"""
tests/test_agent.py — Pruebas unitarias para el agente SoporteTI.

Las pruebas cubren:
  - buscar_conocimiento: casos encontrados y no encontrados.
  - consultar_diagnostico: reglas de internet, lentitud, impresora, cuentas.
  - crear_ticket / obtener_ticket: ciclo de vida basico del ticket.
  - Limites del agente: verificacion de acciones prohibidas.
  - API HTTP: endpoints /health, /iniciar, /responder, /escalar, /ticket.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from app.tools import buscar_conocimiento, consultar_diagnostico, crear_ticket, obtener_ticket
from app.agent import SoporteTIAgent, _verificar_limites


# ---------------------------------------------------------------------------
# Tests — buscar_conocimiento
# ---------------------------------------------------------------------------

class TestBuscarConocimiento:
    def test_encuentra_internet(self):
        resultado = buscar_conocimiento("no tengo internet en mi computador")
        assert resultado["encontrado"] is True
        assert resultado["datos"] is not None
        assert "causas" in resultado["datos"]
        assert "soluciones" in resultado["datos"]

    def test_encuentra_rendimiento(self):
        resultado = buscar_conocimiento("mi computador esta muy lento")
        assert resultado["encontrado"] is True
        assert resultado["archivo"] == "rendimiento"

    def test_encuentra_impresora(self):
        resultado = buscar_conocimiento("la impresora no imprime")
        assert resultado["encontrado"] is True
        assert resultado["archivo"] == "impresoras"

    def test_encuentra_cuentas(self):
        resultado = buscar_conocimiento("olvide mi contrasena")
        assert resultado["encontrado"] is True
        assert resultado["archivo"] == "cuentas"

    def test_encuentra_windows(self):
        resultado = buscar_conocimiento("windows tiene un error")
        assert resultado["encontrado"] is True
        assert resultado["archivo"] == "windows"

    def test_no_encuentra_problema_desconocido(self):
        resultado = buscar_conocimiento("el cafe de la oficina esta frio")
        assert resultado["encontrado"] is False
        assert resultado["datos"] is None


# ---------------------------------------------------------------------------
# Tests — consultar_diagnostico
# ---------------------------------------------------------------------------

class TestConsultarDiagnostico:
    def test_diagnostico_internet(self):
        resultado = consultar_diagnostico("no tengo internet")
        assert resultado["encontrado"] is True
        assert len(resultado["pasos"]) > 0

    def test_diagnostico_lentitud(self):
        resultado = consultar_diagnostico("el equipo esta muy lento")
        assert resultado["encontrado"] is True
        assert len(resultado["pasos"]) > 0

    def test_diagnostico_impresora(self):
        resultado = consultar_diagnostico("la impresora no funciona")
        assert resultado["encontrado"] is True
        assert len(resultado["pasos"]) > 0

    def test_diagnostico_cuenta(self):
        resultado = consultar_diagnostico("no puedo iniciar sesion, olvide mi contrasena")
        assert resultado["encontrado"] is True
        assert len(resultado["pasos"]) > 0

    def test_diagnostico_no_encontrado(self):
        resultado = consultar_diagnostico("problema de cafeteria")
        assert resultado["encontrado"] is False
        assert resultado["escalar"] is not None

    def test_diagnostico_incluye_escalado(self):
        resultado = consultar_diagnostico("no tengo internet")
        assert "escalar" in resultado
        assert isinstance(resultado["escalar"], str)


# ---------------------------------------------------------------------------
# Tests — crear_ticket / obtener_ticket
# ---------------------------------------------------------------------------

class TestTickets:
    def test_crear_ticket_retorna_id(self):
        ticket = crear_ticket("PC lenta", "El equipo tarda mucho en encender.", "usuario1")
        assert ticket["id"].startswith("TKT-")
        assert ticket["estado"] == "Pendiente"
        assert ticket["aprobado"] is False

    def test_ticket_recuperable(self):
        ticket = crear_ticket("Sin internet", "No hay conexion desde esta manana.", "usuario2")
        recuperado = obtener_ticket(ticket["id"])
        assert recuperado is not None
        assert recuperado["id"] == ticket["id"]

    def test_ticket_no_existe(self):
        assert obtener_ticket("TKT-XXXXXX") is None

    def test_ticket_contiene_campos_requeridos(self):
        ticket = crear_ticket("Error de Windows", "Pantalla azul al arrancar.")
        for campo in ("id", "usuario", "problema", "descripcion", "estado", "creado_en", "aprobado"):
            assert campo in ticket


# ---------------------------------------------------------------------------
# Tests — limites del agente
# ---------------------------------------------------------------------------

class TestLimitesAgente:
    def test_detecta_eliminar_archivos(self):
        assert _verificar_limites("eliminar archivos del disco") is True

    def test_detecta_cambiar_contrasena(self):
        assert _verificar_limites("cambiar contrasena del usuario") is True

    def test_detecta_instalar_software(self):
        assert _verificar_limites("instalar software en el equipo") is True

    def test_detecta_cerrar_ticket(self):
        assert _verificar_limites("cerrar ticket numero 123") is True

    def test_problema_normal_no_es_prohibido(self):
        assert _verificar_limites("mi computador esta lento") is False

    def test_problema_internet_no_es_prohibido(self):
        assert _verificar_limites("no tengo conexion a internet") is False


# ---------------------------------------------------------------------------
# Tests — SoporteTIAgent (con modelo mockeado)
# ---------------------------------------------------------------------------

def _mock_openai_client():
    """Retorna un mock de OpenAI que responde con texto simulado."""
    mock_cliente = MagicMock()
    mock_respuesta = MagicMock()
    mock_respuesta.choices[0].message.content = "Respuesta simulada del agente."
    mock_cliente.chat.completions.create.return_value = mock_respuesta
    return mock_cliente


class TestSoporteTIAgent:
    def test_iniciar_devuelve_respuesta(self):
        with patch("app.agent.OpenAI", return_value=_mock_openai_client()):
            agente = SoporteTIAgent()
        respuesta = agente.iniciar("Mi computador esta muy lento")
        assert isinstance(respuesta, str)
        assert len(respuesta) > 0

    def test_iniciar_bloquea_accion_prohibida(self):
        with patch("app.agent.OpenAI", return_value=_mock_openai_client()):
            agente = SoporteTIAgent()
        respuesta = agente.iniciar("eliminar archivos de mi disco")
        assert "limite" in respuesta.lower() or "accion" in respuesta.lower()

    def test_responder_sin_sesion_iniciada(self):
        with patch("app.agent.OpenAI", return_value=_mock_openai_client()):
            agente = SoporteTIAgent()
        respuesta = agente.responder("otro mensaje")
        assert "inicia la sesion" in respuesta.lower()

    def test_responder_continua_conversacion(self):
        with patch("app.agent.OpenAI", return_value=_mock_openai_client()):
            agente = SoporteTIAgent()
        agente.iniciar("no tengo internet")
        respuesta = agente.responder("ya reinicie el router pero sigue sin funcionar")
        assert isinstance(respuesta, str)
        assert len(respuesta) > 0

    def test_escalar_crea_ticket(self):
        with patch("app.agent.OpenAI", return_value=_mock_openai_client()):
            agente = SoporteTIAgent()
        agente.iniciar("error raro en windows", usuario="prueba")
        ticket = agente.escalar()
        assert ticket["id"].startswith("TKT-")
        assert ticket["estado"] == "Pendiente"

    def test_escalar_idempotente(self):
        with patch("app.agent.OpenAI", return_value=_mock_openai_client()):
            agente = SoporteTIAgent()
        agente.iniciar("error en windows")
        ticket1 = agente.escalar()
        ticket2 = agente.escalar()
        assert ticket1["id"] == ticket2["id"]

    def test_limite_iteraciones_escala(self):
        with patch("app.agent.OpenAI", return_value=_mock_openai_client()):
            agente = SoporteTIAgent()
        agente.max_iteraciones = 1
        agente.iniciar("pc lenta")
        respuesta = agente.responder("sigue lenta")
        assert "ticket" in respuesta.lower() or "limite" in respuesta.lower()


# ---------------------------------------------------------------------------
# Tests — API HTTP
# ---------------------------------------------------------------------------

from fastapi.testclient import TestClient
from app.main import app, _sesiones


@pytest.fixture(autouse=True)
def limpiar_sesiones():
    """Limpia las sesiones entre tests para evitar interferencias."""
    _sesiones.clear()
    yield
    _sesiones.clear()


client = TestClient(app)


class TestAPI:
    def _mock_agente(self, session_id: str, problema: str = "pc lenta") -> None:
        """Crea una sesion mockeada directamente en el dict de sesiones."""
        with patch("app.agent.OpenAI", return_value=_mock_openai_client()):
            agente = SoporteTIAgent()
        agente.iniciar(problema)
        _sesiones[session_id] = agente

    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_iniciar_sesion(self):
        with patch("app.main.SoporteTIAgent") as MockAgente:
            instancia = MagicMock()
            instancia.iniciar.return_value = "Hola, describe tu problema."
            MockAgente.return_value = instancia

            resp = client.post("/iniciar", json={
                "session_id": "sesion-001",
                "problema": "mi pc esta muy lenta",
                "usuario": "juan",
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == "sesion-001"
        assert isinstance(data["respuesta"], str)

    def test_responder_sesion_no_encontrada(self):
        resp = client.post("/responder", json={
            "session_id": "sesion-inexistente",
            "mensaje": "sigue sin funcionar",
        })
        assert resp.status_code == 404

    def test_responder_sesion_existente(self):
        self._mock_agente("sesion-002")
        with patch.object(_sesiones["sesion-002"], "responder", return_value="Intenta reiniciar."):
            resp = client.post("/responder", json={
                "session_id": "sesion-002",
                "mensaje": "sigue lenta",
            })
        assert resp.status_code == 200
        assert resp.json()["respuesta"] == "Intenta reiniciar."

    def test_escalar_sesion_no_encontrada(self):
        resp = client.post("/escalar", json={"session_id": "sesion-no-existe"})
        assert resp.status_code == 404

    def test_escalar_crea_ticket(self):
        self._mock_agente("sesion-003", "sin internet")
        resp = client.post("/escalar", json={
            "session_id": "sesion-003",
            "descripcion_adicional": "ya reinicie el router",
        })
        assert resp.status_code == 200
        ticket = resp.json()["ticket"]
        assert ticket["id"].startswith("TKT-")
        assert ticket["estado"] == "Pendiente"

    def test_consultar_ticket_no_existe(self):
        resp = client.get("/ticket/TKT-NOEXI")
        assert resp.status_code == 404

    def test_consultar_ticket_existente(self):
        self._mock_agente("sesion-004", "impresora rota")
        crear_resp = client.post("/escalar", json={"session_id": "sesion-004"})
        ticket_id = crear_resp.json()["ticket"]["id"]

        resp = client.get(f"/ticket/{ticket_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == ticket_id
