---
name: control-antes-de-entregar
description: Control de calidad final antes de mostrar resultados a otra persona. Usar antes de la reunión con la directora, antes de compartir un gráfico o una tabla, antes de mandar un resumen, o cuando se pide "revisá esto antes de que lo mande", "¿está listo?", "¿me olvido de algo?". Es la última puerta antes de que un resultado salga del proyecto.
---

## Cuándo usarla

- Antes de la reunión con la directora (Etapa 5).
- Antes de compartir cualquier gráfico, tabla o resumen fuera del proyecto.
- Cuando hay dudas de si un resultado está listo para mostrarse.

## Proceso

Recorrer las cinco secciones. Cada punto se responde con **sí / no / no aplica**, y todo
"no" se resuelve o se declara explícitamente como limitación antes de entregar.

### 1. El dato de base

- [ ] ¿Se corrió `scripts/check_matrix.py` sobre la versión de la matriz que se usó?
- [ ] ¿Todos los avisos del chequeo están clasificados y registrados?
- [ ] ¿Hay avisos sin resolver? Si sí, ¿están dichos en el entregable?
- [ ] ¿La matriz usada es la misma para todas las variantes que se comparan? (Si una
      variante se corrió antes de la corrección de `F1_PIN_R2` y otra después, no son
      comparables.)

### 2. La reproducibilidad

- [ ] ¿Cada resultado mostrado tiene su carpeta en `results/<variante>/`?
- [ ] ¿Se puede volver a generar cada gráfico con un comando concreto?
- [ ] ¿Están guardadas las tablas de varianza explicada y de scores?
- [ ] ¿Hay entrada en `docs/analysis_notes.md` para cada corrida que se menciona?

### 3. Los números

- [ ] ¿Los porcentajes y coordenadas del texto coinciden con las tablas en `results/`?
- [ ] ¿Los ejes de los gráficos dicen el % de varianza explicada de esa corrida (y no de
      otra)?
- [ ] ¿Los totales cierran? (Ej.: proteínas filtradas + proteínas usadas = 975.)
- [ ] ¿Cada afirmación numérica se puede señalar en un archivo concreto?

### 4. La interpretación

- [ ] ¿Cada hallazgo tiene su nivel de confianza (confirmado / probable / especulación)?
- [ ] ¿Se dice explícitamente qué NO se puede afirmar todavía?
- [ ] ¿Se mencionan las decisiones que condicionan la lectura? (corrección manual de
      `F1_PIN_R2`, réplicas idénticas, matriz normalizada a total fijo)
- [ ] ¿Hay alguna frase que suene a conclusión definitiva? En este proyecto todo es
      exploratorio hasta la revisión con la directora.
- [ ] ¿Se distinguen las causas técnicas de las biológicas, o están mezcladas?

### 5. La comunicación

- [ ] ¿Alguien que no siguió el análisis entiende el entregable solo?
- [ ] ¿Hay jerga estadística que se pueda decir más simple sin perder precisión?
- [ ] ¿Las preguntas para la directora están formuladas de forma concreta y
      respondible?
- [ ] ¿El entregable dice qué se necesita de ella: una decisión, información del
      laboratorio, o solo revisión?

## Qué necesito de vos

- Qué se va a entregar y a quién.
- Si hay una fecha o una reunión concreta (cambia cuánto conviene profundizar).

## Qué produce

- Checklist recorrido con el estado de cada punto.
- Lista de cosas a arreglar antes de entregar, ordenada por gravedad.
- Lista de limitaciones que hay que declarar explícitamente en el entregable.
- Un veredicto claro: listo para entregar, o no y por qué.

## Ojo con

- **No usar el checklist como trámite.** Un "sí" apurado en "los números coinciden" es
  peor que no haber chequeado, porque genera confianza falsa.
- **Encontrar un problema acá es el éxito de la skill**, no un fracaso del análisis.
