"""
run_pca.py — script principal de PCA, parametrizable por variante.

Uso (desde la raíz del proyecto):
    python scripts/run_pca.py
        -> corre el baseline (Etapa 1): sin filtrar proteínas, ceros tal cual,
           estandarizado. Sin argumentos se comporta EXACTAMENTE igual que antes,
           para no romper la reproducibilidad de resultados ya generados.

    python scripts/run_pca.py --min-samples-detected 2 --results-dir results/filtro_min2
        -> variante de la Etapa 2: excluye las proteínas detectadas en menos de 2 de
           las 27 muestras, antes de transponer/estandarizar/correr el PCA.

    python scripts/run_pca.py --drop-duplicates --results-dir results/sin_duplicados
        -> variante de muestras: excluye las muestras que son duplicado exacto de otra
           (ver docs/design_decisions.md). Quedan 23 mediciones independientes de 27.

    python scripts/run_pca.py --exclude-samples F1_RM_R1,P_VM_R2
        -> excluye muestras puntuales por nombre. Se puede combinar con las opciones
           de arriba. La exclusión de muestras se aplica ANTES del filtrado de
           proteínas, así que un umbral --min-samples-detected se cuenta sobre las
           muestras que quedaron.

Está armado como funciones separadas para que en las próximas etapas se puedan agregar
nuevas opciones (por ejemplo zero_handling="min_value" o scaling="log_zscore") sin tener
que reescribir el script entero: alcanza con agregar un nuevo "if" en la función
correspondiente.
"""

import argparse
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# Configuración de la corrida (variante "baseline")
# ---------------------------------------------------------------------------
DATA_PATH = "data/master_matrix.csv"
RESULTS_DIR = "results/baseline"
ZERO_HANDLING = "keep"     # opciones futuras: "min_value", "impute", etc.
SCALING = "zscore"         # opciones futuras: "log_zscore", "none", etc.


def find_duplicate_samples(df):
    """
    Devuelve la lista de muestras que son duplicado exacto de otra muestra anterior.

    Se comparan las columnas completas: si dos muestras tienen exactamente los mismos
    valores en las 975 proteínas, no son dos mediciones, son la misma medición contada
    dos veces. De cada grupo de muestras iguales se conserva la PRIMERA en el orden del
    archivo y se marcan las demás.

    Esto NO es una corrección del dato: las réplicas idénticas son una característica
    real de cómo llegan esas muestras (ver docs/design_decisions.md). Lo que permite
    esta función es correr el PCA sobre mediciones independientes para comparar contra
    la corrida completa y ver cuánto cambia el resultado.
    """
    duplicadas = []
    representativas = []
    for col in df.columns:
        if any(df[col].equals(df[ref]) for ref in representativas):
            duplicadas.append(col)
        else:
            representativas.append(col)
    return duplicadas


def select_samples(df, exclude_samples=None, drop_duplicates=False):
    """
    Excluye muestras (columnas) antes de cualquier otro preprocesamiento.

    df acá todavía tiene proteínas en filas y muestras en columnas. Devuelve
    (df_filtrado, lista_de_muestras_excluidas).

    Importante: la exclusión va ANTES de filtrar proteínas y ANTES de estandarizar,
    porque las dos cosas dependen de qué muestras hay. El z-score de cada proteína se
    calcula sobre las muestras presentes, así que sacar una muestra cambia TODOS los
    valores estandarizados, no solo los de esa muestra.

    Con los valores por defecto (None / False) no se excluye nada, así que el
    comportamiento queda idéntico al baseline original.
    """
    excluidas = []

    if drop_duplicates:
        excluidas.extend(find_duplicate_samples(df))

    if exclude_samples:
        for nombre in exclude_samples:
            if nombre not in df.columns:
                raise ValueError(
                    "La muestra '%s' no existe en la matriz. Disponibles: %s"
                    % (nombre, list(df.columns))
                )
            if nombre not in excluidas:
                excluidas.append(nombre)

    if not excluidas:
        return df, []

    return df.drop(columns=excluidas), excluidas


def filter_proteins(df, min_samples_detected):
    """
    Excluye proteínas detectadas (valor distinto de 0) en muy pocas muestras.
    df acá todavía tiene proteínas en filas y muestras en columnas (antes de
    transponer), así que se cuenta por fila cuántas de las 27 muestras tienen un
    valor no-cero para esa proteína.

    Si min_samples_detected es None (valor por defecto), no se filtra nada: esto
    es lo que mantiene el comportamiento idéntico al baseline de la Etapa 1.
    """
    if min_samples_detected is None:
        return df
    detected_count = (df != 0).sum(axis=1)
    return df[detected_count >= min_samples_detected]


