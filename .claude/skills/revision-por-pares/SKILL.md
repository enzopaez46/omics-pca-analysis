---
name: revision-por-pares
description: Revisión crítica de una variante, un script o una interpretación, buscando errores antes de que los encuentre otro. Usar cuando se pide "revisá esta variante", "¿está bien este script?", "¿esta interpretación se sostiene?", "buscá qué puede estar mal", o antes de comprometerse con una decisión importante del análisis.
---

## Cuándo usarla

- Después de implementar una variante nueva y antes de interpretarla.
- Antes de comprometerse con una decisión importante (por ejemplo, elegir un umbral de
  filtrado definitivo).
- Cuando un resultado es *demasiado* limpio o confirma demasiado bien lo que se esperaba.

El objetivo es encontrar el problema acá, no en la reunión con la directora.

## Proceso

Revisar en estos cuatro planos, en orden. Los errores del plano 1 invalidan todo lo demás,
así que no tiene sentido revisar la interpretación de un script que lee mal los datos.

### 1. ¿El código hace lo que dice hacer?

- ¿Se transpone la matriz en el momento correcto? (El filtrado por proteína se hace con
  proteínas en filas; el PCA con muestras en filas. Confundirlo filtra muestras en vez de
  proteínas y no da error.)
- ¿El filtrado cuenta ceros por el eje correcto?
- ¿Se estandariza por proteína (columna después de transponer) y no por muestra?
- ¿El script lee `data/master_matrix.csv` sin modificarlo?
- ¿Correrlo dos veces da el mismo resultado?
- ¿Los valores por defecto reproducen exactamente el baseline? (Regla del proyecto: una
  variante nueva no debe cambiar los resultados de las anteriores.)

### 2. ¿Los resultados son coherentes entre sí?

- ¿Los % de varianza explicada suman ~100 en la tabla completa?
- ¿La cantidad de proteínas usadas coincide con lo que implica el umbral?
- ¿Los scores tienen 27 filas, una por muestra?
- ¿Los ejes del gráfico muestran los % de *esta* corrida?
- ¿Los números del texto coinciden con los CSV de `results/`?

### 3. ¿La interpretación se sostiene?

- ¿Cada afirmación se puede señalar en una tabla o gráfico concreto?
- ¿Hay una explicación alternativa que no se consideró?
- ¿Se está atribuyendo a biología algo que puede ser del preprocesamiento?
- ¿El patrón afirmado se sostiene al desagregar, o solo en el agregado?
- ¿La causa propuesta explica la magnitud completa del efecto o solo una parte?

### 4. ¿Está registrado como corresponde?

- ¿La variante tiene su carpeta propia en `results/<nombre>/`?
- ¿Está documentada la diferencia respecto de la variante anterior (1-2 líneas)?
- ¿Hay entrada en `docs/analysis_notes.md`?
- ¿Las decisiones no triviales están en `docs/design_decisions.md` con su implicancia?
- ¿Se creó algún script suelto tipo `pca_v2_final.py`? (Va contra la regla 2 de
  `CLAUDE.md`.)

## Qué necesito de vos

- Qué revisar: una variante, un script, una interpretación, o todo.
- Si hay algo que te dejó dudando, decilo — se revisa igual todo, pero se empieza por ahí.

## Qué produce

- Lista de problemas encontrados, separados en: **rompe el resultado** / **hay que
  arreglarlo pero no invalida** / **sugerencia**.
- Para cada problema: dónde está (archivo y línea) y qué habría que cambiar.
- Lista de cosas que se revisaron y están bien (para no re-revisarlas después).
- Si no se encuentra nada: decirlo así, sin inventar observaciones de relleno.

## Ojo con

- **No confundir "distinto de como yo lo haría" con "está mal".** Solo se reportan cosas
  que cambian el resultado o que lo hacen frágil.
- **Los errores silenciosos son los peligrosos.** Un eje mal elegido en pandas no tira
  excepción: devuelve un número plausible y equivocado.
- **Un resultado sospechosamente limpio merece más revisión, no menos.**
