# Evidencia de cierre v0.1

## Repositorio

- URL: `https://github.com/Edinson2499/SoporteTI-Agent`
- Estructura: `app/`, `data/`, `tests/` y `docs/`.
- Configuracion segura: `.env.example` describe variables vacias y `.gitignore` excluye `.env` y `.venv/`.

## Matriz del taller

| Componente | Entrada | Salida | Responsable | Prueba |
| --- | --- | --- | --- | --- |
| `GET /health` | Sin cuerpo | `{"status":"ok"}` | Backend/API | `test_health` valida `200`. |
| `POST /agent/ask` | `question`, `student_id`, `context` opcional | `answer`, `sources`, `needs_approval` | Backend/contrato | Pruebas de respuesta `200` y JSON invalido `400`. |
| JSON | `data/agent_request.json` | `data/agent_response.json` | Datos/contrato | `test_ejemplos_json_son_validos_y_contienen_el_contrato`. |
| Configuracion | `.env.example` | Variables seguras de ejemplo | Configuracion/seguridad | Revision de `.gitignore`: no versiona `.env` ni `.venv/`. |
| Repositorio | Cambios validados | Commit y remoto actualizado | Integracion/Git | `git status --short`, `git log --oneline` y `git push`. |

Los roles son responsabilidades, no personas fijas: en un equipo de tres o cuatro integrantes se pueden asignar y rotar antes de la demostracion.

## Demostracion en dos minutos

1. Mostrar la URL del repositorio, [README.md](../README.md) y la estructura de carpetas.
2. Abrir [data/agent_request.json](../data/agent_request.json) y [data/agent_response.json](../data/agent_response.json); explicar campos y tipos.
3. Ejecutar `GET /health` y enviar el JSON de ejemplo a `POST /agent/ask`; explicar la respuesta `200`, `sources` y `needs_approval`.
4. Enviar un cuerpo sin `question`; mostrar el error `400` legible.
5. Ejecutar `git log --oneline` y `git status --short`.

## Pendiente reconocido

La v0.1 usa una respuesta mock y un origen de trazabilidad fijo (`plan_2026`). Una siguiente iteracion debe incorporar autenticacion, autorizacion por estudiante y una fuente academica persistente antes de conectar un modelo real.