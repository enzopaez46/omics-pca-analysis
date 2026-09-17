"""
run_qualitative.py — variante cualitativa (presencia/ausencia) sobre master_matrix.csv.

Cambia el paradigma respecto a run_pca.py: en vez de mirar cuánta abundancia tiene
cada proteína, mira solamente SI la proteína se detectó o no (valor != 0). Con eso se
comparan los grupos de las tres variables del diseño experimental:

    genotype   -> C (Caimanta), P (Pinton), F1
    stage      -> VM, PIN, RM
    replicate  -> R1, R2, R3

Para cada variable se generan diagramas de Venn de 3 conjuntos (qué proteínas comparten
los grupos y cuáles son exclusivas), un heatmap de similitud (Jaccard %) y tablas con
las proteínas de cada región del Venn y los porcentajes de solapamiento.

Regla de presencia (--presence-rule): define cuándo una proteína cuenta como "presente"
en un grupo de 9 muestras. Se corren las tres y se comparan, igual que se hizo con los
umbrales min2/min3 de la Etapa 2:

    min1  -> detectada en >=1 de las 9 muestras del grupo (la más inclusiva).
    min2  -> detectada en >=2 de las 9 muestras del grupo (saca detecciones únicas).
    rep3  -> reproducible: detectada en las 3 réplicas de al menos una condición
             genotipo+etapa dentro del grupo (la más exigente). Para la variable
             `replicate` no existe ese anidamiento (cada grupo R1/R2/R3 tiene 9
             muestras de condiciones distintas, sin réplicas internas), así que ahí
             rep3 se aproxima con "detectada en >=3 de las 9 muestras del grupo".

Uso (desde la raíz del proyecto):
    python scripts/run_qualitative.py --presence-rule min1
    python scripts/run_qualitative.py --presence-rule min2
    python scripts/run_qualitative.py --presence-rule rep3

Por defecto guarda en results/cualitativo_<regla>/. No modifica data/master_matrix.csv.
"""

import argparse
import itertools
import os

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib_venn import venn3, venn3_circles

DATA_PATH = "data/master_matrix.csv"

# Grupos de cada variable, en el orden en que se quieren mostrar.
FACTOR_GROUPS = {
    "genotype": ["C", "P", "F1"],
    "stage": ["VM", "PIN", "RM"],
    "replicate": ["R1", "R2", "R3"],
}

# Nombre largo para los gráficos (los genotipos son variedades de tomate).
GROUP_LABELS = {
    "C": "C (Caimanta)",
    "P": "P (Pinton)",
    "F1": "F1",
    "VM": "VM",
    "PIN": "PIN",
    "RM": "RM",
    "R1": "R1",
    "R2": "R2",
    "R3": "R3",
}

# Colores: las etapas usan el color real del tomate (CLAUDE.md); genotipo en negro/gris
# (el contrato del proyecto pide genotipo en negro) y réplica en grises azulados
# neutros, porque no representa nada biológico.
FACTOR_COLORS = {
    "stage": {"VM": "#2ca02c", "PIN": "#ff7f0e", "RM": "#d62728"},
    "genotype": {"C": "#000000", "P": "#666666", "F1": "#bbbbbb"},
    "replicate": {"R1": "#4c72b0", "R2": "#8fa8cf", "R3": "#c9d4e6"},
}


def parse_sample_metadata(sample_names):
    """A partir de "C_VM_R1" separa genotipo, etapa y réplica."""
    parts = [name.split("_") for name in sample_names]
    return pd.DataFrame(
        {
            "genotype": [p[0] for p in parts],
            "stage": [p[1] for p in parts],
            "replicate": [p[2] for p in parts],
        },
        index=list(sample_names),
    )


def load_detection_matrix(path):
    """
    Lee master_matrix.csv y lo convierte en matriz booleana de detección
    (proteínas x muestras): True = detectada (valor != 0), False = no detectada.
    El 0 en el dato fuente significa "no detectada", no abundancia cero.
    """
    df = pd.read_csv(path, index_col="Accession")
    return df != 0


