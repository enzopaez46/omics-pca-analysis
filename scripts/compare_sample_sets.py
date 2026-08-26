"""
compare_sample_sets.py — diagnóstico puntual, no es una variante nueva de PCA.

Pregunta a responder: ¿cuánto cambia el PCA si se corre solo sobre las mediciones
independientes (23 muestras) en vez de sobre las 27 columnas del archivo?

De las 27 columnas de master_matrix.csv, 4 son duplicado exacto de otra columna
(C_VM_R3, F1_VM_R2, F1_VM_R3, F1_RM_R3 — ver docs/design_decisions.md). No son
mediciones nuevas: son la misma medición repetida. Este script compara las dos
corridas y cuantifica qué cambia y qué no.

Cómo compara (esto es lo importante, porque comparar dos PCA distintos tiene trampa):

1. **Varianza explicada**: se compara componente por componente. Comparación directa.

2. **Correlación de coordenadas**: para las 23 muestras que están en las dos corridas,
   se correlaciona su posición en PC1 (y en PC2). Si la correlación es cercana a +/-1,
   las dos corridas ordenan las muestras igual, o sea que la estructura se conserva.
   El signo de un eje de PCA es arbitrario (dar vuelta PC1 es la misma solución
   matemática), así que se alinea el signo antes de comparar y de graficar.

3. **Proyección**: se ajusta el PCA sobre las 23 muestras y después se PROYECTAN las 4
   duplicadas en ese mismo espacio (`pca.transform`). Esto es lo que permite ver las
   dos cosas "una al lado de la otra" de verdad: mismos ejes, misma escala. Si una
   muestra duplicada cae exactamente sobre su gemela, queda demostrado que no aporta
   ninguna información nueva.

4. **Dispersión entre réplicas**: para cada condición (genotipo+etapa) se calcula la
   distancia promedio entre sus réplicas en el plano PC1-PC2. Es la forma de medir la
   afirmación "las réplicas idénticas hacen que la consistencia se vea artificialmente
   perfecta": en la corrida de 27 esas condiciones tienen dispersión 0 por construcción.

No modifica data/master_matrix.csv ni ningún resultado ya generado. Todo lo nuevo va a
results/comparacion_27_vs_23/.

Uso (desde la raíz del proyecto):
    python scripts/compare_sample_sets.py
"""

import itertools
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import run_pca

OUT_DIR = "results/comparacion_27_vs_23"
SUMMARY_PATH = "results/comparacion_27_vs_23.md"
N_COMPONENTES_TABLA = 6


def preparar(df_crudo):
    """
    Aplica el mismo preprocesamiento que el baseline (transponer + estandarizar por
    proteína) pero devolviendo también el scaler y el objeto PCA, que run_pca.py no
    expone porque no le hacían falta.

    Se replican los pasos de run_pca.handle_zeros y run_pca.scale_data a propósito:
    hacen falta los objetos intermedios para poder proyectar muestras nuevas después.
    """
    df_t = df_crudo.T
    df_t = run_pca.handle_zeros(df_t, run_pca.ZERO_HANDLING)

    scaler = StandardScaler()
    escalado = scaler.fit_transform(df_t)

    pca = PCA()
    scores = pca.fit_transform(escalado)

    columnas = [f"PC{i+1}" for i in range(scores.shape[1])]
    scores_df = pd.DataFrame(scores, index=df_t.index, columns=columnas)

    return scores_df, pca, scaler, df_t.columns


def metadata_de(nombres):
    """De ['C_VM_R1', ...] saca genotipo, etapa y réplica."""
    partes = [str(n).split("_") for n in nombres]
    return pd.DataFrame(
        {
            "genotype": [p[0] for p in partes],
            "stage": [p[1] for p in partes],
            "replicate": [p[2] for p in partes],
        },
        index=nombres,
    )


