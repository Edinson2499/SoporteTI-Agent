// Port de SoporteTI-Agent (Python/FastAPI) a Node.js para esta Lambda.

const BASE_CONOCIMIENTO = [
  {
    id: 'kb_internet_001',
    palabras_clave: ['internet', 'wifi', 'red', 'conexion'],
    pasos: [
      'Verifica si otro dispositivo puede conectarse a la misma red.',
      'Confirma que el modo avion este desactivado y que WiFi este activo.',
      'Reinicia el adaptador de red desde la configuracion del sistema.',
      'Si el problema continua, informa el resultado al equipo de soporte.',
    ],
  },
  {
    id: 'kb_rendimiento_001',
    palabras_clave: ['lento', 'lenta', 'rendimiento', 'bloqueado'],
    pasos: [
      'Cierra aplicaciones que no estes utilizando.',
      'Reinicia el equipo si lleva mucho tiempo encendido.',
      'Revisa que haya espacio libre disponible en el disco.',
      'Si persiste, informa al soporte sin instalar programas ni cambiar configuraciones criticas.',
    ],
  },
  {
    id: 'kb_impresora_001',
    palabras_clave: ['impresora', 'imprime', 'impresion'],
    pasos: [
      'Verifica que la impresora este encendida y conectada.',
      'Comprueba que tenga papel y no muestre un mensaje fisico de error.',
      'Cancela solo los trabajos propios que permanezcan en cola.',
      'Si el error continua, informa el nombre de la impresora al soporte.',
    ],
  },
];

function buscarConocimiento(problema) {
  const texto = problema.toLowerCase();
  return BASE_CONOCIMIENTO.find((articulo) =>
    articulo.palabras_clave.some((palabra) => texto.includes(palabra))
  );
}

function crearBorradorTicket(problema, usuario) {
  return {
    estado: 'borrador_pendiente_aprobacion',
    titulo: `Revision de soporte para ${usuario}`,
    descripcion: problema,
  };
}

function responderAgente(question, userId, context) {
  const articulo = buscarConocimiento(question);
  const dispositivo = (context && context.device) || 'el equipo';

  if (!articulo) {
    const borrador = crearBorradorTicket(question, userId);
    return {
      answer:
        `No encontre una guia segura para ${dispositivo}. Se preparo un borrador para ` +
        'revision humana; no se enviara ni se ejecutara ningun cambio automaticamente.',
      sources: ['protocolo_escalamiento'],
      needs_approval: true,
      next_action: borrador.estado,
    };
  }

  const pasos = articulo.pasos.map((paso, indice) => `${indice + 1}. ${paso}`).join(' ');
  return {
    answer: `Para ${dispositivo}: ${pasos}`,
    sources: [articulo.id],
    needs_approval: false,
    next_action: 'seguir_pasos_seguros',
  };
}

function response(statusCode, body) {
  return {
    statusCode,
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  };
}

function parseRequestBody(event) {
  let rawBody = event.body || '{}';
  if (event.isBase64Encoded) {
    rawBody = Buffer.from(rawBody, 'base64').toString('utf-8');
  }
  const body = typeof rawBody === 'string' ? JSON.parse(rawBody) : rawBody;
  if (typeof body !== 'object' || body === null || Array.isArray(body)) {
    throw new Error('El cuerpo debe ser un objeto JSON.');
  }
  return body;
}

function validateAskRequest(body) {
  const errors = [];
  const { question, user_id: userId, context } = body;

  if (typeof question !== 'string' || question.length < 5 || question.length > 500) {
    errors.push({ field: 'question', message: 'Debe tener entre 5 y 500 caracteres.' });
  }
  if (typeof userId !== 'string' || userId.length < 3 || userId.length > 50) {
    errors.push({ field: 'user_id', message: 'Debe tener entre 3 y 50 caracteres.' });
  }
  if (context !== undefined && context !== null && typeof context !== 'object') {
    errors.push({ field: 'context', message: 'Debe ser un objeto.' });
  }
  if (errors.length > 0) {
    throw { errors };
  }
  return { question, userId, context: context || null };
}

export const handler = async (event) => {
  const requestContext = event.requestContext || {};
  const http = requestContext.http || {};
  const method = (http.method || event.httpMethod || '').toUpperCase();
  const path = event.rawPath || event.path || '/';

  if (method === 'GET' && path === '/health') {
    return response(200, { status: 'ok' });
  }
  if (method !== 'POST' || path !== '/agent/ask') {
    return response(404, { detail: 'Ruta no encontrada.' });
  }

  let request;
  try {
    const body = parseRequestBody(event);
    request = validateAskRequest(body);
  } catch (exc) {
    return response(400, {
      detail: 'Solicitud invalida.',
      errors: exc && exc.errors ? exc.errors : [],
    });
  }

  const result = responderAgente(request.question, request.userId, request.context);
  return response(200, result);
};
