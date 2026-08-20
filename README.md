# OrientaU - Agente Academico

Servicio FastAPI para orientar consultas academicas. La primera rebanada vertical valida JSON, coordina una respuesta mock y exige aprobacion antes de comunicar una decision. No necesita una API key ni un modelo real.

## Estructura

```
app/                 codigo de la aplicacion
data/                catalogo y ejemplos de contratos JSON
tests/               pruebas automatizadas
docs/                contrato y decisiones de arquitectura
.env.example         configuracion segura de ejemplo
.gitignore           archivos que no se versionan
README.md            como iniciar y verificar
```

## Contrato mock

`POST /agent/ask` recibe `question`, `student_id` y un `context` opcional. Responde JSON con `answer`, `sources` y `needs_approval`. Los ejemplos ejecutables estan en [data/agent_request.json](data/agent_request.json) y [data/agent_response.json](data/agent_response.json).

## Que entra, sale y queda fuera

Entra una pregunta y el contexto permitido del estudiante. Sale una respuesta mock trazable y marcada para aprobacion. El sistema no usa secretos, no llama modelos externos, no inscribe materias, no modifica historiales y no envia solicitudes.

## Entorno aislado y repetible

```powershell
# 1. Crear el entorno aislado
python -m venv .venv

# 2. Activarlo
.\.venv\Scripts\Activate.ps1

# 3. Instalar las versiones congeladas
pip install -r requirements.txt

# 4. Verificar las dependencias instaladas
pip freeze

# 5. Ejecutar el servidor
uvicorn app.main:app --reload
```

El servicio queda en `http://127.0.0.1:8000`; la documentacion interactiva esta en `http://127.0.0.1:8000/docs`.

## Peticion de ejemplo

```http
POST /agent/ask
Content-Type: application/json

{
  "question": "Que materias puedo tomar?",
  "student_id": "UAN-1042",
  "context": {
    "program": "Ingenieria de Sistemas",
    "semester": 5
  }
}
```

Consulta el contrato completo en [docs/contrato-api.md](docs/contrato-api.md), la arquitectura en [docs/arquitectura.md](docs/arquitectura.md) y la matriz con la evidencia de demo en [docs/evidencia-v0.1.md](docs/evidencia-v0.1.md).

## Verificacion y Git

```powershell
pytest tests/ -v
git status
git add .
git commit -m "feat: consultar prerrequisitos academicos"
git push
```

Cada commit debe representar una decision pequena, explicable y verificable.