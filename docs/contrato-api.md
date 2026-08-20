# Contrato de la API

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

El servicio consulta el catalogo local. No autentica estudiantes, no persiste datos personales, no registra inscripciones y no envia correos al coordinador.