def alinear_signo(serie_referencia, serie_a_alinear):
    """
    Da vuelta el signo de un eje si eso mejora la correlación con la referencia.

    Dar vuelta un eje de PCA no cambia nada matemáticamente (es la misma
    descomposición), pero sí cambia cómo se ve el gráfico. Alinear los signos es
    necesario para poder comparar visualmente dos corridas.

    Devuelve (serie_alineada, se_dio_vuelta).
    """
    comunes = serie_referencia.index.intersection(serie_a_alinear.index)
    r = np.corrcoef(serie_referencia[comunes], serie_a_alinear[comunes])[0, 1]
    if r < 0:
        return -serie_a_alinear, True
    return serie_a_alinear, False


def tabla_varianza(pca_27, pca_23):
    """Compara el % de varianza explicada componente por componente."""
    n = min(N_COMPONENTES_TABLA, len(pca_27.explained_variance_ratio_),
            len(pca_23.explained_variance_ratio_))
    return pd.DataFrame({
        "component": [f"PC{i+1}" for i in range(n)],
        "varianza_27_muestras_pct": pca_27.explained_variance_ratio_[:n] * 100,
        "varianza_23_muestras_pct": pca_23.explained_variance_ratio_[:n] * 100,
    })


def tabla_correlacion(scores_27, scores_23, comunes):
    """
    Para cada componente, correlaciona la posición de las 23 muestras comunes en las
    dos corridas. Cerca de 1 significa que las dos corridas ordenan igual las muestras.
    """
    filas = []
    for pc in ["PC1", "PC2", "PC3"]:
        a = scores_27.loc[comunes, pc]
        b = scores_23.loc[comunes, pc]
        r = np.corrcoef(a, b)[0, 1]
        filas.append({
            "component": pc,
            "correlacion": r,
            "correlacion_abs": abs(r),
            "signo_invertido": bool(r < 0),
        })
    return pd.DataFrame(filas)


def tabla_dispersion(scores_27, scores_23):
    """
    Distancia promedio entre las réplicas de cada condición, en el plano PC1-PC2.

    Es la medida concreta de "consistencia entre réplicas". Una condición cuyas
    réplicas son idénticas tiene dispersión exactamente 0 en la corrida de 27, y eso
    no es evidencia biológica: es el mismo dato repetido.
    """
    def dispersion(scores, muestras):
        if len(muestras) < 2:
            return np.nan
        puntos = scores.loc[muestras, ["PC1", "PC2"]].to_numpy()
        distancias = [
            float(np.linalg.norm(a - b))
            for a, b in itertools.combinations(puntos, 2)
        ]
        return float(np.mean(distancias))

    meta_27 = metadata_de(list(scores_27.index))
    meta_23 = metadata_de(list(scores_23.index))

    filas = []
    for (genotipo, etapa), grupo in meta_27.groupby(["genotype", "stage"], sort=False):
        muestras_27 = list(grupo.index)
        muestras_23 = [m for m in muestras_27 if m in meta_23.index]
        filas.append({
            "condicion": f"{genotipo}_{etapa}",
            "n_muestras_27": len(muestras_27),
            "dispersion_27": dispersion(scores_27, muestras_27),
            "n_muestras_23": len(muestras_23),
            "dispersion_23": dispersion(scores_23, muestras_23),
        })
    return pd.DataFrame(filas)


