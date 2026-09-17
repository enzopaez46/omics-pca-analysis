"""
compare_qualitative_rules.py — paneles comparativos del análisis cualitativo.

Toma las mismas tres reglas de presencia que genera run_qualitative.py (min1, min2,
rep3) y las dibuja **en paralelo**, una al lado de la otra, para poder leer de un
vistazo cuánto cambia el resultado según la regla en vez de tener que abrir tres
carpetas distintas.

Por cada variable del diseño (genotype, stage, replicate) genera:
    venn_<variable>.png           -> 3 diagramas de Venn en fila (min1 | min2 | rep3)
    similitud_<variable>.png      -> 3 heatmaps de Jaccard % en fila, escala compartida
    intersecciones_<variable>.png -> 3 gráficos de barras de intersecciones en fila

No recalcula nada distinto de run_qualitative.py: reusa sus mismas funciones, así que
los paneles y las figuras individuales siempre muestran lo mismo.

Uso (desde la raíz del proyecto):
    python scripts/compare_qualitative_rules.py
"""

import os
import sys

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_qualitative import (  # noqa: E402
    DATA_PATH,
    FACTOR_GROUPS,
    draw_intersection_bars,
    draw_similarity,
    draw_venn,
    load_detection_matrix,
    parse_sample_metadata,
    presence_by_group,
    similarity_table,
    venn_regions,
)

RULES = ["min1", "min2", "rep3"]
RULE_SUBTITLE = {
    "min1": "min1 — detectada en ≥1 de 9 muestras",
    "min2": "min2 — detectada en ≥2 de 9 muestras",
    "rep3": "rep3 — en las 3 réplicas de alguna condición",
}
FACTOR_TITLE = {
    "genotype": "Genotipo (C=Caimanta, P=Pinton, F1)",
    "stage": "Etapa de maduración (VM, PIN, RM)",
    "replicate": "Réplica (R1, R2, R3)",
}
OUT_DIR = "results/cualitativo_comparado"


def compute_all(detection, metadata):
    """
    Devuelve, por variable y por regla: los conjuntos de proteínas de cada grupo,
    las regiones del Venn y la tabla de similitud.
    """
    data = {}
    for factor, groups in FACTOR_GROUPS.items():
        data[factor] = {}
        for rule in RULES:
            presence = presence_by_group(detection, metadata, factor, rule)
            sets, regions = venn_regions(presence, groups)
            data[factor][rule] = {
                "sets": sets,
                "regions": regions,
                "sim": similarity_table(sets, groups),
            }
    return data


def panel_title(rule, sets, groups):
    total = len(set.union(*[sets[g] for g in groups]))
    return f"{RULE_SUBTITLE[rule]}\n{total} proteínas detectadas"


def panel_venn(data, factor, groups, out_path):
    fig, axes = plt.subplots(1, 3, figsize=(19, 6.8))
    for ax, rule in zip(axes, RULES):
        d = data[factor][rule]
        draw_venn(ax, d["sets"], groups, factor, rule,
                  title=panel_title(rule, d["sets"], groups))
    fig.suptitle(f"Proteínas compartidas — {FACTOR_TITLE[factor]}", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def panel_similarity(data, factor, groups, out_path):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    im = None
    for ax, rule in zip(axes, RULES):
        d = data[factor][rule]
        im = draw_similarity(ax, d["sim"], groups, factor, rule,
                             title=RULE_SUBTITLE[rule])
    fig.suptitle(f"Similitud de repertorio (Jaccard %) — {FACTOR_TITLE[factor]}",
                 fontsize=14)
    fig.tight_layout(rect=(0, 0, 0.92, 0.93))
    cbar_ax = fig.add_axes((0.94, 0.15, 0.015, 0.7))
    fig.colorbar(im, cax=cbar_ax, label="% compartido (Jaccard)")
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def panel_intersections(data, factor, groups, out_path):
    fig, axes = plt.subplots(1, 3, figsize=(19, 5.2))
    for ax, rule in zip(axes, RULES):
        d = data[factor][rule]
        draw_intersection_bars(ax, d["regions"], factor, rule,
                               title=RULE_SUBTITLE[rule])
    fig.suptitle(f"Tamaño de cada intersección — {FACTOR_TITLE[factor]}", fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def rules_summary(data):
    """Una fila por variable y regla, para leer los números sin abrir los gráficos."""
    rows = []
    for factor, groups in FACTOR_GROUPS.items():
        for rule in RULES:
            d = data[factor][rule]
            sets, regions, sim = d["sets"], d["regions"], d["sim"]
            total = len(set.union(*[sets[g] for g in groups]))
            core = len(regions[tuple(groups)])
            row = {
                "variable": factor,
                "regla": rule,
                "n_detectadas_total": total,
                "n_compartidas_por_3": core,
                "pct_compartidas_por_3": round(100 * core / total, 2) if total else 0.0,
                "jaccard_medio_pct": round(sim["jaccard_pct"].mean(), 2),
            }
            for g in groups:
                row[f"n_{g}"] = len(sets[g])
            for g in groups:
                row[f"n_solo_{g}"] = len(regions[(g,)])
            rows.append(row)
    return pd.DataFrame(rows)


def main():
    figures_dir = os.path.join(OUT_DIR, "figures")
    tables_dir = os.path.join(OUT_DIR, "tables")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)

    detection = load_detection_matrix(DATA_PATH)
    metadata = parse_sample_metadata(detection.columns)
    data = compute_all(detection, metadata)

    for factor, groups in FACTOR_GROUPS.items():
        panel_venn(data, factor, groups,
                   os.path.join(figures_dir, f"venn_{factor}.png"))
        panel_similarity(data, factor, groups,
                         os.path.join(figures_dir, f"similitud_{factor}.png"))
        panel_intersections(data, factor, groups,
                            os.path.join(figures_dir, f"intersecciones_{factor}.png"))
        print(f"[{factor}] paneles listos")

    rules_summary(data).to_csv(
        os.path.join(tables_dir, "resumen_reglas.csv"), index=False
    )
    print(f"Listo. Paneles en {figures_dir}/")


if __name__ == "__main__":
    main()
