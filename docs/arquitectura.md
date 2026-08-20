# Arquitectura

```mermaid
flowchart LR
    U[Estudiante] --> A[FastAPI /consulta]
    A --> V[Validacion Pydantic]
    V --> G[Agente Academico]
    G --> C[data/catalogo_materias.json]
    G --> R[Respuesta JSON y borrador]
```

El agente es un orquestador determinista: recibe datos validados, consulta el catalogo y devuelve una respuesta JSON. Mantener el catalogo como archivo versionado permite revisar cada cambio de prerrequisitos mediante Git.