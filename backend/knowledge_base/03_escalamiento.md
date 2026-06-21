# Reglas de Escalamiento

## Escalamiento por prioridad
- **Critical**: se notifica de inmediato al supervisor del equipo asignado,
  sin importar el horario (incluye fuera de horario laboral y fines de
  semana). Debe tener una primera respuesta humana en menos de 30 minutos.
- **High**: se notifica al líder de equipo si no hay primera respuesta dentro
  de las 2 horas hábiles.
- **Medium / Low**: siguen el flujo normal de la cola del equipo asignado, sin
  notificación especial.

## Escalamiento por reincidencia
Si un mismo cliente (mismo `Customer Email`) abre 3 o más tickets sobre el
mismo `Product Purchased` en un período de 30 días, el caso se escala a
Soporte Técnico Nivel 2 para una revisión más profunda, independientemente de
la prioridad individual de cada ticket.

## Escalamiento por sentimiento negativo
Un ticket con sentimiento negativo marcado y prioridad High o Critical debe
ser revisado por un agente senior antes de cerrarse, no solo por el agente
que lo atendió originalmente.
