# Para debatir — dónde estamos y qué queremos preguntar

Última actualización: 2026-08-26

Esto no es un informe, es una lista de cosas para discutir entre nosotros y después
llevar a la charla con la directora. Nada de acá está cerrado: son los temas que nos
parece que hay que decidir juntos, con los números que tenemos hasta ahora al lado de
cada uno.

---

## 1. Lo de las columnas repetidas y promediadas: probado, y no nos rompe el PCA

Sabemos que en la matriz hicimos dos cosas que no son ideales, y que hicimos porque fue
lo que se pudo con los problemas que aparecieron:

- **Repetimos columnas**: `C_VM_R3` es igual a `C_VM_R2`, las tres réplicas de `F1_VM`
  son iguales entre sí, y `F1_RM_R3` es igual a `F1_RM_R2`. Son 4 columnas que no son
  mediciones nuevas.
- **Promediamos para sacar una tercera réplica**: en `F1_PIN_R2`, 396 de las 975
  proteínas son el promedio de R1 y R3.

Corrimos el PCA sacando esas columnas para ver cuánto importa. **Casi nada:**

| Variante | n | PC1 | PC2 | Correlación con la corrida original |
|---|---|---|---|---|
| 27 columnas (como está hoy) | 27 | 31.82% | 15.06% | — |
| Sin las 4 repetidas | 23 | 31.87% | 15.32% | 0.9998 |
| Sin las repetidas **ni** la promediada | 22 | 32.11% | 14.80% | 0.9996 |

La correlación mide si las muestras quedan ordenadas igual en el gráfico. 0.9996 es
prácticamente idéntico.

Y hay una prueba más directa: proyectamos las 4 columnas repetidas dentro del PCA hecho
con las 23, y **caen exactamente encima de su gemela** (distancia 1e-15, o sea cero).
Tiene sentido: una columna repetida no agrega ninguna dirección nueva de variación,
solo duplica un punto que ya estaba.

**Lo que podemos decir con esto**: los parches que hicimos en la matriz no están
distorsionando el PCA. Está medido, no es una impresión.

**Lo que igual conviene aclarar nosotros, sin que nos lo pregunten**: son 23 mediciones
independientes, no 27 (o 22 si contamos también la promediada). El PCA es el mismo, pero
el N que decimos que tenemos debería ser el real. Y ojo con una cosa: `F1_VM` queda con
**una sola** medición, así que de esa condición no podemos decir nada sobre consistencia
entre réplicas — no es que las réplicas coincidan, es que hay una sola.

Todo esto está en `results/comparacion_27_vs_23.md`.

---

## 2. Esto sí nos preocupa: las muestras no detectan la misma cantidad de proteínas

Acá está lo que nos parece el tema de fondo, y es bastante más grande que lo de arriba.

La matriz tiene **85% de ceros**, y la cantidad de proteínas que detecta cada muestra
va de **4 a 697**:

| Muestra | Proteínas detectadas |
|---|---|
| `P_RM_R1` | 697 |
| `P_PIN_R1` | 494 |
| `F1_PIN_R2` | 379 |
| ... (mediana) | ~107 |
| `P_RM_R3` | 15 |
| `F1_RM_R2` / `R3` | 15 |
| `P_VM_R2` | 5 |
| `F1_RM_R1` | **4** |

O sea que `F1_RM_R1` "ve" 4 proteínas de 975 y pesa lo mismo en el PCA que `P_RM_R1`,
que ve 697.

Y cuando medimos qué tan parecidas son las réplicas de cada condición entre sí (distancia
promedio en el gráfico PC1-PC2), sale esto:

| Condición | Dispersión |
|---|---|
| `F1_VM` | 0 (réplicas repetidas, no medible) |
| `F1_RM` | 0.20 |
| `P_VM` | 0.22 |
| `C_VM` | 0.99 |
| `C_PIN` | 1.24 |
| `C_RM` | 11.1 |
| `P_PIN` | 23.6 |
| `F1_PIN` | 32.7 |
| `P_RM` | **62.2** |

Son **300 veces** de diferencia entre condiciones, con el mismo protocolo y el mismo
equipo. Y las que están más desparramadas son justo las que tienen réplicas con
profundidades muy distintas (`P_RM`: R1 detecta 697 y R3 detecta 15).

**La sospecha, dicha como sospecha**: si estandarizamos por proteína (z-score) sobre una
matriz con 85% de ceros, puede que PC1 y PC2 estén midiendo sobre todo *qué tan profunda
fue cada corrida del equipo* y no biología. Eso explicaría por qué en tres variantes
(baseline, min2, min3) todavía no vemos separación por genotipo ni por maduración: no
necesariamente porque no exista, sino porque estaría tapada.

No lo sabemos. Es la pregunta que queremos hacer.

---

## 3. El material suplementario: CAI somos nosotros

