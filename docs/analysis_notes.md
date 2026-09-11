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

## 2026-08-26 — Variantes: sacando las columnas repetidas (23) y la promediada (22)

Corrimos el PCA sacando las 4 columnas que son copia exacta de otra (`C_VM_R3`,
`F1_VM_R2`, `F1_VM_R3`, `F1_RM_R3`) → `results/sin_duplicados/`, y después sacando
además `F1_PIN_R2`, que es promedio de R1 y R3 en 396 proteínas →
`results/solo_mediciones_reales/`. Comparación en `results/comparacion_27_vs_23.md`.

**Casi no cambia nada**: PC1 va de 31.82% (27 columnas) a 31.87% (23) a 32.11% (22), y
la posición de las muestras correlaciona 0.9996 con la corrida original. Además
proyectamos las 4 copias dentro del PCA de 23 y caen exactamente encima de su gemela
(distancia 1e-15). Tiene sentido: una columna repetida no agrega ninguna dirección nueva
de variación, solo duplica un punto. Los parches que le hicimos a la matriz no están
distorsionando el PCA.

**Pero la consistencia entre réplicas se veía mejor de lo que es.** Con 3 réplicas hay 3
pares para comparar. En `C_VM` los pares dan 1.480, 1.480 y 0.000 — ese cero es R2 contra
R3, que son la misma columna, así que no es "dos mediciones que coinciden", es un número
comparado consigo mismo. El promedio (0.987) subestima el desacuerdo real (1.480) en un
33%. En `F1_VM` los tres pares dan 0: no hay ni una comparación real, así que su
consistencia no es perfecta, es **desconocida**. (Estos números están calculados todos
sobre el mismo PCA del baseline, para aislar el efecto de las copias del efecto de
recalcular el PCA.)

**Y aparte, algo más grande**: la dispersión entre réplicas va de 0.20 (`F1_RM`, `P_VM`)
a 62.2 (`P_RM`) según la condición. Son 300 veces de diferencia con el mismo protocolo.

Duda para seguir: esa diferencia parece ir de la mano con cuántas proteínas detecta cada
muestra (`P_RM` tiene R1 con 697 detectadas y R3 con 15). Si la consistencia entre
réplicas depende sobre todo de la profundidad de la corrida y no del genotipo o la etapa,
habría que pensar si el z-score sobre una matriz con 85% de ceros es el preprocesamiento
adecuado, o si primero hay que igualar de alguna forma la profundidad de detección.

## 2026-08-26 — Cruce con el material suplementario del paper de los NILs

Leímos `docs/MaterialSuplementario/` y **son nuestros mismos parentales**: CAI (Caimanta,
*S. lycopersicum*) es nuestro C, LA0722 (*S. pimpinellifolium*) es nuestro P, MG es
nuestro VM y RR nuestro RM. El paper en vez del híbrido F1 trabaja con NILs, y no tiene
la etapa PIN.

**No se puede usar como réplica extra**: las tablas S3-S6 no tienen abundancias por
muestra, tienen `t_statistic`, `P_Value` y `log2FoldChange` — el resultado de una
comparación ya hecha con limma, no las mediciones. No hay ninguna columna para pegar al
lado de las nuestras.

**Sí sirvió como chequeo externo.** Los identificadores son UniProt igual que los
nuestros, así que cruzamos las listas: de los 117 DEPs de CAI, 46 están en nuestra
matriz; de los 342 de LA0722, 160. Después miramos si las proteínas que más pesan en
nuestro PC1 y PC2 son las que el paper asocia a la maduración: **no hay ningún
enriquecimiento** (en el top-100 de loadings aparecen 4-9 DEPs cuando por azar se
esperarían 4.7-5.6; todos los p > 0.09, tanto en baseline como en filtro_min3).

Ojo con sobre-interpretarlo: el solapamiento es parcial (39-47% de los DEPs están en
nuestra matriz), son experimentos distintos con otro pipeline de cuantificación, y el
paper compara solo MG contra RR. No prueba que nuestro PCA esté mal. Pero es la primera
evidencia independiente de nuestros propios datos que apunta a lo mismo que la nota de
arriba: lo que domina PC1 y PC2 no parece ser la biología de la maduración.

**Encontramos dónde están los datos crudos de ese trabajo**: el paper es Plants 2023, 12,
2812 (doi 10.3390/plants12152812) y depositó todo en PRIDE con el identificador
**PXD036132**. Bajamos el archivo de mapeo de muestras y 12 de sus 24 muestras son 4 de
nuestras 9 condiciones, con las mismas tres réplicas: CAI/MG y CAI/RR son nuestros `C_VM`
y `C_RM`, y LA0722/MG y LA0722/RR son nuestros `P_VM` y `P_RM`. Justo dos de esas son las
que nos dan problemas (`C_VM` tiene réplicas repetidas en nuestra matriz, y `P_RM` es la
de dispersión más alta).

El problema es que en PRIDE solo hay `.raw` (21 GB) y `.pdResult` (10 GB): ninguna matriz
de abundancias procesada. Sacarla desde ahí es posible (los `.pdResult` de Proteome
Discoverer son bases SQLite) pero lleva varios días. Detalle en
`docs/MaterialSuplementario/PXD036132_correspondencia.md`.

Pregunta para la directora, ahora concreta: ¿nos pueden pasar la tabla de abundancias por
muestra de PXD036132? Los autores son el mismo grupo de las referencias 28-32, 66, 69 y
70 del paper, o sea la misma línea de trabajo que este proyecto.
