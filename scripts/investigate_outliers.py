"""
investigate_outliers.py — diagnóstico puntual, no es una variante nueva de PCA.

Objetivo: entender por qué las muestras P_RM_R1 y F1_PIN_R1 aparecen tan lejos del
resto en el gráfico del baseline (results/baseline/pca_pc1_pc2.png). La sospecha es
que se trata de algo parecido al problema de escala que ya encontramos en F1_PIN_R2
(ver docs/design_decisions.md): unos pocos valores de proteínas fuera de rango que
arrastran todo el PCA.

Este script NO modifica data/master_matrix.csv ni los resultados ya guardados en
results/baseline/. Solo lee esos datos, calcula cosas nuevas, y guarda todo aparte en
results/baseline/diagnostics/.

Para cada muestra sospechosa se hacen 3 cosas:
1. Comparar, proteína por proteína, su valor contra el promedio de las otras dos
   réplicas de la misma condición (misma combinación genotipo+etapa). Las proteínas
   con mayor diferencia son las "sospechosas" de esa muestra.
2. Marcar si esas proteínas sospechosas tienen un valor anormalmente alto en toda la
   matriz (por encima del percentil 99 de TODOS los valores), que es la misma señal
   que delató el problema de F1_PIN_R2.
3. Comparar esas proteínas sospechosas contra las que más "pesan" en PC1 y PC2 (los
   loadings del PCA baseline), para confirmar si son las mismas proteínas las que
   arrastran el resultado del PCA.
"""

import os

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

# Reutilizamos las funciones de preprocesamiento del baseline para que el PCA que
# recalculamos acá (necesario para sacar los loadings, que el script del baseline no
# guarda) sea exactamente el mismo que el que generó los resultados en
# results/baseline/.
import run_pca

OUT_DIR = "results/baseline/diagnostics"

# Para cada muestra sospechosa, indicamos cuáles son las otras dos réplicas de su
# misma condición (mismo genotipo + misma etapa de maduración).
TARGET_SAMPLES = {
    "P_RM_R1": ("P_RM_R2", "P_RM_R3"),
    "F1_PIN_R1": ("F1_PIN_R2", "F1_PIN_R3"),
}

N_TOP = 15  # cuántas proteínas listar en cada tabla


def load_raw_matrix():
    """
    Carga master_matrix.csv tal cual está (proteínas en filas, muestras en columnas),
    sin transponer. Para este diagnóstico conviene tenerla así porque comparamos
    columnas (muestras) entre sí, proteína por proteína.
    """
    return pd.read_csv(run_pca.DATA_PATH, index_col="Accession")


def matrix_percentile_99(raw_df):
    """
    Calcula el percentil 99 de todos los valores de la matriz completa (975
    proteínas x 27 muestras, ceros incluidos). Sirve como referencia de "qué es un
    valor raramente alto" en este dataset: si una proteína sospechosa supera este
    umbral, es la misma señal de alerta que delató el problema de escala de
    F1_PIN_R2.
    """
    return np.percentile(raw_df.values.flatten(), 99)


def diff_vs_other_replicates(raw_df, outlier_sample, other_samples, p99):
    """
    Para una muestra sospechosa, calcula por cada proteína:
        diferencia = valor de la muestra sospechosa - promedio de las otras 2 réplicas

    Devuelve las N_TOP proteínas con mayor diferencia en valor absoluto, junto con los
    valores crudos de las 3 réplicas y si el valor de la muestra sospechosa está por
    encima del percentil 99 de toda la matriz.
    """
    outlier_values = raw_df[outlier_sample]
    other_mean = raw_df[list(other_samples)].mean(axis=1)

    table = raw_df[[outlier_sample] + list(other_samples)].copy()
    table["diff_vs_other_mean"] = outlier_values - other_mean
    table["abs_diff"] = table["diff_vs_other_mean"].abs()

    # Nos quedamos con las proteínas donde más se aleja la muestra sospechosa.
    top = table.sort_values("abs_diff", ascending=False).head(N_TOP).copy()

    top["matrix_p99"] = p99
    top["over_p99"] = top[outlier_sample] > p99

    top.index.name = "Accession"
    return top.reset_index()


