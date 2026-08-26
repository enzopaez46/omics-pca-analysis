# Comparación: 27 columnas vs 23 mediciones independientes

Generado por `scripts/compare_sample_sets.py`. Pregunta: ¿cuánto cambia el PCA si se excluyen las columnas que son duplicado exacto de otra?

Columnas excluidas (4): `C_VM_R3`, `F1_VM_R2`, `F1_VM_R3`, `F1_RM_R3`

## Varianza explicada

| component | varianza_27_muestras_pct | varianza_23_muestras_pct |
|-----------|--------------------------|--------------------------|
| PC1       | 31.82                    | 31.87                    |
| PC2       | 15.06                    | 15.32                    |
| PC3       | 11.14                    | 11.35                    |
| PC4       | 8.41                     | 8.66                     |
| PC5       | 6.23                     | 5.54                     |
| PC6       | 4.70                     | 4.86                     |

## ¿Se conserva el orden de las muestras?

Correlación de la posición de las 23 muestras comunes entre las dos corridas. Cerca de 1 (en valor absoluto) significa que las dos corridas ordenan las muestras igual.

| component | correlacion | correlacion_abs | signo_invertido |
|-----------|-------------|-----------------|-----------------|
| PC1       | 0.9998      | 0.9998          | False           |
| PC2       | 0.9977      | 0.9977          | False           |
| PC3       | 0.9990      | 0.9990          | False           |

## Dispersión entre réplicas por condición

Distancia promedio entre las réplicas de una misma condición, en el plano PC1-PC2. Una dispersión de 0 con 2 o 3 muestras significa réplicas idénticas: consistencia aparente que no es evidencia biológica. `NaN` significa que no quedó más de una muestra en esa condición, así que no se puede medir consistencia.

| condicion | n_muestras_27 | dispersion_27 | n_muestras_23 | dispersion_23 |
|-----------|---------------|---------------|---------------|---------------|
| C_VM      | 3             | 0.987         | 2             | 1.361         |
| C_PIN     | 3             | 1.237         | 3             | 1.318         |
| C_RM      | 3             | 11.105        | 3             | 10.542        |
| P_VM      | 3             | 0.225         | 3             | 0.340         |
| P_PIN     | 3             | 23.564        | 3             | 21.521        |
| P_RM      | 3             | 62.216        | 3             | 57.941        |
| F1_VM     | 3             | 0.000         | 1             | n/d           |
| F1_PIN    | 3             | 32.650        | 3             | 31.112        |
| F1_RM     | 3             | 0.197         | 2             | 0.286         |

## Proyección de las duplicadas

Las columnas duplicadas proyectadas en el espacio del PCA de 23 muestras, comparadas contra su gemela conservada. Distancia 0 = la columna duplicada cae exactamente sobre su gemela, o sea que no aporta información nueva.

| muestra_duplicada | gemela_conservada | PC1_proyectado | PC1_gemela | distancia_PC1_PC2 |
|-------------------|-------------------|----------------|------------|-------------------|
| C_VM_R3           | C_VM_R2           | -4.608570      | -4.608570  | 0.000000          |
| F1_VM_R2          | F1_VM_R1          | -4.232162      | -4.232162  | 0.000000          |
| F1_VM_R3          | F1_VM_R1          | -4.232162      | -4.232162  | 0.000000          |
| F1_RM_R3          | F1_RM_R2          | -6.329912      | -6.329912  | 0.000000          |

## Figuras

- `comparacion_27_vs_23/figures/lado_a_lado.png` — los dos PCA en paneles separados.
- `comparacion_27_vs_23/figures/proyeccion_duplicadas.png` — todo en un mismo espacio.
