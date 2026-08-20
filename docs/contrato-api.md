# Contrato de la API

## `GET /health`

No recibe cuerpo y responde `200`:

```json
{"status": "ok"}
```

## `POST /agent/ask`

Recibe una incidencia de soporte TI, valida el contrato, consulta conocimiento local y responde pasos seguros o una escalacion pendiente de aprobacion.

### Entrada

```json
{
  "question": "No tengo internet en mi portatil",
  "user_id": "USR-1042",
  "context": {
    "device": "portatil",
    "operating_system": "Windows 11"
  }
}
```

| Campo | Tipo | Obligatorio | Uso |
| --- | --- | --- | --- |
| `question` | texto | Si | Problema de soporte, entre 5 y 500 caracteres. |
| `user_id` | texto | Si | Identificador del usuario para la escalacion. |
| `context` | objeto | No | Datos como dispositivo o sistema operativo. |

### Respuesta de caso conocido `200`

```json
{
  "answer": "Para portatil: 1. Verifica la red. 2. Confirma WiFi activo.",
  "sources": ["kb_internet_001"],
  "needs_approval": false,
  "next_action": "seguir_pasos_seguros"
}
```

### Respuesta de caso sin guia `200`

La API crea solo un borrador local y devuelve `needs_approval: true` con `next_action: "borrador_pendiente_aprobacion"`.

### Errores

| Estado | Significado |
| --- | --- |
| `400` | JSON invalido, campo obligatorio ausente o tipo incorrecto. |
| `500` | Fallo interno no controlado. |

## Limites

El agente no ejecuta comandos administrativos, no instala software, no cambia contrasenas, no modifica configuraciones criticas, no elimina archivos y no envia tickets automaticamente. La respuesta es una recomendacion segura; los cambios requieren intervencion o aprobacion humana.