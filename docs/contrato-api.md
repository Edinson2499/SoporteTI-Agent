# Contrato de la API

## `GET /health`

No recibe cuerpo y responde `200` con:

```json
{"status": "ok"}
```

## `POST /agent/ask`

Valida una pregunta y coordina la primera respuesta mock del agente.

### Entrada

```json
{
  "question": "Que materias puedo tomar?",
  "student_id": "UAN-1042",
  "context": {
    "program": "Ingenieria de Sistemas",
    "semester": 5
  }
}
```

| Campo | Tipo | Obligatorio | Uso |
| --- | --- | --- | --- |
| `question` | texto | Si | Pregunta del estudiante. |
| `student_id` | texto | Si | Identifica el contexto permitido. |
| `context` | objeto | No | Datos adicionales de la solicitud. |

### Salida `200`

```json
{
  "answer": "Puedes revisar las materias disponibles y sus prerrequisitos.",
  "sources": ["plan_2026"],
  "needs_approval": true
}
```

| Campo | Tipo | Uso |
| --- | --- | --- |
| `answer` | texto | Respuesta mock del agente. |
| `sources` | arreglo | Trazabilidad de la respuesta. |
| `needs_approval` | booleano | Control antes de comunicar una decision. |

Una solicitud con campos ausentes o tipos invalidos responde `400` con un error legible. Un fallo interno no controlado responde `500`.

## `POST /consulta`

### Entrada

```json
{
  "estudiante": "Ana Perez",
  "materias_aprobadas": ["MAT101", "PRO101"]
}
```

- `estudiante`: texto entre 2 y 100 caracteres.
- `materias_aprobadas`: lista opcional de codigos alfanumericos.

### Salida

La respuesta incluye `materias_disponibles`, `materias_bloqueadas` con sus requisitos faltantes y `solicitud`. La solicitud siempre tiene estado `borrador_no_enviado`.

## Limites

El servicio consulta el catalogo local. El endpoint mock no usa API keys ni llama modelos externos. No autentica estudiantes, no persiste datos personales, no registra inscripciones y no envia correos al coordinador.