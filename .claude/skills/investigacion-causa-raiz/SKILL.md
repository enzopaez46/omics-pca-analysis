---
name: investigacion-causa-raiz
description: Investigación estructurada de un resultado inesperado. Usar cuando una muestra se dispara en el PCA, cuando una variante da un resultado que no se esperaba, cuando hay que averiguar por qué pasa algo, o ante preguntas del tipo "¿por qué esta muestra es outlier?", "¿a qué se debe esto?", "¿de dónde viene esta diferencia?". Sirve para no quedarse con la primera explicación que suena bien.
---

## Cuándo usarla

- Una muestra queda lejos del resto en el PCA y no se sabe por qué.
- Una variante nueva da un resultado que contradice lo esperado.
- Hay que decidir si algo es un problema técnico o una señal biológica.

**Caso abierto ahora mismo en el proyecto**: `F1_PIN_R1` sigue siendo la muestra más
alejada del resto con `filtro_min2` y con `filtro_min3`. El filtrado de ceros no lo
explica, así que la causa está sin identificar.

## Proceso

1. **Enunciar el hecho con números, no con adjetivos.** No "F1_PIN_R1 es raro", sino
   "F1_PIN_R1 queda en PC1=39.5 cuando el resto va de -6.6 a 17.8". Sin la magnitud no
   se puede saber después si una hipótesis alcanza para explicarlo.

2. **Listar hipótesis en tres familias, siempre las tres.** El error más común es saltar
   directo a la biología:
   - **Error del dato**: algo mal en el archivo (valores fuera de escala, columnas
     mezcladas, corrección manual previa, duplicados).
   - **Efecto técnico**: algo del laboratorio o del equipo (profundidad de la corrida,
     tanda, lote, orden de procesamiento, sensibilidad del día).
   - **Efecto del preprocesamiento**: algo que introduce el propio análisis (el z-score,
     el filtrado, los ceros tratados como valor real).
   - **Efecto biológico**: la muestra realmente es distinta.

3. **Para cada hipótesis, escribir qué evidencia la confirmaría y qué evidencia la
   descartaría**, antes de mirar los datos. Si una hipótesis no se puede descartar con
   ninguna evidencia disponible, marcarla como "no verificable acá" y decirlo.

4. **Probar primero la más barata.** Un chequeo de 5 líneas sobre la matriz antes de un
   script de investigación de 150. Si `scripts/check_matrix.py` ya responde la pregunta,
   no hace falta nada más.

5. **Anotar los descartes con la misma seriedad que los hallazgos.** "No es un problema
   de abundancia total" es un resultado valioso: cierra un camino. Los descartes de este
   proyecto ya están en `docs/analysis_notes.md` y conviene no repetirlos.

6. **Distinguir "no es" de "no sé".** Si al final la causa sigue sin identificar, decirlo
   así y dejar la pregunta abierta en `docs/design_decisions.md`. No cerrar la
   investigación con la explicación más cómoda.

7. **Chequear si la hipótesis explica la magnitud completa.** Una causa que explica un
   10% del efecto no es *la* causa. Preguntarse siempre: ¿alcanza esto para explicar todo
   lo que veo, o falta algo más?

## Qué necesito de vos

- El hecho concreto a investigar (qué muestra, qué variante, qué número).
- Cualquier información del laboratorio que no esté en `master_matrix.csv`: tandas,
  fechas, lotes, cambios de protocolo, incidentes.
- Si ya hay una sospecha, decirla — pero se va a testear como hipótesis, no asumir.

## Qué produce

- Lista de hipótesis con su estado: confirmada / descartada / no verificable / pendiente.
- Los scripts de diagnóstico que hagan falta, en `scripts/investigate_*.py`.
- Tablas y gráficos de apoyo en `results/<variante>/diagnostics/`.
- Entrada en `docs/analysis_notes.md` (4-6 líneas, lenguaje simple) con qué se investigó,
  qué se encontró y qué queda abierto.
- Si queda sin resolver: pregunta concreta y bien formulada para la directora.

## Ojo con

- **La primera explicación plausible.** Suele ser la más obvia, no la correcta. En este
  proyecto la primera sospecha sobre `P_RM_R1` y `F1_PIN_R1` fue "error de escala como
  `F1_PIN_R2`", y era falsa.
- **Confundir correlación con causa.** Que R3 detecte menos proteínas en el agregado no
  significa que la réplica sea la causa: al mirar los 9 grupos por separado el patrón se
  cumple en 2. Siempre desagregar antes de afirmar un patrón.
