"""
investigate_replicate_pattern.py — diagnóstico puntual, no es una variante nueva de PCA.

Pregunta a responder: en el diagnóstico anterior (investigate_sample_totals.py) vimos
que P_RM_R1 y F1_PIN_R1 detectan muchas más proteínas que el resto. Acá se chequea algo
más amplio: ¿es un patrón sistemático de "R1 detecta más que R2, y R2 más que R3" en
casi todas las combinaciones de genotipo+etapa, o es cosa de una o dos muestras
puntuales?

Usa results/baseline/diagnostics/sample_totals.csv, que ya tiene la cantidad de
proteínas detectadas por muestra (generado por investigate_sample_totals.py). No toca
data/master_matrix.csv ni ningún resultado de results/baseline/tables/,
results/filtro_min2/ ni results/filtro_min3/.
"""

import os

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

SAMPLE_TOTALS_PATH = "results/baseline/diagnostics/sample_totals.csv"
OUT_DIR = "results/baseline/diagnostics"

REPLICATE_ORDER = ["R1", "R2", "R3"]
GENOTYPE_ORDER = ["C", "P", "F1"]
STAGE_ORDER = ["VM", "PIN", "RM"]


def load_sample_totals():
    """Carga la tabla ya calculada de abundancia total / proteínas detectadas."""
    return pd.read_csv(SAMPLE_TOTALS_PATH)


def add_replicate_column(table):
    """
    Saca la réplica (R1, R2 o R3) del nombre de la muestra, sin importar genotipo ni
    etapa. Por ejemplo 'F1_PIN_R2' -> 'R2'.
    """
    table = table.copy()
    table["replica"] = table["muestra"].str.split("_").str[-1]
    return table


def summarize_by_replicate(table):
    """
    Agrupa las 27 muestras solo por réplica (juntando todos los genotipos y etapas) y
    calcula mediana, mínimo y máximo de proteínas detectadas por grupo. Esto muestra
    si hay una tendencia general de "las R1 detectan más" en todo el dataset.
    """
    summary = (
        table.groupby("replica")["proteinas_detectadas"]
        .agg(mediana="median", minimo="min", maximo="max")
        .reindex(REPLICATE_ORDER)
        .reset_index()
    )
    return summary


def plot_boxplot_by_replicate(table, out_path):
    """
    Boxplot de proteínas detectadas por réplica (R1/R2/R3). Si el patrón es
    sistemático, las cajas de R1 deberían quedar más arriba que las de R2, y estas
    más arriba que las de R3.
    """
    plt.figure(figsize=(7, 6))
    sns.boxplot(
        data=table,
        x="replica",
        y="proteinas_detectadas",
        order=REPLICATE_ORDER,
    )
    sns.stripplot(
        data=table,
        x="replica",
        y="proteinas_detectadas",
        order=REPLICATE_ORDER,
        color="black",
        size=5,
        alpha=0.6,
    )
    plt.ylabel("Proteínas detectadas (de 975)")
    plt.xlabel("Réplica")
    plt.title("Proteínas detectadas por réplica (todas las condiciones juntas)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def build_group_table(table):
    """
    Arma una tabla con una fila por cada una de las 9 combinaciones genotipo+etapa
    (C_VM, C_PIN, ..., F1_RM) y una columna por réplica (R1, R2, R3), para poder
    comparar de un vistazo si R1 > R2 > R3 se repite en casi todos los grupos o es
    excepción en algunos.
    """
    table = table.copy()
    table["grupo"] = table["genotipo"] + "_" + table["etapa"]

    pivot = table.pivot(index="grupo", columns="replica", values="proteinas_detectadas")
    pivot = pivot[REPLICATE_ORDER]

    # Orden de filas: genotipo (C, P, F1) x etapa (VM, PIN, RM), para que se lea en
    # el mismo orden que el resto del proyecto.
    ordered_groups = [f"{g}_{s}" for g in GENOTYPE_ORDER for s in STAGE_ORDER]
    pivot = pivot.reindex(ordered_groups)

    pivot["R1_mayor_que_R3"] = pivot["R1"] > pivot["R3"]

    return pivot.reset_index()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    table = load_sample_totals()
    table = add_replicate_column(table)

    replicate_summary = summarize_by_replicate(table)
    print("=== Proteínas detectadas por réplica (todas las condiciones juntas) ===")
    print(replicate_summary.to_string(index=False))
    print()

    plot_boxplot_by_replicate(table, os.path.join(OUT_DIR, "detection_by_replicate.png"))

    group_table = build_group_table(table)
    group_table.to_csv(
        os.path.join(OUT_DIR, "detection_by_replicate_table.csv"), index=False
    )

    n_groups = len(group_table)
    n_matching = group_table["R1_mayor_que_R3"].sum()
    print(f"Grupos donde R1 detecta más que R3: {n_matching} de {n_groups}")
    print()
    print(group_table.to_string(index=False))

    print(f"\nListo. Resultados guardados en {OUT_DIR}/")


if __name__ == "__main__":
    main()
