# Plan de etapas — PCA proteómica de tomate

Hoja de ruta para ir aprendiendo PCA mientras se avanza en el análisis real. Cada etapa
es chica a propósito: se ejecuta, se mira el resultado, se entiende, y recién ahí se pasa
a la siguiente. No hace falta tener todas las decisiones tomadas de antemano — varias se
van a ir ajustando etapa por etapa.

## Etapa 0 — Setup del proyecto

**Objetivo**: dejar el proyecto listo para trabajar.

**Entregables**:
- Estructura de carpetas creada (ver CLAUDE.md).
- `CLAUDE.md` y `README.md` en la raíz.
- `requirements.txt` con las librerías necesarias.
- `data/master_matrix.csv` confirmado en su lugar (no se mueve ni se edita).

Todavía no se escribe el script de PCA.

## Etapa 1 — PCA baseline

**Objetivo**: correr un primer PCA simple para tener un panorama general, sin
sofisticaciones todavía.

**Decisiones por defecto para esta etapa** (razonables para arrancar, se pueden
cuestionar y cambiar en etapas siguientes):
- Cada **muestra** es una observación (fila) y cada **proteína** es una variable
  (columna) → hay que transponer `master_matrix.csv`.
- Los ceros se mantienen tal cual, sin filtrar ni imputar (primera pasada).
- Se estandariza cada proteína (z-score) antes del PCA, porque las abundancias entre
  proteínas distintas pueden tener escalas muy diferentes.
- No se filtra ninguna proteína todavía.

**Entregables**:
- Gráfico PC1 vs PC2 (color = genotipo, forma = etapa de maduración).
- Tabla de % de varianza explicada por componente (PC1, PC2, PC3, ...).
- Tabla de coordenadas de las muestras (scores).
- Entrada en `docs/analysis_notes.md`.

**Preguntas a responder mirando el resultado**: ¿las réplicas de una misma condición
aparecen cerca entre sí? ¿PC1 y/o PC2 parecen separar por genotipo o por maduración?
¿hay alguna muestra que se vea como outlier?

## Etapa 2 — Variante: tratamiento de los ceros

**Objetivo**: entender cuánto influye en el resultado el hecho de que los ceros
representen "no detectado" y no "abundancia cero".

**Ideas a probar** (una o dos por vez, no todas juntas):
- Filtrar proteínas detectadas en muy pocas muestras (ej. menos de N de 27).
- Reemplazar los ceros por un valor mínimo pequeño en vez de 0 puro.

**Comparación**: contra el resultado de la Etapa 1 (baseline). ¿Cambia mucho la
separación entre grupos? ¿Cambian las proteínas más influyentes?

## Etapa 3 — Variante: transformación y escalado

**Objetivo**: evaluar si una transformación logarítmica (habitual en proteómica, porque
las abundancias suelen tener distribución muy asimétrica) cambia la interpretación.

**Comparación**: log-transform + escalado vs. escalado simple (Etapa 1).

## Etapa 4 — Contribución de las proteínas (loadings)

**Objetivo**: identificar qué proteínas contribuyen más a PC1 y PC2 en la variante que
mejor haya funcionado hasta acá, para poder pasar de "las muestras se separan" a "estas
proteínas parecen estar asociadas a esa separación".

## Etapa 5 — Síntesis y revisión con la directora

**Objetivo**: comparar las variantes probadas, elegir la que mejor represente los datos
(o combinar hallazgos de varias), y armar un resumen breve y honesto sobre qué patrones
aparecen y con qué nivel de confianza, para llevar a la reunión con la directora.

---

### Nota sobre el ritmo de trabajo

No hace falta resolver todas las etapas en una sola sesión con Claude Code. La idea es
un prompt (o pocos) por etapa, revisar el resultado, y recién ahí pedir la siguiente.
Cada variante que se descarte también es información útil — no hay que borrarla, alcanza
con dejarla en su carpeta y anotar en `docs/analysis_notes.md` por qué no se siguió por
ese camino.