Leímos `docs/MaterialSuplementario/`. Es el paper de los NILs, y **tiene bastante que ver
con nosotros**:

| En el paper | Qué es | En nuestra matriz |
|---|---|---|
| **CAI** = Caimanta | *S. lycopersicum* cultivado, parental | casi seguro nuestro **C** |
| **LA0722** | *S. pimpinellifolium* silvestre, parental | casi seguro nuestro **P** |
| NIL115, NIL080 | líneas casi isogénicas (BC3S1 / BC4S1) | no las tenemos |
| MG (mature green) | verde maduro | nuestro **VM** |
| RR (red ripe) | rojo maduro | nuestro **RM** |
| — | — | nuestro **PIN** (pintón) no está en el paper |

Así que compartimos los dos parentales y dos de las tres etapas. Nuestro F1 es el híbrido
de CAI × LA0722, y el paper en vez del híbrido trabaja con los NILs. **Es el mismo
programa de investigación, mirado desde otro ángulo.**

### ¿Podemos usarlo como otra réplica? No — pero los datos existen y son públicos

En el suplementario no están las abundancias: las tablas S3 a S6 tienen `t_statistic`,
`P_Value`, `B(Bayes)` y `log2FoldChange` — **el resultado de una comparación ya hecha**
(RR vs MG con limma), no las mediciones. Nada que podamos pegar al lado de las nuestras.

