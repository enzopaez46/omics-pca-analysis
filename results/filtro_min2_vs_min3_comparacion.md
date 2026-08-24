# Comparación: baseline vs filtro_min2 vs filtro_min3

Etapa 2 del plan — efecto de filtrar proteínas poco detectadas antes del PCA.
Todas las corridas usan el mismo preprocesamiento (ceros sin tratar, estandarización
z-score); la única diferencia es cuántas proteínas se excluyen antes de transponer.

## Cuántas proteínas quedaron

| Variante     | Umbral                        | Proteínas usadas | % del total (975) |
|--------------|--------------------------------|-------------------|---------------------|
| baseline     | ninguno (Etapa 1)              | 975               | 100%                |
| filtro_min2  | detectada en ≥2 de 27 muestras | 639               | 66%                 |
| filtro_min3  | detectada en ≥3 de 27 muestras | 443               | 45%                 |

## % de varianza explicada

| Variante     | PC1    | PC2    | PC1+PC2 |
|--------------|--------|--------|---------|
| baseline     | 31.8%  | 15.1%  | 46.9%   |
| filtro_min2  | 24.8%  | 16.0%  | 40.8%   |
| filtro_min3  | 25.4%  | 13.2%  | 38.6%   |

Filtrar baja un poco el % que explican PC1+PC2. Tiene sentido: al sacar proteínas que
solo "existían" en una muestra, se saca variación que antes engordaba artificialmente
un componente.

## Dónde queda cada outlier sospechoso

| Variante     | P_RM_R1 (PC1, PC2)    | F1_PIN_R1 (PC1, PC2)  | Rango normal del resto (PC1 / PC2) |
|--------------|------------------------|-------------------------|--------------------------------------|
| baseline     | (86.1, -13.0) — outlier extremo en PC1, solo | (4.9, 47.7) — outlier extremo en PC2, solo | -5.9 a ~17 / -13 a ~22 |
| filtro_min2  | (22.2, 28.2) — sigue destacándose, ahora en PC2 | (44.5, -27.3) — pasa a ser el más extremo en PC1 | -7.1 a 44.5 / -27.3 a 28.2 |
| filtro_min3  | (14.0, -0.5) — **ya no es outlier**, cae dentro del rango normal | (39.5, -0.6) — sigue siendo claramente el más alto en PC1 | -6.6 a 39.5 / -6.3 a 17.8 |

## Lectura

- **P_RM_R1** deja de ser un outlier extremo con el filtro más estricto
  (`min_samples_detected=3`): pasa de estar 15x más lejos que cualquier otra muestra
  en el baseline a quedar dentro del rango normal de variación. Con `min2` mejora
  parcialmente pero todavía se distingue del resto. Esto confirma la hipótesis del
  diagnóstico anterior: su posición extrema en el baseline se debía en buena parte a
  proteínas detectadas casi solo en esa muestra, y filtrarlas resuelve el problema.

- **F1_PIN_R1** sigue siendo la muestra más alejada del resto en las dos variantes
  filtradas (ahora concentrado en PC1). Filtrar ayudó a P_RM_R1 pero no a esta
  muestra — su comportamiento parece tener otra causa, que todavía no investigamos en
  detalle.

- Con ninguna de las tres variantes se ve todavía una separación clara por genotipo o
  por maduración: la mayoría de las muestras siguen amontonadas juntas y lo que más
  se nota en los gráficos sigue siendo la posición de unas pocas muestras puntuales,
  no un patrón de grupos.

- Entre `min2` y `min3`, `min3` da un resultado más limpio (resuelve el outlier de
  P_RM_R1) sacando más proteínas (532 excluidas en total, contra 336 en `min2`). No
  hay una diferencia enorme entre ambos umbrales en cuanto al panorama general — ver
  figuras en
  `results/filtro_min2/figures/pca_pc1_pc2.png` y
  `results/filtro_min3/figures/pca_pc1_pc2.png` para la comparación visual.
