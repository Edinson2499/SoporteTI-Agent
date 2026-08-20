# SoporteTI-Agent

Agente de IA para soporte tecnico de computadores. El usuario describe su problema y el agente analiza el contexto, consulta una base de conocimiento local, hace preguntas de diagnostico y recomienda pasos para solucionarlo. Si no puede resolver el problema, crea un ticket de soporte para revision humana.

## Estructura del proyecto

```
soporteti-agent/
├── app/
│   ├── main.py       # API HTTP (FastAPI)
│   ├── agent.py      # Ciclo de decision del agente
│   └── tools.py      # Herramientas: buscar_conocimiento, consultar_diagnostico, crear_ticket
├── knowledge/
│   ├── internet.json
│   ├── windows.json
│   ├── impresoras.json
│   ├── rendimiento.json
│   └── cuentas.json
├── tests/
│   └── test_agent.py
├── architecture/
│   └── architecture.md
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Instalacion rapida

```bash
# 1. Clonar el repositorio
git clone https://github.com/Edinson2499/SoporteTI-Agent.git
cd SoporteTI-Agent

# 2. Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configurar la clave de OpenAI
cp .env.example .env
# Editar .env y completar OPENAI_API_KEY

# 4. Iniciar el servidor
uvicorn app.main:app --reload
```

El servidor queda disponible en `http://localhost:8000`. La documentacion interactiva esta en `http://localhost:8000/docs`.

## Uso de la API

### Iniciar una sesion
```http
POST /iniciar
Content-Type: application/json

{
  "session_id": "sesion-001",
  "problema": "Mi computador esta muy lento",
  "usuario": "juan"
}
```

### Continuar la conversacion
```http
POST /responder
Content-Type: application/json

{
  "session_id": "sesion-001",
  "mensaje": "Solo tengo 3 GB libres en el disco"
}
```

### Escalar el caso (crear ticket)
```http
POST /escalar
Content-Type: application/json

{
  "session_id": "sesion-001",
  "descripcion_adicional": "El problema persiste despues de reiniciar"
}
```

### Consultar un ticket
```http
GET /ticket/{ticket_id}
```

## Ejecutar pruebas

```bash
pytest tests/ -v
```

## Arquitectura

Ver [architecture/architecture.md](architecture/architecture.md) para el diagrama completo, tabla de componentes, limites del agente y plan de evolucion.

## Limites del agente

El agente **SI puede**: consultar conocimiento, hacer preguntas, analizar problemas, recomendar soluciones, crear borradores de tickets.

El agente **NO puede**: eliminar archivos, ejecutar comandos administrativos, cambiar contraseñas, instalar software, cerrar tickets sin aprobacion humana.
