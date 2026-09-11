# PXD036132 — dónde están los datos del paper y cómo se corresponden con los nuestros

El paper del material suplementario es:

> Di Giacomo, M.; Vega, T.A.; Cambiaso, V.; Picardi, L.A.; et al.
> *An Integrative Transcriptomics and Proteomics Approach to Identify Putative Genes
> Underlying Fruit Ripening in Tomato near Isogenic Lines with Long Shelf Life.*
> **Plants 2023, 12, 2812.** https://doi.org/10.3390/plants12152812

Es open access (MDPI), también en PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC10421356/

## Los datos están públicos

Del Data Availability Statement del paper:

> "The MS proteomics data were deposited to the ProteomeXchange Consortium via the PRIDE
> partner repository with the dataset identifier **PXD036132**."

https://www.ebi.ac.uk/pride/archive/projects/PXD036132

**Qué hay ahí** (submission type: PARTIAL):

| Tipo | Cantidad | Tamaño c/u | Total aprox. |
|---|---|---|---|
| `.raw` (espectros crudos, Q Exactive) | 24 | 815–977 MB | ~21 GB |
| `.pdResult` (salida de Proteome Discoverer 2.2) | 24 | 205–630 MB | ~10 GB |
| `ID_details.txt` (mapeo de muestras) | 1 | 950 bytes | — |

**No hay ninguna matriz de abundancias lista para usar.** Ni xlsx, ni csv, ni
`proteinGroups.txt`, ni mzTab. Las tablas S3–S6 del suplementario solo tienen el
resultado de la comparación (limma: t, p-valor, log2FC), no los valores por muestra.

## Correspondencia con nuestras muestras

Copiado de `ID_details.txt` del repositorio, con la columna de la derecha agregada por
nosotros:

| Archivo | Genotipo | Etapa | Rép. | Nuestra muestra equivalente |
|---|---|---|---|---|
| JP01 | Caimanta (CAI) *S. lycopersicum* | Mature green | R1 | `C_VM_R1` |
| JP02 | Caimanta (CAI) *S. lycopersicum* | Mature green | R2 | `C_VM_R2` |
| JP03 | Caimanta (CAI) *S. lycopersicum* | Mature green | R3 | `C_VM_R3` |
| JP04 | Caimanta (CAI) *S. lycopersicum* | Red ripe | R1 | `C_RM_R1` |
| JP05 | Caimanta (CAI) *S. lycopersicum* | Red ripe | R2 | `C_RM_R2` |
| JP06 | Caimanta (CAI) *S. lycopersicum* | Red ripe | R3 | `C_RM_R3` |
| JP07 | LA0722 *S. pimpinellifolium* | Mature green | R1 | `P_VM_R1` |
| JP08 | LA0722 *S. pimpinellifolium* | Mature green | R2 | `P_VM_R2` |
| JP09 | LA0722 *S. pimpinellifolium* | Mature green | R3 | `P_VM_R3` |
| JP10 | LA0722 *S. pimpinellifolium* | Red ripe | R1 | `P_RM_R1` |
| JP11 | LA0722 *S. pimpinellifolium* | Red ripe | R2 | `P_RM_R2` |
| JP12 | LA0722 *S. pimpinellifolium* | Red ripe | R3 | `P_RM_R3` |
| JP13–JP18 | NIL115 | MG y RR | R1–R3 | (no tenemos NILs) |
| JP19–JP24 | NIL080 | MG y RR | R1–R3 | (no tenemos NILs) |

**12 de sus 24 muestras corresponden a 4 de nuestras 9 condiciones**, con la misma
estructura de tres réplicas. Lo que no está: nuestro híbrido F1 y nuestra etapa PIN
(pintón), que en su diseño no existen.

## Por qué esto es interesante para nosotros

Dos de esas condiciones son justo las que nos están dando problemas:

- **`C_VM`**: en nuestra matriz R2 y R3 son la misma columna repetida. Ellos tienen tres
  réplicas medidas de verdad.
- **`P_RM`**: es nuestra condición con la dispersión más alta entre réplicas (62.2), con
  R1 detectando 697 proteínas y R3 detectando 15. Ellos tienen tres réplicas
  independientes de exactamente esa condición.

O sea que con sus valores por muestra podríamos chequear si el problema de profundidad de
detección tan desigual **es propio de la técnica y del tejido, o es algo de nuestras
corridas**. Es el diagnóstico más directo que tenemos disponible para la duda del método.

## Lo que NO se puede hacer con esto

**No sirve como réplica extra pegada a nuestra matriz.** Es otro experimento, otro equipo
(Q Exactive), y sobre todo otra normalización: ellos usan log + imputación con
distribución normal desplazada (width 0.3, downshift 1.8) sobre Proteome Discoverer 2.2,
y nuestra matriz viene normalizada a un total fijo de 100 por muestra. Los números no son
comparables columna a columna.

Además el paper habla de **tres réplicas técnicas**, no biológicas — distinto de nuestro
diseño.

## Los dos caminos para conseguir las abundancias

**Camino corto (recomendado): pedirlas.** Los autores son del mismo grupo de Rosario que
aparece en las referencias 28, 29, 30, 31, 32, 66, 69 y 70 del paper (Zorzoli, Pratta,
Picardi, Rodríguez, Cambiaso, Pereira da Costa) — es decir, la misma línea de trabajo de
la que sale nuestro proyecto. Muy probablemente la directora los conozca o sea parte del
grupo. Un mail pidiendo la tabla de abundancias procesada resuelve en un día lo que por
el otro camino son varios.

**Camino largo (si no se puede pedir): bajar los `.pdResult`.** Los archivos `.pdResult`
de Proteome Discoverer son en realidad bases SQLite, así que se pueden abrir con
`sqlite3` sin la licencia comercial de Thermo. Para nuestro caso alcanzaría con los 12 de
CAI y LA0722 (JP01–JP12), unos 3–7 GB. El esquema interno no está documentado, así que
hay que explorarlo. Es factible pero no es una tarde.

Los `.raw` (21 GB) solo tendrían sentido si quisiéramos re-procesar todo desde cero con
nuestro propio pipeline, lo cual es otro proyecto.
