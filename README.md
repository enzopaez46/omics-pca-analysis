# omics-pca-analysis

Análisis exploratorio por PCA (Análisis de Componentes Principales) de datos de
proteómica de tomate. El diseño experimental combina genotipo (C, P, F1), etapa de
maduración (VM, PIN, RM) y réplicas biológicas (R1-R3), dando 27 muestras.

El dato de partida es `data/master_matrix.csv` (975 proteínas x 27 muestras) y **no se
modifica**. El objetivo es explorar si el PCA muestra patrones asociados al genotipo
y/o a la maduración, y qué tan consistentes son las réplicas entre sí.

Cada corrida de PCA es una "variante" (una combinación de decisiones de
preprocesamiento) documentada en su propia carpeta bajo `results/`. Este proyecto es
exploratorio: los resultados son patrones a interpretar con cautela, no conclusiones
definitivas.

Ver `CLAUDE.md` para las reglas de trabajo y `docs/PLAN_ETAPAS.md` para la hoja de ruta.
