# SLA (Acuerdos de Nivel de Servicio)

El SLA se mide en dos tiempos: tiempo a primera respuesta (`First Response
Time` menos la fecha de creación del ticket) y tiempo a resolución
(`Time to Resolution` menos la fecha de creación).

| Prioridad | Primera respuesta | Resolución objetivo |
|---|---|---|
| Critical | 30 minutos | 4 horas |
| High | 2 horas | 24 horas |
| Medium | 8 horas | 3 días hábiles |
| Low | 24 horas | 7 días hábiles |

## Incumplimiento de SLA
Si un ticket `Open` o `Pending Customer Response` supera el tiempo de
resolución objetivo de su prioridad sin haberse cerrado, se considera en
**incumplimiento de SLA** y debe escalarse automáticamente al supervisor del
equipo asignado.

## Satisfacción del cliente
La calificación de satisfacción (`Customer Satisfaction Rating`, escala 1-5)
solo existe para tickets `Closed`. Una calificación de 1 o 2 en un ticket de
prioridad Critical o High dispara una revisión de calidad obligatoria del
caso por parte del equipo correspondiente.
