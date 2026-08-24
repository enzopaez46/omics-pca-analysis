# CLAUDE.md — Contrato de trabajo del proyecto

## Contexto del proyecto

Este proyecto analiza datos de proteómica de tomate mediante Análisis de Componentes
Principales (PCA). El diseño experimental combina:

- **Genotipo**: C, P, F1
- **Etapa de maduración**: VM, PIN, RM
- **Réplicas biológicas**: R1, R2, R3

Esto da 27 muestras (3 x 3 x 3), nombradas como `C_VM_R1`, `C_VM_R2`, ..., `F1_RM_R3`.

El dato de partida es `data/master_matrix.csv`: 975 proteínas (filas, identificadas por
`Accession`) x 27 muestras (columnas). Los valores faltantes fueron reemplazados por 0,
lo cual **no significa abundancia biológica cero**: significa "proteína no detectada" en
esa muestra. Esto hay que tenerlo en cuenta en cualquier preprocesamiento.

**Objetivo del proyecto**: explorar si el PCA muestra patrones de variación asociados al
genotipo y/o a la maduración, y evaluar qué tan consistentes son las réplicas entre sí.

**Importante sobre el estado del proyecto**: Enzo (investigador a cargo) está aprendiendo
PCA a la vez que avanza en el análisis. Todo lo que se genera acá es exploratorio hasta
que se revise con la directora del proyecto. Ningún resultado debe presentarse como
conclusión definitiva — son patrones a interpretar con cautela.

## Reglas de trabajo para Claude Code

1. **Nunca modificar `data/master_matrix.csv`.** Es el dato fuente y no se toca.

2. **Cada corrida de PCA es una "variante".** Una variante es una combinación concreta
   de decisiones de preprocesamiento (qué se hace con los ceros, si se escala o
   transforma, si se filtran proteínas) más el script que la genera. No crear scripts
   sueltos tipo `pca_final_v2_real.py`. Cada variante tiene su propia carpeta en
   `results/<nombre_variante>/` y, si el script cambia respecto a otra variante, se
   documenta la diferencia en 1-2 líneas.

3. **Antes de programar una variante nueva**, explicar en 2-3 líneas qué se va a probar
   y por qué, en la conversación misma (no hace falta un documento aparte).

4. **Cada corrida debe guardar en su carpeta de resultados**:
   - Gráfico PC1 vs PC2 (y PC1 vs PC3 si aporta algo), coloreado por genotipo y con
     forma distinta por etapa de maduración.
   - Tabla de % de varianza explicada por componente.
   - Tabla de coordenadas de las muestras (scores).
   - Si es relevante para esa variante, proteínas con mayor contribución a PC1/PC2
     (loadings).

5. **Después de cada corrida**, agregar una entrada corta (4-6 líneas, lenguaje simple,
   sin jerga estadística innecesaria) en `docs/analysis_notes.md`: qué se corrió, qué se
   observó, y una duda o hipótesis para seguir. No hace falta detallar el código ahí.

6. **Decisiones técnicas no triviales** (ej. cómo tratar los ceros, si escalar o no,
   si filtrar proteínas) se explican con 2-3 alternativas en términos simples y se
   espera la decisión de Enzo antes de asumir una por defecto — salvo que ya esté
   acordada en este archivo o en `docs/design_decisions.md`.

7. **Herramientas**: Python (pandas, numpy, scikit-learn, matplotlib/seaborn), salvo que
   se acuerde otra cosa. Mantener `requirements.txt` actualizado si se agrega una
   librería nueva.

8. **Avisar siempre antes de sobrescribir** resultados de una variante ya generada.

## Estructura del proyecto

```
omics-pca-analysis/
├── data/
│   └── master_matrix.csv        # dato fuente, no se modifica
├── scripts/
│   ├── run_pca.py               # script principal, parametrizable por variante
│   └── utils.py                 # funciones compartidas (si hacen falta)
├── results/
│   ├── baseline/
│   │   ├── figures/
│   │   └── tables/
│   └── <variant_XX>/
│       ├── figures/
│       └── tables/
├── docs/
│   ├── PLAN_ETAPAS.md           # hoja de ruta del análisis
│   ├── analysis_notes.md        # bitácora simple, una entrada por corrida
│   └── design_decisions.md      # decisiones técnicas acordadas (opcional, crece con el proyecto)
├── CLAUDE.md
├── README.md
└── requirements.txt
```

## Estado actual

- [x] Etapa 0 — Setup del proyecto
- [x] Etapa 1 — PCA baseline
- [x] Etapa 2 — Variante: tratamiento de ceros
- [ ] Etapa 3 — Variante: transformación/escalado
- [ ] Etapa 4 — Contribución de proteínas (loadings)
- [ ] Etapa 5 — Síntesis y revisión con la directora

(Ver el detalle de cada etapa en `docs/PLAN_ETAPAS.md`. Marcar acá cuando se completen.)