def load_and_transpose(path, min_samples_detected=None,
                       exclude_samples=None, drop_duplicates=False):
    """
    Lee master_matrix.csv (proteínas x muestras), excluye muestras si corresponde,
    filtra proteínas poco detectadas si corresponde, y transpone para que cada fila
    sea una muestra y cada columna una proteína, que es el formato que espera
    scikit-learn (observaciones en filas, variables en columnas).

    El archivo original nunca se modifica: acá solo se lee en memoria.

    Llamada sin los argumentos nuevos, se comporta exactamente igual que antes, para
    no romper los resultados ya generados ni los scripts de diagnóstico que la usan.
    """
    df = pd.read_csv(path, index_col="Accession")
    # Primero las muestras, después las proteínas: el conteo de detección por proteína
    # depende de cuántas muestras haya presentes.
    df, _excluidas = select_samples(df, exclude_samples, drop_duplicates)
    df = filter_proteins(df, min_samples_detected)
    # .T transpone: las columnas (muestras) pasan a ser filas.
    df_t = df.T
    return df_t


def handle_zeros(df, method):
    """
    Decide qué hacer con los valores 0 (proteína no detectada en esa muestra).
    Por ahora solo existe la opción "keep", que no cambia nada. Se deja esta
    función como punto de entrada para futuras variantes (Etapa 2 del plan).
    """
    if method == "keep":
        return df
    raise ValueError(f"zero_handling '{method}' no implementado todavía")


def scale_data(df, method):
    """
    Escala los datos antes del PCA. Con "zscore" se estandariza cada proteína
    (columna) para que tenga media 0 y desvío estándar 1. Esto es importante
    porque el PCA es sensible a la escala: sin estandarizar, las proteínas con
    valores más grandes dominarían los componentes principales solo por su
    magnitud, no porque varíen más biológicamente.
    """
    if method == "zscore":
        scaler = StandardScaler()
        scaled_values = scaler.fit_transform(df)
        return pd.DataFrame(scaled_values, index=df.index, columns=df.columns)
    raise ValueError(f"scaling '{method}' no implementado todavía")


def run_pca(df):
    """
    Corre el PCA sobre los datos ya preprocesados (ceros tratados + escalados).
    Devuelve:
    - scores: coordenadas de cada muestra en los componentes principales.
    - variance_explained: % de varianza que explica cada componente.
    """
    pca = PCA()
    scores_values = pca.fit_transform(df)

    n_components = scores_values.shape[1]
    component_names = [f"PC{i+1}" for i in range(n_components)]

    scores = pd.DataFrame(scores_values, index=df.index, columns=component_names)

    variance_explained = pd.DataFrame({
        "component": component_names,
        "variance_explained_pct": pca.explained_variance_ratio_ * 100,
    })

    return scores, variance_explained


def parse_sample_metadata(sample_names):
    """
    A partir de nombres de muestra tipo "C_VM_R1" separa genotipo, etapa de
    maduración y réplica, para poder colorear/dar forma en el gráfico.
    """
    metadata = pd.DataFrame(index=sample_names)
    parts = [name.split("_") for name in sample_names]
    metadata["genotype"] = [p[0] for p in parts]
    metadata["stage"] = [p[1] for p in parts]
    metadata["replicate"] = [p[2] for p in parts]
    return metadata


