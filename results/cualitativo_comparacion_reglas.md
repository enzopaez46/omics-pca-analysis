# Comparación de las tres reglas de presencia (análisis cualitativo)

Paradigma nuevo: en vez de mirar cuánta abundancia tiene cada proteína (PCA), acá se
mira solamente **si la proteína se detectó o no** en cada grupo, y se comparan los
repertorios de las tres variables del diseño: genotipo (C=Caimanta, P=Pinton, F1),
etapa (VM, PIN, RM) y réplica (R1, R2, R3).

Como no había un criterio acordado para decir "esta proteína está presente en Caimanta"
(un grupo son 9 muestras), se corrieron las tres reglas y se comparan acá, igual que se
hizo con los umbrales min2/min3 de la Etapa 2:

| regla | qué exige |
|-------|-----------|
| `min1` | detectada en ≥1 de las 9 muestras del grupo |
| `min2` | detectada en ≥2 de las 9 muestras del grupo |
| `rep3` | detectada en las 3 réplicas de al menos una condición del grupo (para la variable réplica, que no tiene réplicas internas, se aproxima con ≥3 de 9) |

Resultados en `results/cualitativo_min1/`, `cualitativo_min2/` y `cualitativo_rep3/`
(cada una con `figures/` — Venn, heatmap de similitud, barras de intersecciones — y
`tables/`).

## Cuántas proteínas quedan en juego

| regla | genotipo | etapa | réplica |
|-------|----------|-------|---------|
| min1 | 973 | 973 | 973 |
| min2 | 593 | 543 | 543 |
| rep3 | 185 | 185 | 330 |

De 975 proteínas, 973 se detectan en alguna muestra; pero solo 185 se detectan de forma
reproducible en las 3 réplicas de alguna condición. O sea: **el 81% de la matriz son
detecciones que no se repiten dentro de un mismo trío de réplicas**.

## Genotipo (C=Caimanta, P=Pinton, F1)

Tamaño del repertorio de cada genotipo y núcleo compartido por los tres:

| regla | C | P | F1 | compartidas por los 3 | Jaccard medio |
|-------|---|---|----|----------------------|---------------|
| min1 | 408 | 863 | 413 | 247 (25.4%) | 40.8% |
| min2 | 219 | 434 | 413 | 159 (26.8%) | 41.7% |
| rep3 | 88 | 29 | 166 | 20 (10.8%) | 25.6% |

El ranking de "quién detecta más" se da vuelta según la regla: con `min1` Pinton parece
el genotipo más rico (863 proteínas, con 417 exclusivas), pero eso viene casi entero de
`P_RM_R1`, la muestra que detecta 697 proteínas y aporta 234 exclusivas de ella sola (ya
diagnosticado en `docs/analysis_notes.md`). Con `rep3` pasa lo contrario: Pinton se cae a
29 proteínas y F1 queda con 166, pero eso también es artificial, porque F1_VM y F1_RM
tienen réplicas idénticas (ver `docs/design_decisions.md`) y por definición cumplen
"detectada en las 3 réplicas".

Con `min2` (la regla donde los dos artefactos pesan menos, aunque no desaparecen) el par
más parecido es **Pinton–F1 (47.8% Jaccard)**, después C–F1 (39.8%) y último C–P (37.5%).
Mirando el solapamiento asimétrico: el 82% del repertorio de Caimanta está también en F1,
y el 63% del de Pinton está en F1.

Lecturas posibles de eso, sin elegir una:
- **Biológica**: un híbrido que hereda repertorio de los dos padres daría justamente
  F1 contiendo buena parte de C y de P.
- **Técnica**: F1 podría simplemente tener más profundidad de detección, y "contener a
  los padres" ser consecuencia de detectar más, no de heredar.
- **De diseño**: F1_VM y F1_RM tienen réplicas idénticas, lo que infla artificialmente
  su repertorio (ver `docs/design_decisions.md`).

Qué haría falta para separarlas: comparar los tres genotipos a igual profundidad
(ej. submuestreando a la misma cantidad de detecciones por muestra) y rehacer el
solapamiento sin las condiciones con réplicas idénticas.

## Etapa de maduración (VM, PIN, RM)

| regla | VM | PIN | RM | compartidas por las 3 | Jaccard medio |
|-------|----|-----|----|----------------------|---------------|
| min1 | 257 | 627 | 783 | 190 (19.5%) | 35.3% |
| min2 | 212 | 413 | 301 | 111 (20.4%) | 36.0% |
| rep3 | 160 | 91 | 16 | 8 (4.3%) | 18.3% |