**Pero encontramos dónde están los datos crudos.** El paper es
[Plants 2023, 12, 2812](https://doi.org/10.3390/plants12152812) y su Data Availability
Statement dice que depositaron todo en PRIDE con el identificador **PXD036132**. Bajamos
el archivo de mapeo de muestras (950 bytes) y **12 de sus 24 muestras son 4 de nuestras
9 condiciones**, con las mismas tres réplicas:

| Sus archivos | Genotipo | Etapa | Nuestras muestras |
|---|---|---|---|
| JP01–JP03 | CAI | Mature green | `C_VM_R1/R2/R3` |
| JP04–JP06 | CAI | Red ripe | `C_RM_R1/R2/R3` |
| JP07–JP09 | LA0722 | Mature green | `P_VM_R1/R2/R3` |
| JP10–JP12 | LA0722 | Red ripe | `P_RM_R1/R2/R3` |

Y justo dos de esas condiciones son las que nos están dando problemas: **`C_VM`** (donde
nuestras R2 y R3 son la misma columna repetida, y ellos tienen tres réplicas medidas de
verdad) y **`P_RM`** (nuestra condición con la dispersión más alta, 62.2, con R1
detectando 697 proteínas y R3 detectando 15).

**Igual no sirve como réplica pegada a nuestra matriz**, y esto es importante que quede
claro: es otro experimento, otro equipo (Q Exactive), y sobre todo otra normalización
—ellos usan log + imputación con normal desplazada sobre Proteome Discoverer 2.2, y
nuestra matriz viene normalizada a un total fijo de 100 por muestra. Los números no son
comparables columna a columna. Además el paper habla de **réplicas técnicas**, no
biológicas, que es un diseño distinto al nuestro.

**Para qué sí serviría**: chequear si el problema de profundidad de detección tan
desigual (el punto 2) es propio de la técnica y del tejido, o es algo de nuestras
corridas. Es el diagnóstico más directo que tenemos a mano para la duda del método.

El detalle completo (qué archivos hay, tamaños, y los dos caminos para conseguir las
abundancias) está en `docs/MaterialSuplementario/PXD036132_correspondencia.md`.

### Para qué sí sirve, y es más interesante

Sirve como **chequeo externo e independiente**. Los identificadores son los mismos
(UniProt), así que se puede cruzar directamente:

| Lista del paper | Proteínas | Están en nuestra matriz |
|---|---|---|
| DEPs de CAI (Tabla S3) | 117 | 46 (39%) |
| DEPs de LA0722 (Tabla S4) | 342 | 160 (47%) |
| DEPs de NIL115 (Tabla S5) | 111 | 37 (33%) |
| DEPs de NIL080 (Tabla S6) | 57 | 19 (33%) |

Y ya hicimos el cruce que importa: **¿las proteínas que más pesan en nuestro PC1 y PC2
son las que el paper encontró que cambian durante la maduración?**

| Corrida | Componente | Lista | Observado en el top-100 | Esperado por azar | p |
|---|---|---|---|---|---|
| baseline | PC1 | CAI | 4 | 4.7 | 0.71 |
| baseline | PC2 | CAI | 6 | 4.7 | 0.33 |
| min3 | PC1 | CAI | 5 | 5.6 | 0.71 |
| min3 | PC2 | CAI | 9 | 5.6 | 0.09 |
| min3 | PC1 | LA0722 | 19 | 19.4 | 0.60 |

**No hay ningún enriquecimiento.** Las proteínas que dominan nuestros componentes
principales son, hasta donde se puede ver, indistinguibles de una selección al azar
respecto de las que el paper asocia a la maduración.

Esto **no prueba** que nuestro PCA esté mal — el solapamiento es parcial (39-47%), son
experimentos distintos, y el paper compara solo MG contra RR. Pero es la primera
evidencia *independiente de nuestros propios datos* que apunta en la misma dirección que
el punto 2: lo que domina PC1 y PC2 no parece ser la biología de la maduración.

---

## 4. Lo que queremos charlar con la directora

Ordenadas de más concreta a más abierta. Las tres primeras son de información que solo
ella (o el laboratorio) puede darnos:

1. **¿Las réplicas R1, R2 y R3 se procesaron en tandas, días o lotes distintos?**
   En el conjunto R3 detecta menos que R1 y R2 (mediana 50 vs ~138), pero al mirar las 9
   combinaciones genotipo-etapa por separado el patrón se cumple limpio en solo 2. Si
   hubo tandas, eso podría explicarlo; si no, hay que buscar por otro lado.

2. **¿Por qué unas muestras detectan 697 proteínas y otras 4?** ¿Fue una corrida
   distinta, otro lote, un cambio en el protocolo, un problema puntual con esas muestras?

3. **¿Nos pueden pasar la tabla de abundancias por muestra del trabajo de los NILs
   (PXD036132)?** Es la pregunta más concreta que tenemos. Los datos están públicos en
   PRIDE, pero solo como `.raw` (21 GB) y `.pdResult` (10 GB) — no hay ninguna matriz
   procesada, así que sacarla desde el repositorio es varios días de trabajo. Si el grupo
   la tiene armada (que casi seguro sí, es lo que usaron para correr limma), es un mail.

   Y vale la pena mencionar que los autores son el mismo grupo que aparece en las
   referencias 28 a 32, 66, 69 y 70 del propio paper (Zorzoli, Pratta, Picardi,
   Rodríguez, Cambiaso, Pereira da Costa), o sea la misma línea de trabajo de la que sale
   este proyecto. Probablemente sea preguntar adentro de casa.

4. **La pregunta de método**: con 85% de ceros y profundidades de detección tan
   distintas, ¿el z-score por proteína es el preprocesamiento adecuado, o primero
   habría que igualar de alguna forma la profundidad de detección entre muestras?
   Esto no lo podemos decidir solos.

5. **¿Los parches de la matriz (columnas repetidas y promediadas) le parecen aceptables
   para un análisis exploratorio?** Nosotros ya medimos que no cambian el PCA, pero la
   decisión de si eso alcanza no es nuestra.

---

## 5. En qué ando yo (Lucas)

Para que quede claro dónde me meto y dónde no, porque el análisis y el PCA son de Enzo.

**Lo que hice:**

- Dejé el proyecto corriendo de nuevo (`.venv` + `requirements.txt`). No se podía
  regenerar nada: ninguna instalación de Python de la máquina tenía las librerías.
  Verifiqué que el baseline regenerado da un resultado idéntico byte a byte al que ya
  estaba guardado, así que no rompí nada.
- `scripts/check_matrix.py`: chequea la matriz antes de analizarla. Los tres problemas de
  la Etapa 1 (la columna fuera de escala, las réplicas repetidas, los ceros) los agarra
  juntos y de entrada, en vez de que aparezcan de a uno después de correr el PCA.
- `scripts/compare_sample_sets.py` y las variantes de 23 y 22 muestras: todo el punto 1.
- El cruce con el material suplementario del punto 3.

**Lo que no me corresponde y no voy a hacer:**

- Interpretar biología. Si el PCA separa o no por genotipo y qué significa, lo dice Enzo.
- Elegir el umbral de filtrado o el preprocesamiento. Puedo correr las variantes y armar
  las comparaciones; la decisión es de él.
- Tocar `data/master_matrix.csv`. Nunca.
- Presentar nada de esto como conclusión. Es material para decidir juntos.

**Lo que me queda pendiente:**

- Documentar cómo levantar y correr el proyecto, para que la directora pueda hacerlo en
  su máquina si quiere. Todavía no, esperamos a que se estabilicen las variantes.

**Cambios que hice sobre lo que ya estaba** (ninguno rompe resultados anteriores;
`baseline`, `filtro_min2` y `filtro_min3` quedaron intactas):

| Archivo | Qué cambió |
|---|---|
| `scripts/run_pca.py` | Agregué `--drop-duplicates` y `--exclude-samples`, y que guarde `samples_used.csv`. Sin argumentos reproduce el baseline igual que antes |
| `scripts/check_matrix.py` | Nuevo |
| `scripts/compare_sample_sets.py` | Nuevo |
| `CLAUDE.md` | Regla 9 (chequear el dato antes de cada variante) + sección de skills |
| `.claude/skills/` | Nuevo, 8 skills en español |
| `.gitignore` | Nuevo (hacía falta por el `.venv`) |
