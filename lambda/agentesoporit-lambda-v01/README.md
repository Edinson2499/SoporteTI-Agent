# agentesoporit-lambda-v01

Codigo desplegado en la funcion AWS Lambda `agentesoporit-lambda-v01` (region `us-east-2`).

- `lambda_function.py`: version activa (runtime `python3.13`, handler `lambda_function.lambda_handler`).
  Valida `request_id`, `user_id`, `question`, `channel` y responde con `status`, `request_id`, `answer`,
  `source`, `next_action`, clasificando la pregunta por palabras clave (internet, rendimiento, impresora)
  o escalando a humano si no reconoce el tema.
- `index.mjs`: version previa en Node.js (no desplegada actualmente), se conserva como referencia.
