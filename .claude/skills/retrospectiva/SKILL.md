---
name: retrospectiva
description: Cerrar una etapa del plan sacando conclusiones sobre cómo se trabajó, no sobre los datos. Usar al terminar una etapa de PLAN_ETAPAS.md, después de la reunión con la directora, cuando se pide "cerremos esta etapa", "qué aprendimos", "qué haríamos distinto", o cuando el análisis se estancó y conviene parar a mirar el proceso.
---

## Cuándo usarla

- Al terminar una etapa de `docs/PLAN_ETAPAS.md`.
- Después de la reunión con la directora, para ordenar lo que salió de ahí.
- Cuando el análisis se estancó y conviene revisar el proceso antes de seguir probando.

Esta skill mira **cómo se trabajó**, no qué dicen los datos. Para eso está
**sintesis-hallazgos**.

## Proceso

1. **Reconstruir qué se hizo en la etapa**, a partir de `docs/analysis_notes.md` y las
   carpetas de `results/`. Sin interpretar todavía: solo la lista.

2. **Separar en tres columnas, con ejemplos concretos de esta etapa:**
   - **Funcionó** — qué conviene repetir en la etapa siguiente.
   - **Costó más de lo necesario** — dónde se perdió tiempo y por qué.
   - **Se aprendió** — qué se sabe ahora que no se sabía al empezar.

3. **Para cada punto de "costó más de lo necesario", buscar la causa del proceso, no de
   la persona.** Ejemplo real de la Etapa 1: los problemas del dato aparecieron de a uno
   después de correr el PCA. La causa no fue distracción: era que no existía un chequeo
   previo. La solución fue `scripts/check_matrix.py`, no "prestar más atención".

4. **Convertir cada aprendizaje en algo concreto**, o descartarlo. Un aprendizaje que no
   cambia nada se olvida en una semana. Las formas válidas de concretarlo:
   - Una regla nueva en `CLAUDE.md`.
   - Una decisión registrada en `docs/design_decisions.md`.
   - Un script o una skill que automatice el chequeo.
   - Un ajuste en el plan de etapas siguientes.

5. **Revisar si el plan sigue teniendo sentido.** Comparar `PLAN_ETAPAS.md` con lo que se
   sabe ahora. Si una etapa quedó sin sentido, o hace falta una que no estaba, proponerlo
   con el motivo. El plan está hecho para ajustarse.

6. **Actualizar el estado en `CLAUDE.md`** (la lista de etapas con checkboxes) y dejar una
   entrada corta en `docs/analysis_notes.md`.

7. **Anotar qué NO hacer.** Las variantes descartadas y los caminos cerrados son
   información: evitan repetir el intento. Nunca borrar una variante descartada, alcanza
   con anotar por qué no se siguió por ahí.

## Qué necesito de vos

- Qué etapa se está cerrando.
- Si hubo algo que te frustró o te trabó, aunque parezca menor: suele ser la señal más
  útil.
- Si hubo reunión con la directora, qué salió de ahí.

## Qué produce

- Las tres columnas (funcionó / costó / se aprendió) con ejemplos concretos.
- Cada aprendizaje convertido en una acción concreta, o descartado explícitamente.
- Cambios propuestos a `CLAUDE.md`, `PLAN_ETAPAS.md` o `design_decisions.md`.
- Estado de las etapas actualizado.
- Lista de caminos cerrados, para no volver a intentarlos.

## Ojo con

- **Que no se vuelva un trámite.** Si no sale ningún cambio concreto, la retrospectiva no
  sirvió: o faltó honestidad, o la etapa fue realmente limpia (posible, pero raro).
- **No buscar culpables.** Casi todo lo que "costó más de lo necesario" es un hueco del
  proceso, no un descuido.
- **No inflar la lista de aprendizajes.** Dos aprendizajes concretos valen más que ocho
  genéricos.