def tabla_proyeccion(df_crudo, duplicadas, pca_23, scaler_23, proteinas_23, scores_23):
    """
    Proyecta las muestras duplicadas en el espacio del PCA de 23 y las compara contra
    la muestra que las representa (su "gemela" conservada).

    Si la distancia es 0, la muestra duplicada cae exactamente sobre su gemela: aporta
    cero información nueva al PCA. Es la demostración numérica de por qué se pueden
    excluir sin perder nada.
    """
    if not duplicadas:
        return pd.DataFrame(), pd.DataFrame()

    bloque = df_crudo[duplicadas].T[proteinas_23]
    escalado = scaler_23.transform(bloque)
    proyectado = pca_23.transform(escalado)
    columnas = [f"PC{i+1}" for i in range(proyectado.shape[1])]
    proy_df = pd.DataFrame(proyectado, index=duplicadas, columns=columnas)

    filas = []
    for muestra in duplicadas:
        # La gemela es la muestra conservada con valores idénticos.
        gemela = next(
            (m for m in scores_23.index if df_crudo[m].equals(df_crudo[muestra])),
            None,
        )
        if gemela is None:
            filas.append({
                "muestra_duplicada": muestra, "gemela_conservada": "(ninguna)",
                "PC1_proyectado": proy_df.loc[muestra, "PC1"],
                "PC1_gemela": np.nan, "distancia_PC1_PC2": np.nan,
            })
            continue
        d = float(np.linalg.norm(
            proy_df.loc[muestra, ["PC1", "PC2"]].to_numpy()
            - scores_23.loc[gemela, ["PC1", "PC2"]].to_numpy()
        ))
        filas.append({
            "muestra_duplicada": muestra,
            "gemela_conservada": gemela,
            "PC1_proyectado": float(proy_df.loc[muestra, "PC1"]),
            "PC1_gemela": float(scores_23.loc[gemela, "PC1"]),
            "distancia_PC1_PC2": d,
        })

    return proy_df, pd.DataFrame(filas)


