# SoporteTI-Agent

Base tecnica v0.1 de un agente de soporte TI. Recibe una incidencia, analiza el contexto, consulta una base de conocimiento local, devuelve pasos seguros y escala los casos sin guia para aprobacion humana.

## Estructura

```
app/                 API, orquestador y herramientas
data/                conocimiento y contratos JSON
tests/               pruebas automatizadas
docs/                contrato, arquitectura, mapa y evidencia
.env.example         configuracion segura de ejemplo
.gitignore           archivos que no se versionan
```

## Arquitectura

El agente sigue el ciclo: **objetivo -> contexto -> decision -> herramientas -> observacion -> limites**. Consulta el [mapa de arquitectura](docs/arquitectura.md) y el [contrato HTTP](docs/contrato-api.md).

## Entorno aislado y ejecucion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest tests/ -v
uvicorn app.main:app --reload
```

La API queda en `http://127.0.0.1:8000` y la documentacion interactiva en `http://127.0.0.1:8000/docs`.

## Ejemplo

```http
POST /agent/ask
Content-Type: application/json

{
  "question": "No tengo internet en mi portatil",
  "user_id": "USR-1042",
  "context": {
    "device": "portatil",
    "operating_system": "Windows 11"
  }
}
```

Los contratos de referencia estan en [data/agent_request.json](data/agent_request.json) y [data/agent_response.json](data/agent_response.json). La base de conocimiento local esta en [data/conocimiento_soporte.json](data/conocimiento_soporte.json).

## Limites

El agente no ejecuta comandos administrativos, no instala software, no cambia contrasenas, no modifica configuraciones criticas, no elimina archivos y no envia tickets. Cuando no encuentra una guia, prepara un borrador y devuelve `needs_approval: true`.

## Evidencia

La [matriz de la base tecnica](docs/reporte-matriz-v0.1.md) resume componentes, responsabilidades y pruebas. Usa `git status`, `git log --oneline` y `git push` para registrar decisiones pequenas y verificables.