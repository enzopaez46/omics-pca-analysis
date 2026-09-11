---
name: resumen-ejecutivo
description: Armar un resumen corto y honesto de todo el análisis para llevar a una reunión. Usar en la Etapa 5, cuando se pide "armá el resumen para la directora", "necesito algo corto para la reunión", "resumí todo el proyecto", o cuando hay que presentar el estado del análisis a alguien que no lo siguió. Correr sintesis-hallazgos antes.
---

## Cuándo usarla

- Etapa 5 del plan: síntesis y revisión con la directora.
- Cuando hay que presentar el estado del análisis a alguien que no lo siguió de cerca.

Requisito previo: los hallazgos ya tienen que estar sintetizados y con nivel de confianza
asignado. Si no, correr primero **sintesis-hallazgos**.

## Proceso

1. **Empezar por la conclusión, no por el recorrido.** El orden cronológico ("primero
   corrimos el baseline, después...") es para la bitácora. Un resumen para reunión arranca
   con lo más importante en la primera oración, y después justifica.

2. **Estructurar en estas cinco partes, en este orden y no más de una página:**

   - **Dónde estamos** (2-3 oraciones) — qué se probó y qué se ve hasta ahora. Incluyendo
     el resultado incómodo si existe: hasta acá no se ve separación clara por genotipo ni
     por maduración en ninguna de las variantes.
   - **Lo que sí sabemos** (3-4 puntos) — hallazgos con nivel de confianza. Cada uno en una
     línea, con el número que lo respalda.
   - **Lo que no sabemos todavía** (2-3 puntos) — las preguntas abiertas, dichas como
     preguntas.
   - **Qué necesitamos de vos** — la parte más importante de la reunión. Separar en:
     información del laboratorio (tandas, lotes, protocolo), decisiones que no se pueden
     tomar sin criterio biológico, y validación de interpretación.
   - **Próximos pasos propuestos** — 2-3 opciones concretas, no una lista de deseos.

3. **Un número por afirmación, y que se pueda rastrear.** "PC1 baja de 31.8% a 25.4% al
   filtrar" es verificable en `results/*/tables/variance_explained.csv`. "El filtrado
   mejora bastante" no dice nada.

4. **Declarar las limitaciones dentro del resumen, no en una nota al pie.** Las tres que
   este proyecto tiene que mencionar siempre que hable de consistencia entre réplicas:
   - `F1_PIN_R2` fue corregida manualmente en 396 de 975 proteínas con el promedio de R1 y
     R3, así que no es una tercera medición independiente.
   - Algunas condiciones tienen réplicas idénticas entre sí, así que su consistencia no es
     evidencia biológica.
   - La matriz viene normalizada a un total fijo, así que las diferencias de abundancia
     total no existen en este dato.

5. **Formular las preguntas para que sean respondibles.** Mal: "¿por qué P_RM_R1 detecta
   tantas proteínas?". Bien: "¿P_RM_R1 y F1_PIN_R1 se procesaron en una corrida o tanda
   distinta al resto? Detectan 697 y 356 proteínas contra una mediana de ~100, y eso
   explica su posición en el PCA."

6. **Ningún resultado como conclusión definitiva.** Regla del proyecto: todo es
   exploratorio hasta que se revise con la directora. El resumen tiene que sonar así, sin
   por eso ser vago.

7. **Guardarlo donde se pueda encontrar** — `results/resumen_etapa5.md` o similar — y
   dejar una entrada corta en `docs/analysis_notes.md`.

## Qué necesito de vos

- Para quién es y cuánto tiempo hay para presentarlo.
- Si hay alguna pregunta o decisión específica que la reunión tiene que resolver.
- Si querés incluir gráficos, cuáles (recomendación: uno o dos, no seis).

## Qué produce

- Resumen de una página con las cinco secciones.
- Lista de preguntas concretas para la directora, separadas por tipo.
- Selección de 1-2 gráficos con una línea de lectura cada uno.
- Versión oral de 30 segundos para abrir la reunión.

## Ojo con

- **Esconder el resultado incómodo.** Que todavía no se vea separación por genotipo es
  información valiosa sobre el dato, y es mejor que salga de vos en la reunión.
- **Llenar de detalle metodológico.** El detalle va en `docs/` y en los scripts; el
  resumen dice qué se decidió y por qué, no cómo se implementó.
- **Presentar variantes descartadas como fracasos.** Cada variante descartada acotó el
  problema: `min3` resolvió el outlier de `P_RM_R1` y eso es un hallazgo.