def presence_by_group(detection, metadata, factor, rule):
    """
    Devuelve un DataFrame booleano (proteínas x grupos del factor) aplicando la regla
    de presencia elegida. Cada grupo tiene 9 muestras (3 x 3).
    """
    groups = FACTOR_GROUPS[factor]
    presence = pd.DataFrame(index=detection.index, columns=groups, dtype=bool)

    for group in groups:
        samples = metadata.index[metadata[factor] == group]
        sub = detection[samples]

        if rule == "min1":
            presence[group] = sub.sum(axis=1) >= 1
        elif rule == "min2":
            presence[group] = sub.sum(axis=1) >= 2
        elif rule == "rep3":
            if factor == "replicate":
                # No hay réplicas anidadas dentro de R1/R2/R3: se aproxima con >=3 de 9.
                presence[group] = sub.sum(axis=1) >= 3
            else:
                # El otro factor define las condiciones internas del grupo
                # (ej. dentro de C están C_VM, C_PIN, C_RM, cada una con 3 réplicas).
                other = "stage" if factor == "genotype" else "genotype"
                reproducible = pd.Series(False, index=detection.index)
                for level in FACTOR_GROUPS[other]:
                    cond_samples = metadata.index[
                        (metadata[factor] == group) & (metadata[other] == level)
                    ]
                    all_three = sub[cond_samples].all(axis=1)
                    reproducible = reproducible | all_three
                presence[group] = reproducible
        else:
            raise ValueError(f"presence_rule '{rule}' no implementada")

    return presence


def venn_regions(presence, groups):
    """
    Calcula las 7 regiones de un Venn de 3 conjuntos como listas de Accessions.
    Las claves son tuplas de los grupos que comparten esa región.
    """
    a, b, c = groups
    sets = {g: set(presence.index[presence[g]]) for g in groups}
    regions = {}
    for r in range(1, 4):
        for combo in itertools.combinations(groups, r):
            inside = set.intersection(*[sets[g] for g in combo])
            outside = [g for g in groups if g not in combo]
            for g in outside:
                inside = inside - sets[g]
            regions[combo] = sorted(inside)
    return sets, regions


def similarity_table(sets, groups):
    """
    Tabla de solapamiento por pares:
    - jaccard_pct: compartidas / union (simétrico, "qué tan parecidos son").
    - pct_of_a / pct_of_b: qué porcentaje del repertorio de cada grupo es compartido
      (asimétrico: importa cuando un grupo detecta muchas más proteínas que el otro).
    """
    rows = []
    for a, b in itertools.combinations(groups, 2):
        sa, sb = sets[a], sets[b]
        shared = len(sa & sb)
        union = len(sa | sb)
        rows.append({
            "group_a": a,
            "group_b": b,
            "n_a": len(sa),
            "n_b": len(sb),
            "shared": shared,
            "union": union,
            "jaccard_pct": round(100 * shared / union, 2) if union else 0.0,
            "pct_of_a_shared": round(100 * shared / len(sa), 2) if sa else 0.0,
            "pct_of_b_shared": round(100 * shared / len(sb), 2) if sb else 0.0,
        })
    return pd.DataFrame(rows)


# Cada gráfico se dibuja con una función draw_* que recibe un `ax`, y una función
# plot_* que crea la figura, llama al draw_* y la guarda. Así el mismo dibujo se puede
# reusar en un panel comparativo de varias reglas (scripts/compare_qualitative_rules.py)
# sin duplicar el código de estilo.

VENN_MEMBERS = {
    "100": [0], "010": [1], "001": [2],
    "110": [0, 1], "101": [0, 2], "011": [1, 2], "111": [0, 1, 2],
}