Acá la inestabilidad es todavía más fuerte: con `min1` el orden es RM > PIN > VM, con
`min2` es PIN > RM > VM y con `rep3` se invierte del todo (VM > PIN > RM, con RM en 16
proteínas). Una tendencia biológica real no debería darse vuelta al cambiar el umbral.
Con `min1`/`min2` el par más parecido es PIN–RM (48.6% / 42.0%), lo cual sí tendría
sentido biológico (etapas consecutivas), pero con `rep3` el par más parecido pasa a ser
VM–PIN.

Dos lecturas conviven acá: que el orden lo esté marcando la **profundidad de detección**
de cada muestra (y no la maduración), o que haya señal de maduración real **tapada** por
esa diferencia de profundidad. La inestabilidad entre reglas no permite distinguirlas:
dice que el resultado depende del umbral, no cuál de las dos causas manda. Para separarlas
habría que comparar etapas dentro de un mismo genotipo y controlando profundidad.

## Réplica (R1, R2, R3)

| regla | R1 | R2 | R3 | compartidas por las 3 | Jaccard medio |
|-------|----|----|----|----------------------|---------------|
| min1 | 945 | 525 | 265 | 248 (25.5%) | 42.1% |
| min2 | 527 | 253 | 150 | 142 (26.2%) | 42.7% |
| rep3 | 316 | 158 | 90 | 83 (25.2%) | 41.7% |

Este es el único patrón que se mantiene igual con las tres reglas, y es el más claro de
todo el análisis: los repertorios están **anidados**, R3 ⊂ R2 ⊂ R1. El 95-97% de lo que
detecta R3 también lo detecta R2, y el 92-95% de lo que detecta R2 también lo detecta R1;
en cambio solo el 27% de lo que detecta R1 aparece en R3. Las proteínas exclusivas de R2
y R3 son 10 y 2 (min2), prácticamente nada, mientras R1 tiene 286 exclusivas.

Anidado quiere decir que R1, R2 y R3 no ven cosas distintas: ven **cada vez menos de lo
mismo**. Esa forma es compatible con una diferencia de sensibilidad/profundidad entre
corridas, pero el patrón por sí solo no prueba la causa; solo dice que las réplicas no son
intercambiables. Lo que haría falta para cerrarlo es información externa al dato: en qué
orden/lote se procesó cada réplica, y si hay alguna métrica de la corrida (nº total de
espectros, intensidad total) que ordene R1 > R2 > R3 igual que el repertorio. Queda
enganchado con la pregunta abierta sobre lotes anotada en `docs/design_decisions.md`.

## Qué queda sobre la mesa (exploratorio, nada cerrado)

Esto no son conclusiones: son las observaciones que quedaron y las preguntas que abren.
La interpretación es de Enzo y la decisión final de la directora.

**Observaciones**

- El patrón más estable de todo el análisis no está en genotipo ni en etapa, sino en
  **réplica**: repertorios anidados R3 ⊂ R2 ⊂ R1 con las tres reglas.
- De 975 proteínas, 973 se detectan en alguna muestra pero solo 185 se detectan en las
  3 réplicas de alguna condición: la mayor parte de la matriz son detecciones que no se
  repiten dentro de un mismo trío.
- El ranking de etapas se da vuelta según la regla (RM > PIN > VM con `min1`,
  VM > PIN > RM con `rep3`); el de genotipos también.
- `min1` está dominado por `P_RM_R1` (697 proteínas, 234 exclusivas de esa sola muestra)
  y `rep3` está inflado por las condiciones con réplicas idénticas.

**Preguntas abiertas**

1. ¿El orden R1 > R2 > R3 es de procesamiento (lote, orden de corrida, sensibilidad del
   equipo) o puede haber algo del diseño que lo explique? Sin el dato de cómo se
   procesaron las muestras no se puede responder desde la matriz.
2. Si ese efecto existe, ¿tapa una señal de genotipo/etapa, o directamente no hay señal
   de repertorio que encontrar? Son dos escenarios distintos y este análisis no los
   separa.
3. La similitud P–F1 > C–F1 > C–P, ¿es herencia del híbrido o profundidad de detección?
   (ver alternativas en la sección de genotipo).
4. ¿Qué regla mostrar en la reunión? Argumento a favor de mostrar las tres: la
   inestabilidad entre reglas es información. Argumento a favor de `min2`: es donde menos
   pesan los dos artefactos conocidos. Queda a criterio de Enzo/la directora.
5. Las réplicas idénticas de F1_VM y F1_RM: ¿son un error de armado de la matriz o son
   así en el dato original? Esto conviene chequearlo antes de la reunión, porque cambia
   la lectura de casi todo lo de genotipo.

**Pendiente natural**

Repetir esto por condición (las 9 combinaciones genotipo+etapa) en vez de por variable
suelta, para ver si el efecto de réplica se puede mirar por separado del de
genotipo/etapa.
