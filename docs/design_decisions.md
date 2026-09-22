# Decisiones de diseño acordadas

Registro de decisiones técnicas no triviales tomadas durante el proyecto, para no
tener que redescubrirlas o repreguntarlas en cada etapa.

## Corrección manual de F1_PIN_R2 (valores fuera de escala)

Los valores originales de la columna `F1_PIN_R2` en `master_matrix.csv` estaban fuera
de escala respecto al resto de la matriz (hasta 1533, cuando ninguna otra columna
supera ~15). Enzo corrigió manualmente el archivo fuente reemplazando esos valores por
el promedio de `F1_PIN_R1` y `F1_PIN_R3` para esa misma proteína, en 396 de las 975
proteínas. Esta corrección se hizo directamente sobre el dato fuente, no fue generada
por ningún script de este repositorio.

**Implicancia para el análisis**: para esas 396 proteínas, `F1_PIN_R2` ya no es una
medición independiente, sino un promedio de las otras dos réplicas de esa misma
condición. Esto hay que tenerlo en cuenta al interpretar la consistencia entre
réplicas de la condición F1_PIN en cualquier PCA: va a parecer más consistente de lo
que sería con una tercera réplica real, porque en parte "copia" a las otras dos.

## Réplicas idénticas en algunas condiciones

Se detectó que en algunas condiciones (ej. las 3 réplicas de `F1_VM`) los valores son
idénticos entre sí, columna por columna. Se confirmó con Enzo que esto es una
característica real de cómo llegan esas muestras (no un error al armar
`master_matrix.csv` ni un artefacto de este repositorio).

**Implicancia para el análisis**: por ahora no se le da más peso que esta anotación,
pero hay que tener presente que los grupos con réplicas idénticas van a verse
artificialmente "perfectos" en términos de consistencia entre réplicas — esa
consistencia no es evidencia de nada biológico, es un reflejo de cómo se generó el
dato.

## Etapa 2 — probar dos umbrales de filtrado en vez de elegir uno solo

Para la variante de tratamiento de ceros, se decidió correr y comparar dos umbrales de
`min_samples_detected` (≥2 y ≥3 de 27 muestras) en vez de elegir uno de entrada. La
idea es ver el efecto del filtrado antes de comprometerse con un umbral, en vez de
asumir uno por defecto sin evidencia.

**Resultado de la comparación** (ver `results/filtro_min2_vs_min3_comparacion.md`):
el umbral ≥3 resuelve el outlier de `P_RM_R1` (detectado en el diagnóstico anterior),
mientras que ≥2 lo mejora solo parcialmente. Ninguno de los dos resuelve el outlier de
`F1_PIN_R1`. Todavía no se eligió un umbral definitivo — queda para cuando se sumen
más variantes (Etapa 3 en adelante) y se pueda comparar con más información.

## Posible efecto de orden/lote entre réplicas R1/R2/R3 — pregunta abierta, sin resolver

Se agrupó la cantidad de proteínas detectadas por réplica (R1, R2, R3), juntando las
27 muestras sin importar genotipo ni etapa (ver
`results/baseline/diagnostics/detection_by_replicate.png` y
`detection_by_replicate_table.csv`). En conjunto, la mediana de proteínas detectadas
es parecida entre R1 (139) y R2 (138), pero R3 es notablemente más baja (50), y la
caja de R1 en el boxplot es la más ancha y alta de las tres.

**Ojo con sobre-interpretar esto**: al mirar el detalle por cada una de las 9
combinaciones genotipo+etapa, el patrón NO es parejo. Solo en 2 de los 9 grupos
(`P_PIN`, `P_RM`) se cumple el orden completo R1 > R2 > R3. En otros 3 grupos el orden
va al revés o R3 es la que más detecta (`C_PIN`, `C_RM`, `P_VM`), y en los grupos con
réplicas idénticas (`C_VM`, `F1_VM`, `F1_RM` — ver la sección de arriba) el orden no
aplica porque dos de las tres réplicas son la misma medición repetida. En total, R1 es
mayor que R3 en 5 de los 9 grupos, no en "casi todos".

**Pregunta abierta para la directora, sin proponer solución todavía**: ¿las réplicas
R1, R2 y R3 se procesaron en tandas, días o lotes de laboratorio distintos? Si es así,
la tendencia agregada (R3 detectando menos que R1/R2 en el conjunto de datos) podría
ser un efecto técnico de orden/lote y no biológico — aunque el hecho de que no se
repita parejo en las 9 combinaciones también podría indicar que no es tan sistemático,
o que se mezcla con otras causas. Esto necesita información del diseño experimental
que no está en `master_matrix.csv` para poder confirmarse.

## Análisis cualitativo — correr las tres reglas de presencia en vez de elegir una

Al pasar al análisis de presencia/ausencia hubo que definir cuándo una proteína cuenta
como "presente" en un grupo de 9 muestras (ej. en Caimanta). Enzo decidió correr y
comparar las tres alternativas en vez de asumir una, siguiendo el mismo criterio que en
la Etapa 2 con min2/min3:

- `min1`: detectada en ≥1 de las 9 muestras del grupo.
- `min2`: detectada en ≥2 de las 9 muestras del grupo.
- `rep3`: detectada en las 3 réplicas de al menos una condición del grupo. Para la
  variable réplica (R1/R2/R3), que no tiene réplicas anidadas, se aproxima con ≥3 de 9.

**Resultado de la comparación** (ver `results/cualitativo_comparacion_reglas.md`):
`min1` queda dominado por `P_RM_R1` (aporta 234 proteínas exclusivas de esa sola muestra)
y `rep3` queda inflado en F1 y VM por las condiciones con réplicas idénticas, que cumplen
"presente en las 3 réplicas" por construcción. `min2` es la menos sesgada de las tres,
pero todavía no se elige una sola: la inestabilidad de los resultados entre reglas es
parte del hallazgo y conviene mostrarla.
