# Evidencia de Cierre v0.1

## Demostracion en dos minutos

1. Mostrar el repositorio, [README.md](../README.md) y las carpetas `app/`, `data/`, `tests/` y `docs/`.
2. Abrir los contratos [agent_request.json](../data/agent_request.json) y [agent_response.json](../data/agent_response.json).
3. Ejecutar `GET /health` y enviar el request a `POST /agent/ask`.
4. Explicar `sources`, `next_action` y el limite `needs_approval` para un caso sin guia.
5. Ejecutar las pruebas y mostrar `git log --oneline` y `git status --short`.

## Pendiente reconocido

La respuesta usa conocimiento local y el borrador de ticket no se persiste. Faltan autenticacion, persistencia, observabilidad y un gestor de secretos para despliegue cloud.