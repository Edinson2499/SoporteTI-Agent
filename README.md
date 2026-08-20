# Agente Academico

Servicio FastAPI que consulta prerrequisitos desde un catalogo JSON y prepara un borrador de solicitud para el coordinador. El resultado es determinista y no necesita una clave de IA.

## Estructura

```
app/                 codigo de la aplicacion
data/                catalogo JSON de materias
tests/               pruebas automatizadas
docs/                contrato y decisiones de arquitectura
.env.example         configuracion segura de ejemplo
.gitignore           archivos que no se versionan
README.md            como iniciar y verificar
```

## Que entra, sale y queda fuera

Entra el nombre del estudiante y los codigos de materias aprobadas. Sale JSON con materias disponibles, materias bloqueadas y un borrador no enviado. El sistema no inscribe materias, no modifica historiales y no envia solicitudes.

## Ejecucion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

El servicio queda en `http://127.0.0.1:8000`; la documentacion interactiva esta en `http://127.0.0.1:8000/docs`.

## Consulta de ejemplo

```http
POST /consulta
Content-Type: application/json

{
  "estudiante": "Ana Perez",
  "materias_aprobadas": ["MAT101", "PRO101"]
}
```

Consulta el contrato completo en [docs/contrato-api.md](docs/contrato-api.md) y la arquitectura en [docs/arquitectura.md](docs/arquitectura.md).

## Verificacion y Git

```powershell
pytest tests/ -v
git status
git add .
git commit -m "feat: consultar prerrequisitos academicos"
git push
```

Cada commit debe representar una decision pequena, explicable y verificable.