def plot_pc1_pc2(scores, metadata, variance_explained, out_path, title):
    """
    Grafica PC1 vs PC2. El color representa el genotipo (C, P, F1) y la forma
    representa la etapa de maduración (VM, PIN, RM), para poder ver a simple
    vista si las muestras se agrupan según alguno de los dos factores.
    """
    plot_df = scores[["PC1", "PC2"]].join(metadata)

    pc1_var = variance_explained.loc[
        variance_explained["component"] == "PC1", "variance_explained_pct"
    ].values[0]
    pc2_var = variance_explained.loc[
        variance_explained["component"] == "PC2", "variance_explained_pct"
    ].values[0]

    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        data=plot_df,
        x="PC1",
        y="PC2",
        hue="genotype",
        style="stage",
        s=120,
    )
    plt.xlabel(f"PC1 ({pc1_var:.1f}% varianza explicada)")
    plt.ylabel(f"PC2 ({pc2_var:.1f}% varianza explicada)")
    plt.title(title)
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def parse_args():
    """
    Lee los parámetros de la corrida desde la línea de comandos. Todos tienen un
    valor por defecto igual al baseline (sin filtrar, guardando en
    results/baseline), así que correr el script sin argumentos reproduce
    exactamente la Etapa 1.
    """
    parser = argparse.ArgumentParser(
        description="Corre una variante de PCA sobre master_matrix.csv"
    )
    parser.add_argument(
        "--min-samples-detected",
        type=int,
        default=None,
        help=(
            "Excluye proteínas detectadas en menos de este número de muestras "
            "(de 27). Por defecto no se filtra nada (comportamiento baseline)."
        ),
    )
    parser.add_argument(
        "--drop-duplicates",
        action="store_true",
        help=(
            "Excluye las muestras que son duplicado exacto de otra, conservando una "
            "por grupo. Sirve para correr el PCA solo sobre mediciones independientes."
        ),
    )
    parser.add_argument(
        "--exclude-samples",
        type=str,
        default=None,
        help=(
            "Muestras a excluir, separadas por coma (ej. F1_RM_R1,P_VM_R2). Se aplica "
            "antes del filtrado de proteínas."
        ),
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default=RESULTS_DIR,
        help=f"Carpeta donde guardar los resultados (default: {RESULTS_DIR})",
    )
    args = parser.parse_args()
    # La lista llega como un string separado por comas; se convierte a lista de nombres.
    if args.exclude_samples:
        args.exclude_samples = [
            s.strip() for s in args.exclude_samples.split(",") if s.strip()
        ]
    return args


def main():
    args = parse_args()
    results_dir = args.results_dir
    min_samples_detected = args.min_samples_detected

    # Crear carpetas de resultados si no existen (no toca nada más).
    figures_dir = os.path.join(results_dir, "figures")
    tables_dir = os.path.join(results_dir, "tables")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)

    # 1. Cargar datos, filtrar proteínas poco detectadas (si corresponde) y
    #    transponer (muestras = filas, proteínas = columnas).
    df = load_and_transpose(
        DATA_PATH, min_samples_detected,
        exclude_samples=args.exclude_samples,
        drop_duplicates=args.drop_duplicates,
    )
    n_proteins = df.shape[1]
    n_samples = df.shape[0]

    # Guardar qué muestras entraron en esta corrida. Sin esta tabla, dos variantes con
    # distinta cantidad de muestras son imposibles de comparar después.
    pd.DataFrame({"sample": df.index}).to_csv(
        os.path.join(tables_dir, "samples_used.csv"), index=False
    )

    # 2. Tratar los ceros según la variante configurada.
    df = handle_zeros(df, ZERO_HANDLING)

    # 3. Escalar (estandarizar) cada proteína.
    df_scaled = scale_data(df, SCALING)

    # 4. Correr PCA.
    scores, variance_explained = run_pca(df_scaled)

    # 5. Guardar tablas de resultados.
    variance_explained.to_csv(
        os.path.join(tables_dir, "variance_explained.csv"), index=False
    )
    scores.to_csv(os.path.join(tables_dir, "scores.csv"), index_label="sample")

    # 6. Armar metadata de las muestras (genotipo/etapa/réplica) y graficar.
    metadata = parse_sample_metadata(df.index)
    partes_titulo = []
    if min_samples_detected is not None:
        partes_titulo.append(f"min_samples_detected={min_samples_detected}")
    if args.drop_duplicates:
        partes_titulo.append("sin duplicados")
    if args.exclude_samples:
        partes_titulo.append(f"{len(args.exclude_samples)} excluidas a mano")

    if not partes_titulo:
        title = f"PCA baseline ({n_samples} muestras) — PC1 vs PC2"
    else:
        title = f"PCA {', '.join(partes_titulo)} ({n_samples} muestras) — PC1 vs PC2"
    plot_pc1_pc2(
        scores, metadata, variance_explained,
        os.path.join(figures_dir, "pca_pc1_pc2.png"),
        title,
    )

    print(f"Muestras usadas:  {n_samples} de 27")
    print(f"Proteínas usadas: {n_proteins} de 975")
    print(f"Listo. Resultados guardados en {results_dir}/")


if __name__ == "__main__":
    main()
