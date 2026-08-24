"""
investigate_sample_totals.py — diagnóstico puntual, no es una variante nueva de PCA.

Pregunta a responder: ¿P_RM_R1 y F1_PIN_R1 (las dos muestras que aparecen como
outliers en el PCA baseline) tienen una abundancia total distinta al resto? Esto es
un problema técnico típico en proteómica (cuánto material se cargó, sensibilidad del
equipo ese día) que el z-score por proteína NO corrige, porque el z-score compara cada
proteína contra sí misma en las 27 muestras, no compara muestras completas entre sí.

Este script usa data/master_matrix.csv tal cual, SIN el preprocesamiento del PCA
(sin filtrar proteínas ni estandarizar). No modifica ese archivo ni ningún resultado
ya guardado — todo lo nuevo se guarda en results/baseline/diagnostics/.
"""

import os

import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = "data/master_matrix.csv"
OUT_DIR = "results/baseline/diagnostics"
TARGET_SAMPLES = ["P_RM_R1", "F1_PIN_R1"]


def load_raw_matrix():
    """Lee master_matrix.csv tal cual (proteínas en filas, muestras en columnas)."""
    return pd.read_csv(DATA_PATH, index_col="Accession")


def parse_sample_name(sample_name):
    """De 'C_VM_R1' saca genotipo ('C') y etapa de maduración ('VM')."""
    genotype, stage, _replicate = sample_name.split("_")
    return genotype, stage


def compute_sample_totals(raw_df):
    """
    Para cada muestra (columna), calcula:
    - abundancia_total: suma de los valores de las 975 proteínas. Si el equipo cargó
      más o menos material, o tuvo distinta sensibilidad ese día, esto debería
      notarse acá.
    - proteinas_detectadas: cuántas de las 975 proteínas tienen un valor distinto de
      cero en esa muestra (cuántas se "vieron").

    Devuelve una tabla ordenada de mayor a menor abundancia total.
    """
    totals = raw_df.sum(axis=0)
    detected = (raw_df != 0).sum(axis=0)

    rows = []
    for sample in raw_df.columns:
        genotype, stage = parse_sample_name(sample)
        rows.append({
            "muestra": sample,
            "genotipo": genotype,
            "etapa": stage,
            "abundancia_total": totals[sample],
            "proteinas_detectadas": detected[sample],
        })

    table = pd.DataFrame(rows)
    table = table.sort_values("abundancia_total", ascending=False).reset_index(drop=True)
    return table


def check_out_of_range(table, target_samples, metric):
    """
    Para cada muestra objetivo, compara su valor en `metric` (abundancia_total o
    proteinas_detectadas) contra la mediana y el rango (mínimo-máximo) del RESTO de
    las 26 muestras. Si el valor cae afuera de ese rango, se marca como "fuera de
    rango" — la forma más simple de detectar algo raro sin asumir de antemano qué es
    "normal".
    """
    results = {}
    for sample in target_samples:
        others = table.loc[table["muestra"] != sample, metric]
        value = table.loc[table["muestra"] == sample, metric].values[0]

        low, high = others.min(), others.max()
        results[sample] = {
            "valor": value,
            "mediana_resto": others.median(),
            "rango_resto_min": low,
            "rango_resto_max": high,
            "fuera_de_rango": bool(value < low or value > high),
        }
    return results


def plot_sample_totals(table, target_samples, out_path):
    """
    Gráfico de barras de abundancia total por muestra, ordenado de mayor a menor.
    Como las abundancias totales resultan estar todas muy cerca de 100 (ver
    conclusión), se ajusta el eje Y para que se puedan ver las diferencias chicas
    entre muestras en vez de una barra plana. Las dos muestras sospechosas se marcan
    en otro color y con su valor exacto arriba de la barra.
    """
    colors = ["crimson" if s in target_samples else "steelblue" for s in table["muestra"]]

    plt.figure(figsize=(13, 6))
    bars = plt.bar(table["muestra"], table["abundancia_total"], color=colors)

    # Achicamos el rango del eje Y a los datos reales (con un margen chico) para que
    # se noten las diferencias, en vez de que todas las barras se vean "iguales".
    margin = (table["abundancia_total"].max() - table["abundancia_total"].min()) * 0.15
    plt.ylim(
        table["abundancia_total"].min() - margin,
        table["abundancia_total"].max() + margin,
    )

    for sample in target_samples:
        idx = table.index[table["muestra"] == sample][0]
        value = table.loc[idx, "abundancia_total"]
        plt.annotate(
            f"{sample}\n{value:.4f}",
            xy=(idx, value),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            fontsize=8,
            fontweight="bold",
        )

    plt.xticks(rotation=90, fontsize=7)
    plt.ylabel("Abundancia total (suma de las 975 proteínas)")
    plt.title("Abundancia total por muestra (ordenado de mayor a menor)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    raw_df = load_raw_matrix()
    table = compute_sample_totals(raw_df)

    table.to_csv(os.path.join(OUT_DIR, "sample_totals.csv"), index=False)
    plot_sample_totals(table, TARGET_SAMPLES, os.path.join(OUT_DIR, "sample_totals.png"))

    print("=== Chequeo: ¿las muestras sospechosas están fuera de rango? ===\n")
    for metric, label in [
        ("abundancia_total", "Abundancia total"),
        ("proteinas_detectadas", "Proteínas detectadas"),
    ]:
        print(f"--- {label} ---")
        result = check_out_of_range(table, TARGET_SAMPLES, metric)
        for sample, info in result.items():
            status = "FUERA de rango" if info["fuera_de_rango"] else "dentro de rango"
            print(
                f"{sample}: valor={info['valor']:.4f} | "
                f"mediana del resto={info['mediana_resto']:.4f} | "
                f"rango del resto=[{info['rango_resto_min']:.4f}, {info['rango_resto_max']:.4f}] "
                f"-> {status}"
            )
        print()

    print(f"Listo. Resultados guardados en {OUT_DIR}/")


if __name__ == "__main__":
    main()
