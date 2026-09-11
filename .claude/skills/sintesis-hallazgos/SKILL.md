---
name: sintesis-hallazgos
description: Convertir resultados sueltos en hallazgos con significado y nivel de confianza. Usar cuando hay varias variantes o diagnósticos corridos y hay que sacar conclusiones, cuando se pide "resumir qué encontramos", "qué nos dice esto", "cuáles son las conclusiones", o antes de armar un resumen para la directora. Es el paso previo a resumen-ejecutivo.
---

## Cuándo usarla

- Hay varias variantes o diagnósticos corridos y hay que sacar una lectura general.
- Antes de la Etapa 5 (síntesis y revisión con la directora).
- Cuando `docs/analysis_notes.md` ya tiene varias entradas y hace falta unirlas.

## Proceso

1. **Separar dato de hallazgo.** Un dato dice qué pasó. Un hallazgo dice qué pasó, por
   qué (o cuál es la explicación más probable) y qué implica para el próximo paso.

   | Dato | Hallazgo |
   |---|---|
   | "P_RM_R1 detecta 697 proteínas" | "P_RM_R1 detecta 697 proteínas contra una mediana de ~100. Eso hace que el z-score la dispare y que domine PC1 en el baseline. Filtrar con `min3` la devuelve al rango normal, así que el outlier era del preprocesamiento, no biológico." |
   | "PC1+PC2 explican 46.9%" | "PC1+PC2 explican 46.9% en el baseline pero bajan a 38.6% con `min3`. La caída es esperable y buena señal: parte de ese 46.9% venía de proteínas presentes en una sola muestra." |

2. **Aplicar el test del "¿y qué?" tres veces.** Sobre cada resultado, preguntarse "¿y
   qué?" hasta llegar a algo que cambie una decisión. La tercera respuesta suele ser lo
   que vale contar. Si a la primera no se puede responder, el resultado no está listo
   para compartir.

3. **Asignar nivel de confianza a cada hallazgo**, con estas tres etiquetas y nada más
   ambiguo:
   - **Confirmado** — se verificó con evidencia directa en los datos.
   - **Probable** — la evidencia apunta ahí pero hay explicaciones alternativas abiertas.
   - **Especulación** — hipótesis razonable sin evidencia todavía.

   En este proyecto **nada es una conclusión definitiva** hasta la revisión con la
   directora (ver `CLAUDE.md`). "Confirmado" significa "confirmado dentro de este
   análisis exploratorio", no "es así".

4. **Separar lo que el análisis puede responder de lo que no.** Hay hallazgos que
   necesitan información que no está en `master_matrix.csv` (tandas, lotes, protocolo).
   Esos van a una lista aparte de preguntas para la directora, no se resuelven con más
   preprocesamiento.

5. **Ordenar por importancia, no por orden cronológico.** Primero lo que cambia cómo se
   interpreta todo el resto. La bitácora es cronológica a propósito; la síntesis no.

6. **Decir explícitamente qué NO se puede afirmar todavía.** En este proyecto, por
   ejemplo: con baseline, min2 y min3 todavía no se ve separación clara por genotipo ni
   por maduración. Eso es un resultado honesto y hay que decirlo, no esconderlo.

## Qué necesito de vos

- Qué variantes y diagnósticos considerar (o "todo lo que hay").
- Para quién es la síntesis: para vos, para la directora, o para el registro.
- Si hay alguna pregunta específica que la síntesis tiene que responder.

## Qué produce

- Lista de hallazgos ordenados por importancia, cada uno con: qué se observó, la
  explicación más probable, el nivel de confianza, y qué implica.
- Lista separada de preguntas que necesitan información del laboratorio.
- Lista explícita de lo que todavía no se puede afirmar.
- Sin conclusiones definitivas: son patrones a interpretar con cautela.

## Ojo con

- **Quedarse en lo descriptivo.** "PC1 explica 31.8%" es reporte, no análisis.
- **Sobreinterpretar patrones agregados** sin desagregar (ver el caso R1/R2/R3 en
  `docs/design_decisions.md`: parecía un patrón claro y al desagregar se cumplía en 2 de
  9 grupos).
- **Olvidar las decisiones que condicionan la lectura.** La corrección manual de
  `F1_PIN_R2` y las réplicas idénticas afectan cómo se interpreta la consistencia entre
  réplicas. Cualquier síntesis que hable de consistencia tiene que mencionarlas.