def draw_venn(ax, sets, groups, factor, rule, title=None):
    """Diagrama de Venn de 3 conjuntos con conteo y % sobre el total detectado."""
    colors = [FACTOR_COLORS[factor][g] for g in groups]
    labels = [GROUP_LABELS[g] for g in groups]
    subsets = [sets[g] for g in groups]
    total = len(set.union(*subsets))

    v = venn3(subsets, set_labels=labels, ax=ax)

    # matplotlib_venn pinta las regiones con su paleta por defecto (magenta/celeste),
    # que no respeta los colores del proyecto. Se repinta cada región: las exclusivas
    # con el color de su grupo y las compartidas con la mezcla de los grupos que la
    # forman, para que el color siga indicando de quién es cada zona.
    for patch_id, member_idx in VENN_MEMBERS.items():
        patch = v.get_patch_by_id(patch_id)
        if patch is None:
            continue
        rgbs = np.array([to_rgb(colors[i]) for i in member_idx])
        patch.set_color(tuple(rgbs.mean(axis=0)))
        patch.set_alpha(0.55)
        patch.set_edgecolor("none")
    venn3_circles(subsets, linewidth=1.0, color="black", ax=ax)

    # Etiquetas: conteo + % respecto del total de proteínas detectadas en el trío.
    for patch_id in VENN_MEMBERS:
        label = v.get_label_by_id(patch_id)
        if label is None:
            continue
        n = int(label.get_text()) if label.get_text() else 0
        label.set_text(f"{n}\n({100 * n / total:.1f}%)" if n else "")
        label.set_fontsize(9)

    ax.set_title(
        title or (
            f"Proteínas compartidas entre {factor} — regla '{rule}'\n"
            f"{total} proteínas detectadas en total (de 975)"
        )
    )
    return v


def similarity_matrix(sim, groups):
    """Pasa la tabla de pares a matriz cuadrada de Jaccard % (diagonal = 100)."""
    mat = pd.DataFrame(100.0, index=groups, columns=groups)
    for _, row in sim.iterrows():
        mat.loc[row["group_a"], row["group_b"]] = row["jaccard_pct"]
        mat.loc[row["group_b"], row["group_a"]] = row["jaccard_pct"]
    return mat


def draw_similarity(ax, sim, groups, factor, rule, title=None):
    """Heatmap de Jaccard % entre los grupos del factor (matriz 3x3)."""
    mat = similarity_matrix(sim, groups)
    im = ax.imshow(mat.values, cmap="Greys", vmin=0, vmax=100)
    ax.set_xticks(range(len(groups)), [GROUP_LABELS[g] for g in groups])
    ax.set_yticks(range(len(groups)), [GROUP_LABELS[g] for g in groups])
    for i in range(len(groups)):
        for j in range(len(groups)):
            val = mat.values[i, j]
            ax.text(j, i, f"{val:.1f}%", ha="center", va="center",
                    color="white" if val > 55 else "black", fontsize=10)
    ax.set_title(
        title or f"Similitud de repertorio (Jaccard)\n{factor} — regla '{rule}'",
        fontsize=11,
    )
    return im


