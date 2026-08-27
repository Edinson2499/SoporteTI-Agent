import json
import re


def build_response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(payload, ensure_ascii=False),
    }


# Cada articulo: (palabras_clave, respuesta, fuente). Se evalua en orden; las categorias mas
# especificas van primero para que no sean opacadas por palabras genericas como "conexion".
BASE_CONOCIMIENTO = [
    (
        ("vpn", "acceso remoto", "conexion remota"),
        "Confirma usuario y contraseña de la VPN, revisa que el cliente este actualizado y "
        "que no haya otra sesion activa desde otro dispositivo.",
        "guia-soporte-vpn-v0.1",
    ),
    (
        ("contrasena", "contraseña", "password", "clave", "bloqueada", "olvide"),
        "Usa la opcion 'Olvide mi contraseña' en el portal institucional. Si no llega el correo "
        "de recuperacion, solicita el restablecimiento manual al soporte.",
        "guia-soporte-contrasena-v0.1",
    ),
    (
        ("correo", "email", "outlook", "gmail", "bandeja"),
        "Verifica tu conexion a internet, confirma que el servicio de correo no este caido y "
        "revisa la carpeta de spam. Si no puedes iniciar sesion, reporta el error exacto.",
        "guia-soporte-correo-v0.1",
    ),
    (
        ("impresora", "imprime", "impresion", "imprimir"),
        "Confirma que la impresora este encendida, con papel y sin trabajos atascados en cola. "
        "Reinstala el driver si el error persiste.",
        "guia-soporte-impresora-v0.1",
    ),
    (
        ("pantalla azul", "bsod", "pantallazo azul", "error azul"),
        "Anota el codigo de error mostrado, reinicia el equipo y evita instalar nuevo hardware o "
        "drivers hasta que el soporte revise el caso.",
        "guia-soporte-pantallazo-azul-v0.1",
    ),
    (
        ("audio", "sonido", "microfono", "bocina", "altavoz"),
        "Revisa el volumen y el dispositivo de salida/entrada seleccionado en la configuracion de "
        "sonido, y confirma que los cables o el bluetooth esten conectados.",
        "guia-soporte-audio-v0.1",
    ),
    (
        ("teclado", "mouse", "raton", "periferico"),
        "Prueba el periferico en otro puerto USB o con otro cable, reinicia el equipo y revisa "
        "que las baterias no esten agotadas si es inalambrico.",
        "guia-soporte-perifericos-v0.1",
    ),
    (
        ("actualizacion", "actualizar", "update", "parche"),
        "Guarda tu trabajo antes de actualizar, conecta el equipo a la corriente y no lo apagues "
        "durante el proceso. Reporta cualquier codigo de error al soporte.",
        "guia-soporte-actualizaciones-v0.1",
    ),
    (
        ("virus", "antivirus", "malware", "sospechoso"),
        "Desconecta el equipo de la red, no ingreses contraseñas ni abras archivos adicionales, y "
        "reporta el caso de inmediato al soporte para un analisis de seguridad.",
        "guia-soporte-seguridad-v0.1",
    ),
    (
        ("instalar", "instalacion", "programa", "software", "aplicacion"),
        "Verifica que tengas permisos de instalacion; si no los tienes, solicita la instalacion "
        "al soporte indicando el nombre exacto del programa y su version.",
        "guia-soporte-software-v0.1",
    ),
    (
        ("lento", "lenta", "rendimiento", "bloqueado", "congelado", "colgado"),
        "Cierra aplicaciones sin uso, revisa espacio en disco y reinicia el equipo si lleva "
        "mucho tiempo encendido. Si sigue lento, reporta modelo y sistema operativo al soporte.",
        "guia-soporte-rendimiento-v0.1",
    ),
    (
        ("internet", "wifi", "red", "conexion"),
        "Verifica que el WiFi este activo, reinicia el adaptador de red y prueba con otro "
        "dispositivo. Si el problema continua, reinicia el router y escala al soporte.",
        "guia-soporte-internet-v0.1",
    ),
]


def clasificar_pregunta(question):
    """Devuelve (answer, source, next_action) buscando coincidencias por palabra completa."""
    texto = question.lower()
    for palabras_clave, answer, source in BASE_CONOCIMIENTO:
        if any(re.search(rf"\b{re.escape(palabra)}\b", texto) for palabra in palabras_clave):
            return answer, source, "responder"
    return (
        "No encontre una respuesta autorizada para esa pregunta; un agente de soporte IT la "
        "revisara y te contactara.",
        "fallback-no-encontrado",
        "escalar_a_humano",
    )


def lambda_handler(event, context):
    print("Request ID:", context.aws_request_id)

    payload = event
    # Permite probar desde la consola o desde una Function URL.
    if isinstance(event, dict) and "body" in event:
        payload = event["body"]
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                return build_response(400, {"status": "error", "message": "JSON invalido."})

    required = ["request_id", "user_id", "question", "channel"]
    missing = [field for field in required if not isinstance(payload, dict) or not payload.get(field)]
    if missing:
        return build_response(400, {"status": "error", "missing_fields": missing})

    answer, source, next_action = clasificar_pregunta(payload["question"])

    return build_response(
        200,
        {
            "status": "ok",
            "request_id": payload["request_id"],
            "answer": answer,
            "source": source,
            "next_action": next_action,
        },
    )
