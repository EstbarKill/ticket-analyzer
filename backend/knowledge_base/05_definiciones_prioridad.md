# Definiciones de Prioridad

## Critical
El cliente no puede usar el producto en absoluto, hay pérdida de datos, un
riesgo de seguridad, o impacto económico directo y significativo. Requiere
atención inmediata.

## High
El cliente puede usar el producto pero con una limitación importante que
afecta su operación diaria (por ejemplo, una función clave no funciona). No
hay pérdida de datos ni riesgo de seguridad.

## Medium
El cliente tiene un problema real pero existe una forma de continuar usando
el producto (un workaround), o el impacto es moderado y no urgente.

## Low
Preguntas generales, dudas sobre el producto, solicitudes de información o
problemas cosméticos sin impacto funcional.

## Nota sobre prioridad reportada vs. prioridad sugerida por IA
La prioridad que llega en el campo `Ticket Priority` del sistema de origen es
la prioridad *reportada* en el momento de creación del ticket, y puede estar
desactualizada o mal asignada por el cliente o el agente. La prioridad
*sugerida* por el análisis de IA (`ai_priority`) se calcula a partir del
contenido real del ticket y puede diferir de la original; en caso de
conflicto, se debe confiar más en la sugerida por IA para la cola de trabajo
diaria, pero sin sobreescribir el dato original (se conservan ambas).