def draw_intersection_bars(ax, regions, factor, rule, title=None):
    """
    Barras tipo UpSet simplificadas: tamaño de cada una de las 7 regiones del Venn,
    ordenadas de mayor a menor. Sirve para leer los números sin depender del área
    de los círculos, que en un Venn no es proporcional.
    """
    items = sorted(regions.items(), key=lambda kv: len(kv[1]), reverse=True)
    names = [" ∩ ".join(k) if len(k) > 1 else f"solo {k[0]}" for k, _ in items]
    values = [len(v) for _, v in items]
    total = sum(values)

    ax.bar(range(len(values)), values, color="#444444")
    for i, val in enumerate(values):
        pct = 100 * val / total if total else 0
        ax.text(i, val, f"{val}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(len(names)), names, rotation=30, ha="right")
    ax.set_ylabel("proteínas")
    ax.set_ylim(0, max(values) * 1.22 if values else 1)
    ax.set_title(title or f"Tamaño de cada intersección — {factor}, regla '{rule}'")


def plot_venn(sets, groups, factor, rule, out_path):
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    draw_venn(ax, sets, groups, factor, rule)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_similarity_heatmap(sim, groups, factor, rule, out_path):
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    im = draw_similarity(ax, sim, groups, factor, rule)
    fig.colorbar(im, ax=ax, label="% compartido (Jaccard)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_intersection_bars(regions, groups, factor, rule, out_path):
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    draw_intersection_bars(ax, regions, factor, rule)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def regions_to_table(regions, groups):
    """Tabla con una fila por región del Venn: cuántas proteínas y qué % del total."""
    total = sum(len(v) for v in regions.values())
    rows = []
    for combo, accs in sorted(regions.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        rows.append({
            "region": " ∩ ".join(combo) if len(combo) > 1 else f"solo {combo[0]}",
            "n_groups": len(combo),
            "n_proteins": len(accs),
            "pct_of_detected": round(100 * len(accs) / total, 2) if total else 0.0,
        })
    return pd.DataFrame(rows)


def regions_to_long_table(regions):
    """Una fila por proteína, indicando en qué región del Venn cayó."""
    rows = []
    for combo, accs in regions.items():
        region = " ∩ ".join(combo) if len(combo) > 1 else f"solo {combo[0]}"
        for acc in accs:
            rows.append({"Accession": acc, "region": region, "n_groups": len(combo)})
    return pd.DataFrame(rows).sort_values(["n_groups", "region", "Accession"],
                                          ascending=[False, True, True])


def parse_args():
    parser = argparse.ArgumentParser(
        description="Análisis cualitativo (presencia/ausencia) de master_matrix.csv"
    )
    parser.add_argument(
        "--presence-rule", choices=["min1", "min2", "rep3"], default="min2",
        help="Cuándo una proteína cuenta como presente en un grupo (default: min2)",
    )
    parser.add_argument(
        "--results-dir", type=str, default=None,
        help="Carpeta de salida (default: results/cualitativo_<regla>)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    rule = args.presence_rule
    results_dir = args.results_dir or f"results/cualitativo_{rule}"
    figures_dir = os.path.join(results_dir, "figures")
    tables_dir = os.path.join(results_dir, "tables")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)

    detection = load_detection_matrix(DATA_PATH)
    metadata = parse_sample_metadata(detection.columns)

    # Resumen de detección por muestra (contexto: la matriz es muy dispersa).
    per_sample = pd.DataFrame({
        "sample": detection.columns,
        "n_detected": detection.sum(axis=0).values,
    }).merge(metadata, left_on="sample", right_index=True)
    per_sample.to_csv(os.path.join(tables_dir, "detected_per_sample.csv"), index=False)

    summary_rows = []
    for factor, groups in FACTOR_GROUPS.items():
        presence = presence_by_group(detection, metadata, factor, rule)
        presence.astype(int).to_csv(
            os.path.join(tables_dir, f"presence_{factor}.csv"), index_label="Accession"
        )

        sets, regions = venn_regions(presence, groups)
        sim = similarity_table(sets, groups)
        sim.to_csv(os.path.join(tables_dir, f"similarity_{factor}.csv"), index=False)
        regions_to_table(regions, groups).to_csv(
            os.path.join(tables_dir, f"venn_regions_{factor}.csv"), index=False
        )
        regions_to_long_table(regions).to_csv(
            os.path.join(tables_dir, f"proteins_by_region_{factor}.csv"), index=False
        )

        plot_venn(sets, groups, factor, rule,
                  os.path.join(figures_dir, f"venn_{factor}.png"))
        plot_similarity_heatmap(sim, groups, factor, rule,
                                os.path.join(figures_dir, f"similarity_{factor}.png"))
        plot_intersection_bars(regions, groups, factor, rule,
                               os.path.join(figures_dir, f"intersections_{factor}.png"))

        total = len(set.union(*[sets[g] for g in groups]))
        core = len(regions[tuple(groups)])
        summary_rows.append({
            "factor": factor,
            "presence_rule": rule,
            "n_detected_total": total,
            "n_core_shared_by_3": core,
            "pct_core": round(100 * core / total, 2) if total else 0.0,
            "mean_jaccard_pct": round(sim["jaccard_pct"].mean(), 2),
            **{f"n_{g}": len(sets[g]) for g in groups},
            **{f"n_exclusive_{g}": len(regions[(g,)]) for g in groups},
        })

        print(f"[{factor}] total detectadas={total} | core(3 grupos)={core} "
              f"({100 * core / total:.1f}%) | Jaccard medio={sim['jaccard_pct'].mean():.1f}%")

    pd.DataFrame(summary_rows).to_csv(
        os.path.join(tables_dir, "summary.csv"), index=False
    )
    print(f"Listo. Resultados en {results_dir}/")


if __name__ == "__main__":
    main()
