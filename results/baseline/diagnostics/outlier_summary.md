# Diagnóstico de outliers — P_RM_R1 y F1_PIN_R1

Este es un chequeo puntual, no una variante nueva de PCA. Objetivo: entender por qué
estas dos muestras aparecen tan lejos del resto en `results/baseline/pca_pc1_pc2.png`,
y si se parece al problema de escala que encontramos en F1_PIN_R2.

## Lo que se hizo

- Para cada muestra, se comparó proteína por proteína contra el promedio de sus otras
  2 réplicas → `outlier_P_RM_R1.csv`, `outlier_F1_PIN_R1.csv`.
- Se comparó cada valor sospechoso contra el percentil 99 de toda la matriz
  (**1.82**), como el que usamos para detectar el problema de F1_PIN_R2.
- Se sacaron las 15 proteínas con más peso ("loading") en PC1 y en PC2 del PCA
  baseline → `loadings_top15_pc1.csv`, `loadings_top15_pc2.csv`.

## Conclusión corta: **no parece el mismo problema de F1_PIN_R2**

El problema de F1_PIN_R2 era un puñado de valores absurdamente altos (hasta 1533,
cuando el resto de la matriz no pasa de ~15-47) — un error de escala evidente. Acá no
aparece nada así:

- El valor más alto de P_RM_R1 es 7.89 y el de F1_PIN_R1 es 3.2. Están por encima del
  percentil 99 (1.82) en algunas proteínas puntuales, pero dentro del rango de valores
  normales de la matriz (el máximo global es 47.4, en otra muestra). No hay ningún
  valor "imposible".
- Las 15 proteínas con mayor diferencia contra sus réplicas **no coinciden** con las
  15 proteínas de mayor peso en PC1 o PC2 (columnas `in_top15_...` en las 4 tablas,
  todas en `False`). O sea, no hay un puñado de proteínas puntuales arrastrando el
  resultado.

## Entonces, ¿por qué se disparan tanto?

Mirando los loadings de PC1 y PC2, llama la atención que son muchos valores parecidos
entre sí (~0.054 en PC1, ~0.077-0.08 en PC2) en vez de unos pocos valores mucho más
grandes que el resto. Esto sugiere que no son "unas pocas proteínas culpables", sino
muchas proteínas empujando un poco cada una, todas en la misma dirección.

Revisando por qué: esta matriz es muy dispersa (en promedio, cada proteína se detecta
en solo 4 de las 27 muestras). Encontramos que:

- **234 de las 975 proteínas** (24%) se detectan **únicamente** en `P_RM_R1` y en
  ninguna otra de las 27 muestras.
- `P_RM_R1` es la muestra con el valor más alto en **284 proteínas**, y `F1_PIN_R1` en
  **132 proteínas** — muchas más que el promedio esperable si todas las muestras
  fueran parecidas.

Cuando una proteína se detecta casi solo en una muestra, al estandarizar (z-score) esa
muestra queda con un valor extremo para esa proteína, aunque el número crudo sea
chico. Con cientos de proteínas así, los efectos se suman y arrastran a la muestra
lejos del resto en el PCA — sin que exista ningún valor erróneo de por sí.

## Lectura en simple

No parece un error de carga de datos como F1_PIN_R2. Parece más bien un efecto de
que la matriz tiene muchos ceros y estas dos muestras concentran una cantidad inusual
de proteínas "raras" (detectadas casi solo ahí). Esto es justamente lo que la Etapa 2
del plan (tratamiento de ceros / filtrado de proteínas poco detectadas) está pensada
para explorar — conviene tenerlo presente al decidir esa variante, porque probablemente
cambie bastante la posición de estas dos muestras en el PCA.
