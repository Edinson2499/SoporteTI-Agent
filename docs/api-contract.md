# API Contract

Este es el contrato de la API de SoporteTI-Agent solicitado para la entrega de la base técnica v0.1.

## `GET /health`

- Entrada: ninguna.
- Salida: `{"status":"ok"}`.
- Estado exitoso: `200`.

## `POST /agent/ask`

### Entrada JSON

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

- `question`: texto obligatorio de la incidencia.
- `user_id`: texto obligatorio para identificar el caso.
- `context`: objeto opcional con datos del equipo.

### Salida JSON `200`

```json
{
  "answer": "Para portatil: sigue los pasos seguros de la base de conocimiento.",
  "sources": ["kb_internet_001"],
  "needs_approval": false,
  "next_action": "seguir_pasos_seguros"
}
```

- `answer`: recomendacion o resultado del agente.
- `sources`: fuentes usadas para la respuesta.
- `needs_approval`: indica si requiere revision humana.
- `next_action`: siguiente accion explicita.

### Estados

- `200`: solicitud procesada, incluso cuando se prepara una escalacion.
- `400`: JSON invalido o falta un campo obligatorio.
- `500`: fallo interno no controlado.

La API no ejecuta comandos, instala software, cambia contrasenas ni envia tickets automaticamente.