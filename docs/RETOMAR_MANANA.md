# Para retomar — 2026-09-11

## Dónde quedó

Se cambió de paradigma: además del PCA, ahora hay un **análisis cualitativo** que mira
solo si cada proteína se detecta o no, y compara repertorios entre genotipos
(C=Caimanta, P=Pinton, F1), etapas (VM/PIN/RM) y réplicas (R1/R2/R3), con Venn,
similitud Jaccard % e intersecciones. Corrido y guardado. Etapa 2B marcada en CLAUDE.md.

## Qué abrir primero (en este orden)

1. `results/cualitativo_comparado/README.md` — todos los gráficos, las tres reglas una
   al lado de la otra. 2 minutos de mirada.
2. `results/cualitativo_comparacion_reglas.md` — qué significa lo que se ve.
3. `docs/analysis_notes.md` — última entrada, resumen corto.

## Los 3 hallazgos

1. **R3 ⊂ R2 ⊂ R1**: casi todo lo que detecta R3 lo detectan también R2 y R1, pero R1
   tiene 286 proteínas que nadie más ve. Es profundidad de corrida, no biología. Es el
   efecto más fuerte de todo el análisis.
2. **Genotipos (regla min2)**: P–F1 47.8% de similitud > C–F1 39.8% > C–P 37.5%. F1
   contiene el 82% del repertorio de Caimanta y el 63% del de Pinton. Compatible con un
   híbrido, pero débil.
3. **Etapas**: el orden de riqueza se da vuelta según la regla que se use → no se puede
   concluir nada de maduración todavía.

## Decisión pendiente

Elegir (o no) una sola regla de presencia. `min2` es la menos sesgada: `min1` está
dominado por `P_RM_R1` y `rep3` está inflado por las condiciones con réplicas idénticas.
Opción válida: no elegir y mostrar las tres, porque la inestabilidad entre reglas es
parte del resultado.

## Próximos pasos sugeridos

- Repetir el análisis cualitativo **dentro de una sola réplica** (ej. solo R1) para sacar
  del medio el efecto de profundidad y ver si queda señal de genotipo/etapa.
- Seguir con la Etapa 3 del plan (log-transform + escalado) si se quiere volver al PCA.
- Preguntas para la directora: ¿R1/R2/R3 se procesaron en tandas distintas? ¿por qué
  `P_RM_R1` y `F1_PIN_R1` detectan muchas más proteínas que el resto?

## Comandos

```
cd ~/omics-pca-analysis
.venv/bin/python scripts/run_qualitative.py --presence-rule min2   # o min1 / rep3
.venv/bin/python scripts/compare_qualitative_rules.py              # paneles comparativos
```

El entorno `.venv/` ya está armado (no había pandas en el python del sistema). Está en
`.gitignore`. Nada está commiteado todavía: `git status` muestra todo lo nuevo.
