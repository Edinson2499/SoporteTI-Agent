"""Integracion futura con Amazon Bedrock (RF08, seccion AMAZON BEDROCK).

Aun no esta conectada al flujo del agente: `agent.diagnosticar` sigue usando la
base de conocimiento local de forma determinista. Cuando se habilite Bedrock,
esta funcion debera recibir la pregunta, el contexto y el articulo encontrado
(o None) y devolver una respuesta en lenguaje natural respetando las reglas de
seguridad del agente (no inventar procedimientos, pedir contexto si falta
informacion, escalar cuando corresponda).
"""


def generar_respuesta_ia(question, contexto, articulo):
    raise NotImplementedError("Integracion con Amazon Bedrock pendiente.")
