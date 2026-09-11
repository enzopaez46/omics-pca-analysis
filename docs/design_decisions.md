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

## Qué réplica conservamos al excluir las repetidas — a confirmar entre nosotros

Para las variantes `results/sin_duplicados/` (23) y `results/solo_mediciones_reales/`
(22) hubo que elegir cuál de las réplicas repetidas se queda. La regla que usamos es
**conservar la de número de réplica más bajo** (la primera en el orden del archivo):

| Condición | Réplicas iguales | Se queda | Se saca |
|---|---|---|---|
| `C_VM`  | R2 = R3           | R1 y R2 | `C_VM_R3` |
| `F1_VM` | R1 = R2 = R3      | R1      | `F1_VM_R2`, `F1_VM_R3` |
| `F1_RM` | R2 = R3           | R1 y R2 | `F1_RM_R3` |

Son 4 columnas, y quedan 23 mediciones independientes de las 27 del archivo.

**La regla es arbitraria y en este caso no cambia nada**: como las columnas son idénticas,
da exactamente lo mismo quedarse con R2 que con R3. La anotamos solo para que la variante
se pueda reproducir. Si algún día sacamos columnas *casi* iguales (no exactas), ahí la
regla ya no sería neutral y habría que repensarla.

**La variante de 22** suma a `F1_PIN_R2`, donde 396 de las 975 proteínas son el promedio
de R1 y R3 (ver más arriba), así que tampoco es una medición del todo independiente. La
separamos en dos variantes a propósito, para cambiar un factor por vez y poder ver el
efecto de cada cosa.

**Resultado**: ni sacando las repetidas ni sacando además la promediada cambia el PCA
(PC1 va de 31.82% a 31.87% a 32.11%, correlación 0.9996). Detalle en
`results/comparacion_27_vs_23.md` y en `docs/para_debatir.md`.

**Falta confirmarlo entre nosotros**: la regla la elegí yo (Lucas) para poder medir el
efecto, no la charlamos todavía.
