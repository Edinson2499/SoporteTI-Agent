# Arquitectura — SoporteTI-Agent v0.1

## Diagrama general

```
                    ┌─────────────────┐
                    │     USUARIO     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   WEB / API     │
                    │  (FastAPI HTTP) │
                    └────────┬────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │    AGENTE SoporteTI  │
                 │                      │
                 │  Objetivo            │
                 │  Contexto            │
                 │  Decision            │
                 │  Limites             │
                 └───────┬───────┬──────┘
                         │       │
              ┌──────────┘       └───────────┐
              ▼                              ▼
     ┌─────────────────┐            ┌─────────────────┐
     │   MODELO IA     │            │  BASE DE        │
     │  (OpenAI API)   │            │  CONOCIMIENTO   │
     └─────────────────┘            │  (JSON local)   │
                                    └────────┬────────┘
                                             │
                                             ▼
                                   ┌─────────────────┐
                                   │  RESULTADO /    │
                                   │  RECOMENDACION  │
                                   └─────────────────┘
```

## Tabla capacidad-servicio

| Componente          | Funcion                                          | Tecnologia        |
|---------------------|--------------------------------------------------|-------------------|
| Interfaz HTTP       | Recibe solicitudes del usuario                   | FastAPI           |
| Agente              | Ciclo objetivo → contexto → decision → herramienta → resultado → limite | Python |
| Modelo IA           | Comprende el lenguaje natural                    | OpenAI gpt-4o-mini|
| Base de conocimiento| Contiene soluciones estructuradas                | JSON local        |
| Herramienta 1       | buscar_conocimiento — busca en JSON              | Python            |
| Herramienta 2       | consultar_diagnostico — aplica reglas            | Python            |
| Herramienta 3       | crear_ticket — crea borrador de ticket           | Python (memoria)  |
| Estado              | Historial de conversacion por sesion             | dict en memoria   |
| Logs                | Salida estandar (extensible a cloud)             | Python logging    |

## Limites del agente

### El agente SI puede
- Consultar la base de conocimiento.
- Hacer preguntas al usuario.
- Analizar el problema.
- Recomendar pasos de solucion.
- Crear un borrador de ticket.

### El agente NO puede
- Eliminar archivos.
- Ejecutar comandos administrativos.
- Cambiar contraseñas directamente.
- Modificar configuraciones criticas.
- Instalar software de forma automatica.
- Cerrar o borrar tickets sin aprobacion humana.

## Flujo de decision

```
USUARIO
  │ "Mi computador esta muy lento"
  ▼
AGENTE
  │ buscar_conocimiento("lento") → rendimiento.json
  │ consultar_diagnostico("lento") → pasos de diagnostico
  ▼
MODELO IA
  │ Analiza contexto + conocimiento
  ▼
AGENTE
  │ "¿Cuanto espacio libre tienes en C:?"
  ▼
USUARIO
  │ "Solo 3 GB"
  ▼
AGENTE
  │ RECOMENDACION:
  │   1. Liberar espacio con el limpiador de disco
  │   2. Deshabilitar programas de inicio
  │   3. Reiniciar el equipo
  ▼
USUARIO
```

## Riesgos y controles

| Riesgo                             | Control                                       |
|------------------------------------|-----------------------------------------------|
| Accion peligrosa solicitada        | Lista de acciones prohibidas verificada antes de llamar al modelo |
| Sesion sin fin                     | Limite de iteraciones por sesion (max_iteraciones) |
| Ticket modificado sin autorizacion | El campo aprobado=False; no hay endpoint de cierre automatico |
| Clave API expuesta                 | Variable de entorno; .env en .gitignore       |

## Evolucion planificada

| Fase | Descripcion                                      |
|------|--------------------------------------------------|
| v0.1 | Prototipo local: API + Agente + Knowledge base   |
| v0.2 | Persistencia de tickets en base de datos         |
| v0.3 | Memoria de conversaciones entre sesiones         |
| v0.4 | Despliegue en cloud (AWS / Azure / GCP)          |
| v0.5 | Autenticacion de usuarios y logs persistentes    |