def fit_baseline_pca():
    """
    Recalcula el PCA del baseline (mismos pasos que scripts/run_pca.py: transponer,
    tratar ceros, estandarizar) para poder acceder a pca.components_ (los loadings),
    que el script del baseline no guarda porque no hacían falta para esa entrega.

    Como se usan las mismas funciones y la misma configuración, este PCA es idéntico
    al que generó los resultados en results/baseline/ — no es un PCA nuevo ni una
    variante distinta.
    """
    df = run_pca.load_and_transpose(run_pca.DATA_PATH)
    df = run_pca.handle_zeros(df, run_pca.ZERO_HANDLING)
    df_scaled = run_pca.scale_data(df, run_pca.SCALING)

    pca = PCA()
    pca.fit(df_scaled)

    return pca, df_scaled.columns  # columns = nombres de proteínas, en orden


def top_loadings(pca, protein_names, component_index, component_label):
    """
    Los "loadings" de un componente indican cuánto pesa cada proteína en ese
    componente: valores grandes (en valor absoluto, positivos o negativos) significan
    que esa proteína influye mucho en cómo se calcula ese eje del PCA.

    Devuelve las N_TOP proteínas con mayor loading absoluto para el componente pedido
    (PC1 = component_index 0, PC2 = component_index 1).
    """
    loadings = pca.components_[component_index]
    table = pd.DataFrame({
        "Accession": protein_names,
        component_label: loadings,
    })
    table["abs_loading"] = table[component_label].abs()
    top = table.sort_values("abs_loading", ascending=False).head(N_TOP).copy()
    return top.drop(columns="abs_loading").reset_index(drop=True)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    raw_df = load_raw_matrix()
    p99 = matrix_percentile_99(raw_df)

    # --- Loadings del PCA baseline (para el punto de "coinciden con el PCA") ---
    pca, protein_names = fit_baseline_pca()
    loadings_pc1 = top_loadings(pca, protein_names, 0, "loading_PC1")
    loadings_pc2 = top_loadings(pca, protein_names, 1, "loading_PC2")

    loadings_pc1_set = set(loadings_pc1["Accession"])
    loadings_pc2_set = set(loadings_pc2["Accession"])

    # --- Diagnóstico por muestra sospechosa ---
    outlier_diff_sets = {}
    for outlier_sample, other_samples in TARGET_SAMPLES.items():
        diff_table = diff_vs_other_replicates(raw_df, outlier_sample, other_samples, p99)

        # Marcamos si cada proteína sospechosa también está entre las que más pesan
        # en PC1 y/o PC2, para ver si son las mismas proteínas las que arrastran el
        # resultado del PCA.
        diff_table["in_top15_loadings_PC1"] = diff_table["Accession"].isin(loadings_pc1_set)
        diff_table["in_top15_loadings_PC2"] = diff_table["Accession"].isin(loadings_pc2_set)

        out_path = os.path.join(OUT_DIR, f"outlier_{outlier_sample}.csv")
        diff_table.to_csv(out_path, index=False)

        outlier_diff_sets[outlier_sample] = set(diff_table["Accession"])

    # Cruzamos también en el otro sentido: para cada proteína top en los loadings,
    # marcamos si aparece entre las sospechosas de cada muestra.
    for sample_name, protein_set in outlier_diff_sets.items():
        col_name = f"in_top15_diff_{sample_name}"
        loadings_pc1[col_name] = loadings_pc1["Accession"].isin(protein_set)
        loadings_pc2[col_name] = loadings_pc2["Accession"].isin(protein_set)

    loadings_pc1.to_csv(os.path.join(OUT_DIR, "loadings_top15_pc1.csv"), index=False)
    loadings_pc2.to_csv(os.path.join(OUT_DIR, "loadings_top15_pc2.csv"), index=False)

    print(f"Percentil 99 de toda la matriz: {p99:.5f}")
    print(f"Listo. Resultados guardados en {OUT_DIR}/")


if __name__ == "__main__":
    main()