def figura_lado_a_lado(scores_27, pca_27, scores_23, pca_23, ruta):
    """
    Dos paneles con la misma escala de ejes: 27 columnas contra 23 mediciones
    independientes. Sirve para ver si la forma general de la nube cambia.

    Ojo: los ejes de los dos paneles NO son el mismo eje. Son dos PCA distintos. Se
    pueden comparar cualitativamente (¿se agrupan igual?), no coordenada por coordenada.
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharex=True, sharey=True)

    for ax, (scores, pca, titulo) in zip(axes, [
        (scores_27, pca_27, f"27 columnas del archivo (incluye 4 duplicadas)"),
        (scores_23, pca_23, f"23 mediciones independientes"),
    ]):
        datos = scores[["PC1", "PC2"]].join(metadata_de(list(scores.index)))
        sns.scatterplot(
            data=datos, x="PC1", y="PC2", hue="genotype", style="stage",
            s=130, ax=ax, legend=(ax is axes[1]),
        )
        v1 = pca.explained_variance_ratio_[0] * 100
        v2 = pca.explained_variance_ratio_[1] * 100
        ax.set_xlabel(f"PC1 ({v1:.1f}% varianza explicada)")
        ax.set_ylabel(f"PC2 ({v2:.1f}% varianza explicada)")
        ax.set_title(f"{titulo}  —  n={scores.shape[0]}")
        ax.axhline(0, color="grey", linewidth=0.5, zorder=0)
        ax.axvline(0, color="grey", linewidth=0.5, zorder=0)

    axes[1].legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    fig.suptitle(
        "PCA con todas las columnas vs. solo mediciones independientes\n"
        "(los ejes de cada panel son de su propio PCA: comparar la forma, no las coordenadas)",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


def figura_proyeccion(scores_23, pca_23, proy_df, ruta):
    """
    Un solo gráfico, un solo espacio: el PCA ajustado sobre las 23 mediciones
    independientes, con las 4 duplicadas proyectadas encima (marcador hueco).

    Acá sí los ejes son los mismos para todas las muestras, así que las posiciones son
    directamente comparables. Es la forma correcta de poner las dos cosas "una al lado
    de la otra".
    """
    fig, ax = plt.subplots(figsize=(9, 7))

    datos = scores_23[["PC1", "PC2"]].join(metadata_de(list(scores_23.index)))
    sns.scatterplot(
        data=datos, x="PC1", y="PC2", hue="genotype", style="stage", s=140, ax=ax,
    )

    if not proy_df.empty:
        ax.scatter(
            proy_df["PC1"], proy_df["PC2"],
            s=320, facecolors="none", edgecolors="red", linewidths=2.0,
            label="duplicadas (proyectadas)", zorder=5,
        )
        for muestra in proy_df.index:
            ax.annotate(
                muestra,
                (proy_df.loc[muestra, "PC1"], proy_df.loc[muestra, "PC2"]),
                textcoords="offset points", xytext=(10, 6),
                fontsize=8, color="red",
            )

    v1 = pca_23.explained_variance_ratio_[0] * 100
    v2 = pca_23.explained_variance_ratio_[1] * 100
    ax.set_xlabel(f"PC1 ({v1:.1f}% varianza explicada)")
    ax.set_ylabel(f"PC2 ({v2:.1f}% varianza explicada)")
    ax.set_title(
        "PCA ajustado sobre 23 mediciones independientes,\n"
        "con las 4 columnas duplicadas proyectadas en el mismo espacio"
    )
    ax.axhline(0, color="grey", linewidth=0.5, zorder=0)
    ax.axvline(0, color="grey", linewidth=0.5, zorder=0)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


def a_markdown(tabla, decimales=3):
    """
    Convierte un DataFrame en una tabla Markdown.

    Se hace a mano en vez de usar df.to_markdown() porque eso requiere la librería
    `tabulate`, y el proyecto mantiene las dependencias al mínimo (pandas, numpy,
    scikit-learn, matplotlib, seaborn).
    """
    def fmt(v):
        if isinstance(v, float):
            if np.isnan(v):
                return "n/d"
            return f"{v:.{decimales}f}"
        return str(v)

    columnas = list(tabla.columns)
    filas = [[fmt(v) for v in fila] for fila in tabla.to_numpy()]

    anchos = [
        max(len(str(col)), *(len(f[i]) for f in filas)) if filas else len(str(col))
        for i, col in enumerate(columnas)
    ]

    lineas = [
        "| " + " | ".join(str(c).ljust(anchos[i]) for i, c in enumerate(columnas)) + " |",
        "|" + "|".join("-" * (a + 2) for a in anchos) + "|",
    ]
    for fila in filas:
        lineas.append("| " + " | ".join(v.ljust(anchos[i]) for i, v in enumerate(fila)) + " |")
    return "\n".join(lineas)


def escribir_resumen(varianza, correlacion, dispersion, proyeccion, duplicadas):
    """Resumen en Markdown, siguiendo el formato de la comparación de la Etapa 2."""
    lineas = []
    lineas.append("# Comparación: 27 columnas vs 23 mediciones independientes\n")
    lineas.append(
        "Generado por `scripts/compare_sample_sets.py`. Pregunta: ¿cuánto cambia el "
        "PCA si se excluyen las columnas que son duplicado exacto de otra?\n"
    )
    lineas.append(f"Columnas excluidas ({len(duplicadas)}): "
                  + ", ".join(f"`{d}`" for d in duplicadas) + "\n")

    lineas.append("## Varianza explicada\n")
    lineas.append(a_markdown(varianza, 2) + "\n")

    lineas.append("## ¿Se conserva el orden de las muestras?\n")
    lineas.append(
        "Correlación de la posición de las 23 muestras comunes entre las dos corridas. "
        "Cerca de 1 (en valor absoluto) significa que las dos corridas ordenan las "
        "muestras igual.\n"
    )
    lineas.append(a_markdown(correlacion, 4) + "\n")

    lineas.append("## Dispersión entre réplicas por condición\n")
    lineas.append(
        "Distancia promedio entre las réplicas de una misma condición, en el plano "
        "PC1-PC2. Una dispersión de 0 con 2 o 3 muestras significa réplicas idénticas: "
        "consistencia aparente que no es evidencia biológica. `NaN` significa que no "
        "quedó más de una muestra en esa condición, así que no se puede medir "
        "consistencia.\n"
    )
    lineas.append(a_markdown(dispersion, 3) + "\n")

    lineas.append("## Proyección de las duplicadas\n")
    lineas.append(
        "Las columnas duplicadas proyectadas en el espacio del PCA de 23 muestras, "
        "comparadas contra su gemela conservada. Distancia 0 = la columna duplicada "
        "cae exactamente sobre su gemela, o sea que no aporta información nueva.\n"
    )
    lineas.append(a_markdown(proyeccion, 6) + "\n")

    lineas.append("## Figuras\n")
    lineas.append("- `comparacion_27_vs_23/figures/lado_a_lado.png` — los dos PCA en paneles separados.")
    lineas.append("- `comparacion_27_vs_23/figures/proyeccion_duplicadas.png` — todo en un mismo espacio.\n")

    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))


def main():
    figures_dir = os.path.join(OUT_DIR, "figures")
    tables_dir = os.path.join(OUT_DIR, "tables")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)

    df_crudo = pd.read_csv(run_pca.DATA_PATH, index_col="Accession")
    duplicadas = run_pca.find_duplicate_samples(df_crudo)
    print(f"Columnas duplicadas detectadas ({len(duplicadas)}): {duplicadas}")

    # Corrida A: las 27 columnas, igual que el baseline.
    scores_27, pca_27, _scaler_27, _prot_27 = preparar(df_crudo)

    # Corrida B: solo las mediciones independientes.
    df_23 = df_crudo.drop(columns=duplicadas)
    scores_23, pca_23, scaler_23, prot_23 = preparar(df_23)

    comunes = [m for m in scores_23.index if m in scores_27.index]

    # Alinear los signos de los ejes para poder comparar y graficar.
    for pc in ["PC1", "PC2", "PC3"]:
        alineado, invertido = alinear_signo(scores_27[pc], scores_23[pc])
        scores_23[pc] = alineado
        if invertido:
            print(f"  (se dio vuelta el signo de {pc} de la corrida de 23 para alinear)")

    varianza = tabla_varianza(pca_27, pca_23)
    correlacion = tabla_correlacion(scores_27, scores_23, comunes)
    dispersion = tabla_dispersion(scores_27, scores_23)

    proy_df, proyeccion = tabla_proyeccion(
        df_crudo, duplicadas, pca_23, scaler_23, prot_23, scores_23
    )
    # El signo de los ejes de scores_23 se alineó arriba; la proyección se calculó con
    # el pca original, así que hay que aplicarle el mismo criterio para que sean
    # comparables en el gráfico.
    if not proy_df.empty:
        for pc in ["PC1", "PC2", "PC3"]:
            a = scores_23.loc[comunes, pc]
            b = pd.Series(
                pca_23.transform(scaler_23.transform(df_23[comunes].T[prot_23]))[
                    :, int(pc[2:]) - 1
                ],
                index=comunes,
            )
            if np.corrcoef(a, b)[0, 1] < 0:
                proy_df[pc] = -proy_df[pc]

    varianza.to_csv(os.path.join(tables_dir, "comparacion_varianza.csv"), index=False)
    correlacion.to_csv(os.path.join(tables_dir, "correlacion_coordenadas.csv"), index=False)
    dispersion.to_csv(os.path.join(tables_dir, "dispersion_replicas.csv"), index=False)
    if not proyeccion.empty:
        proyeccion.to_csv(
            os.path.join(tables_dir, "proyeccion_duplicadas.csv"), index=False
        )

    figura_lado_a_lado(
        scores_27, pca_27, scores_23, pca_23,
        os.path.join(figures_dir, "lado_a_lado.png"),
    )
    figura_proyeccion(
        scores_23, pca_23, proy_df,
        os.path.join(figures_dir, "proyeccion_duplicadas.png"),
    )

    escribir_resumen(varianza, correlacion, dispersion, proyeccion, duplicadas)

    print("\n--- Varianza explicada ---")
    print(varianza.to_string(index=False))
    print("\n--- Correlacion de coordenadas (23 muestras comunes) ---")
    print(correlacion.to_string(index=False))
    print("\n--- Dispersion entre replicas por condicion ---")
    print(dispersion.to_string(index=False))
    if not proyeccion.empty:
        print("\n--- Proyeccion de las duplicadas ---")
        print(proyeccion.to_string(index=False))
    print(f"\nListo. Resultados en {OUT_DIR}/ y resumen en {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
