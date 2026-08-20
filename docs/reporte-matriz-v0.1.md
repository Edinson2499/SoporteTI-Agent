# Reporte de Matriz - Base Tecnica v0.1

## Objetivo

Demostrar que OrientaU cuenta con una base tecnica minima, repetible y verificable: repositorio, configuracion segura, contratos JSON, API y evidencia de Git.

## Matriz de componentes

| Componente | Entrada | Salida esperada | Responsable | Evidencia o prueba |
| --- | --- | --- | --- | --- |
| `GET /health` | No recibe cuerpo | `200` y `{"status":"ok"}` | Backend/API | Prueba automatizada `test_health`. |
| `POST /agent/ask` | `question`, `student_id` y `context` opcional | `200` con `answer`, `sources` y `needs_approval` | Backend/contrato | `test_agent_ask_retorna_respuesta_mock_con_aprobacion`. |
| Validacion de API | JSON sin `question` o con tipos invalidos | `400` y detalle legible | Backend/contrato | `test_agent_ask_rechaza_question_faltante`. |
| Contratos JSON | [agent_request.json](../data/agent_request.json) | [agent_response.json](../data/agent_response.json) | Datos/contrato | `test_ejemplos_json_son_validos_y_contienen_el_contrato`. |
| Configuracion | [`.env.example`](../.env.example) | `API_KEY=` y `MODEL_NAME=mock` sin secretos | Configuracion/seguridad | [`.gitignore`](../.gitignore) excluye `.env` y `.venv/`. |
| Entorno aislado | `requirements.txt` | Dependencias instalables en `.venv` | Configuracion/seguridad | `python -m venv .venv` y `pip install -r requirements.txt`. |
| Repositorio | Cambios validados | Commit significativo y remoto actualizado | Integracion/Git | `git status --short`, `git log --oneline` y `git push`. |

## Evidencia de cierre

- Repositorio: `https://github.com/Edinson2499/SoporteTI-Agent`
- Contrato HTTP: [contrato-api.md](contrato-api.md)
- Arquitectura: [arquitectura.md](arquitectura.md)
- Pruebas: `8 passed` con `./.venv/Scripts/python.exe -m pytest tests/ -v`.
- Commit base v0.1: `581468a feat: establecer base tecnica v0.1`.

## Roles para el equipo

| Rol | Responsabilidad durante la demostracion |
| --- | --- |
| Integracion/Git | Muestra el repositorio, `git log --oneline` y el estado limpio. |
| Backend/API | Explica `GET /health`, `POST /agent/ask` y los estados `200` y `400`. |
| Datos/contrato | Presenta los JSON y los campos obligatorios de entrada y salida. |
| Configuracion/seguridad | Explica `.venv`, `requirements.txt`, `.env.example` y `.gitignore`. |

## Pendiente reconocido

La respuesta actual es mock y usa la fuente fija `plan_2026`. Antes de integrar un modelo real se requiere autenticacion, autorizacion por estudiante y una fuente academica persistente.