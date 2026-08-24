# Bitácora de análisis

## 2026-08-24 — Etapa 1: PCA baseline

Se corrió el primer PCA (`results/baseline/`) dejando los ceros tal cual y
estandarizando cada proteína antes del análisis, sin filtrar nada. PC1 explica un 31.8%
de la variación y PC2 un 15.1% (juntos, casi la mitad).

En el gráfico casi todas las muestras quedan amontonadas en un mismo punto, salvo dos que
se disparan lejos del resto: `P_RM_R1` (muy separada en PC1) y `F1_PIN_R1` (muy separada
en PC2). Con esas dos dominando el gráfico, todavía no se puede ver si hay separación
real por genotipo o por maduración — hay que resolver el tema de las outliers antes de
sacar conclusiones sobre eso.

Además, al revisar los datos crudos aparece algo raro: varias réplicas de una misma
condición tienen valores idénticos entre sí (ej. las 3 réplicas de `F1_VM` son
exactamente iguales, columna por columna). Duda para la próxima: ¿es un error al armar
`master_matrix.csv` (columnas duplicadas por error) o tiene una explicación válida?
Conviene confirmarlo antes de seguir, porque si son duplicados de verdad están
inflando artificialmente la "consistencia" entre réplicas.

**Actualización**: la duda de las réplicas idénticas quedó resuelta — no es un error,
es así como llegan esas muestras. Queda documentado en `docs/design_decisions.md`,
junto con otra corrección manual sobre `F1_PIN_R2`. No hace falta re-correr el
baseline: ya se calculó sobre esta versión corregida de la matriz.

## 2026-08-24 — Diagnóstico: por qué se disparan P_RM_R1 y F1_PIN_R1

Se investigó si el motivo por el que estas dos muestras dominan PC1 y PC2 es parecido
al error de escala de `F1_PIN_R2` (ver `results/baseline/diagnostics/`). **No lo es**:
sus valores más altos (7.9 y 3.2) están dentro del rango normal de la matriz, nada
parecido a los 1533 de aquel error.

Lo que sí se encontró es que la matriz tiene muchos ceros (cada proteína se detecta en
promedio en solo 4 de las 27 muestras), y que estas dos muestras concentran una
cantidad inusual de proteínas "raras": 234 proteínas se detectan únicamente en
`P_RM_R1` y en ninguna otra muestra. Al estandarizar, muchas proteínas así empujan un
poco cada una en la misma dirección y la muestra termina lejos del resto — no es culpa
de un puñado de proteínas puntuales ni de un error de carga.

Hipótesis para seguir: esto probablemente se relacione directamente con la Etapa 2
(tratamiento de ceros / filtrado de proteínas poco detectadas), porque filtrar
proteínas raras debería achicar bastante este efecto.

## 2026-08-24 — Etapa 2: filtrado de proteínas poco detectadas (min2 y min3)

Se corrieron dos variantes filtrando proteínas detectadas en pocas muestras antes del
PCA: `filtro_min2` (≥2 de 27 muestras, quedan 639 proteínas) y `filtro_min3` (≥3 de 27,
quedan 443). Se comparan entre sí y contra el baseline en
`results/filtro_min2_vs_min3_comparacion.md`.

El resultado confirma la hipótesis de la nota anterior: `P_RM_R1` deja de ser un
outlier extremo con el filtro más estricto (min3) — pasa de estar clavado solo en un
extremo del gráfico a caer dentro del rango normal de las demás muestras. Con min2
mejora, pero no del todo. En cambio, `F1_PIN_R1` sigue siendo la muestra más alejada
del resto en las dos variantes filtradas — filtrar ceros no resuelve su caso, así que
debe tener otra causa que todavía no investigamos.

Con ninguna de las tres versiones (baseline, min2, min3) se ve todavía una separación
clara por genotipo o por maduración: el resto de las muestras sigue amontonado, y lo
que domina el gráfico sigue siendo la posición de pocas muestras puntuales. Duda para
seguir: ¿por qué F1_PIN_R1 se mantiene como outlier a pesar del filtrado, y a qué se
debe?

## 2026-08-24 — Diagnóstico: ¿es un problema de abundancia total/carga?

Se chequeó si `P_RM_R1` y `F1_PIN_R1` tienen una abundancia total distinta al resto
(problema técnico típico: cuánto material se cargó, sensibilidad del equipo ese día),
ya que eso el z-score por proteína no lo corrige. Ver
`results/baseline/diagnostics/sample_totals.csv` y `.png`.

**No es un problema de abundancia total**: las 27 muestras suman prácticamente lo
mismo (entre 99.9967 y 100.0000 — la matriz ya viene normalizada así). Las diferencias
son de cuarta cifra decimal, sin relevancia real, aunque técnicamente `P_RM_R1` es la
más baja de las 27.

Lo que sí es real y llamativo: la **cantidad de proteínas detectadas**. La mediana de
la matriz es ~97-107 proteínas detectadas por muestra, pero `P_RM_R1` detecta 697 (la
que más detecta de las 27, por lejos) y `F1_PIN_R1` detecta 356 (la 4ª que más
detecta). O sea, ambas "ven" muchísimas más proteínas que una muestra típica, aunque
el total sumado dé igual (porque está normalizado). Esto sí encaja con una causa
técnica de proteómica — no cuánto material se cargó, sino qué tan sensible/profunda
fue esa corrida para detectar proteínas de baja abundancia — y explica por qué el
z-score las dispara: al normalizar a un total fijo con muchas más proteínas "activas",
cada proteína individual queda con valores más chicos y dispersos, lo que combinado
con la Etapa 2 arma el efecto que ya vimos.

Duda para seguir: ¿por qué estas muestras detectan tantas proteínas más que el resto?
¿Es una corrida distinta, un lote distinto, o algo del protocolo? Es una pregunta para
la directora más que algo que se resuelva con más preprocesamiento.

## 2026-08-24 — Diagnóstico: ¿el patrón de detección es por réplica (R1/R2/R3)?

Se miró si la cantidad de proteínas detectadas depende de si la muestra es R1, R2 o R3
(sin importar genotipo/etapa) — ver `results/baseline/diagnostics/detection_by_replicate.png`.
En conjunto, R3 detecta bastante menos que R1 y R2 (mediana 50 vs ~138), pero al
revisar grupo por grupo (`detection_by_replicate_table.csv`) el patrón no es parejo:
solo se cumple limpio en 2 de las 9 combinaciones genotipo-etapa. Quedó anotado como
pregunta abierta en `design_decisions.md` (posible efecto de lote/orden), sin
proponer todavía ninguna solución.
