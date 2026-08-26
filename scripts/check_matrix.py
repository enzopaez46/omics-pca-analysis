"""
check_matrix.py — chequeo de calidad de la matriz de datos, ANTES de analizar.

Uso (desde la raíz del proyecto):
    python scripts/check_matrix.py
        -> chequea data/master_matrix.csv e imprime el informe en pantalla.

    python scripts/check_matrix.py --output results/chequeo_matriz.md
        -> además guarda el informe en un archivo Markdown.

    python scripts/check_matrix.py --input data/otra_matriz.csv
        -> chequea otro archivo (por ejemplo una versión corregida del dato).

¿Para qué existe este script?
-----------------------------
En la Etapa 1 los problemas del dato fueron apareciendo de a uno, DESPUÉS de haber
corrido el PCA: la columna `F1_PIN_R2` con valores fuera de escala, las réplicas
idénticas entre sí, y la enorme cantidad de ceros. Cada uno costó un script de
investigación aparte y frenó el análisis.

Este script hace todos esos chequeos de una sola vez y en un solo lugar, para que
los problemas del dato se vean ANTES de interpretar cualquier resultado. La idea es
correrlo cada vez que cambie el archivo fuente, o antes de empezar una variante nueva.

IMPORTANTE: este script solo LEE. Nunca modifica `master_matrix.csv` ni ningún dato.

Nota sobre la salida: se usa solo texto ASCII (`>=`, `->`, `[AVISO]`) en vez de
símbolos tipo flechas, porque la consola de Windows no siempre puede imprimirlos y
el script se cortaría a mitad del informe.
"""

import argparse
import itertools
import os

import pandas as pd
import numpy as np

DATA_PATH = "data/master_matrix.csv"
INDEX_COL = "Accession"

# Umbrales por defecto de los avisos. Son puntos de partida razonables, no verdades
# absolutas: se pueden ajustar por línea de comandos si en algún momento molestan.
FACTOR_FUERA_DE_ESCALA = 10.0   # cuántas veces el máximo típico para considerarlo raro
FACTOR_DETECCION = 3.0          # cuántas veces la detección típica para considerarla rara
TOLERANCIA_TOTALES = 0.01       # diferencia máxima entre totales para decir "normalizada"


# ---------------------------------------------------------------------------
# Chequeos individuales. Cada uno devuelve (texto_del_informe, lista_de_avisos).
# ---------------------------------------------------------------------------

def chequear_forma(df):
    """
    Verifica el tamaño de la matriz y que los nombres de muestra sigan el patrón
    esperado `GENOTIPO_ETAPA_REPLICA` (ej. C_VM_R1), con el diseño 3x3x3 completo.
    Un nombre mal escrito acá se propaga a todos los gráficos coloreados por
    genotipo o etapa, así que conviene detectarlo al principio.
    """
    lineas = []
    avisos = []

    n_proteinas, n_muestras = df.shape
    lineas.append(f"Proteínas (filas):  {n_proteinas}")
    lineas.append(f"Muestras (columnas): {n_muestras}")

    genotipos, etapas, replicas = set(), set(), set()
    mal_formados = []
    for nombre in df.columns:
        partes = str(nombre).split("_")
        if len(partes) != 3:
            mal_formados.append(nombre)
            continue
        genotipos.add(partes[0])
        etapas.add(partes[1])
        replicas.add(partes[2])

    lineas.append(f"Genotipos encontrados: {sorted(genotipos)}")
    lineas.append(f"Etapas encontradas:    {sorted(etapas)}")
    lineas.append(f"Réplicas encontradas:  {sorted(replicas)}")

    if mal_formados:
        avisos.append(
            f"{len(mal_formados)} nombre(s) de muestra no siguen el patrón "
            f"GENOTIPO_ETAPA_REPLICA: {mal_formados}"
        )

    esperadas = len(genotipos) * len(etapas) * len(replicas)
    if not mal_formados and esperadas != n_muestras:
        avisos.append(
            f"El diseño sugiere {len(genotipos)}x{len(etapas)}x{len(replicas)} = "
            f"{esperadas} muestras, pero hay {n_muestras}. Falta o sobra alguna "
            f"combinación."
        )

    return lineas, avisos


def chequear_integridad(df):
    """
    Busca problemas básicos que rompen o distorsionan el PCA sin avisar:
    celdas vacías (NaN), valores negativos, y columnas que no sean numéricas.
    """
    lineas = []
    avisos = []

    no_numericas = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    if no_numericas:
        avisos.append(f"Columnas no numéricas: {no_numericas}")
        lineas.append(f"Columnas no numéricas: {no_numericas}")
    else:
        lineas.append("Todas las columnas son numéricas: OK")

    n_nan = int(df.isna().sum().sum())
    lineas.append(f"Celdas vacías (NaN): {n_nan}")
    if n_nan > 0:
        muestras_con_nan = df.columns[df.isna().any()].tolist()
        avisos.append(
            f"Hay {n_nan} celda(s) vacía(s) en {muestras_con_nan}. scikit-learn "
            f"va a fallar o descartar filas. Hay que decidir qué hacer con ellas."
        )

    numerico = df.select_dtypes(include=[np.number])
    n_negativos = int((numerico < 0).sum().sum())
    lineas.append(f"Valores negativos: {n_negativos}")
    if n_negativos > 0:
        avisos.append(
            f"Hay {n_negativos} valor(es) negativo(s). En una matriz de abundancia "
            f"esto no debería pasar: revisar el armado del archivo."
        )

    return lineas, avisos


def chequear_rango_por_muestra(df, factor):
    """
    Compara el valor máximo de cada muestra contra el máximo típico (la mediana de
    los máximos). Si una muestra tiene un máximo muchísimo más alto que el resto,
    probablemente esté en otra escala o tenga un error de carga.

    Este es el chequeo que habría detectado de entrada el problema de `F1_PIN_R2`
    (valores hasta 1533 cuando ninguna otra columna pasaba de ~15).
    """
    lineas = []
    avisos = []

    maximos = df.max()
    max_tipico = float(maximos.median())
    lineas.append(f"Máximo típico por muestra (mediana): {max_tipico:.4f}")
    lineas.append("")
    lineas.append("Muestra          Mínimo      Máximo   Veces el típico")
    lineas.append("-" * 58)

    for muestra in df.columns:
        maximo = float(maximos[muestra])
        minimo = float(df[muestra].min())
        veces = maximo / max_tipico if max_tipico > 0 else float("nan")
        marca = "  <-- FUERA DE ESCALA" if veces >= factor else ""
        lineas.append(
            f"{muestra:<15} {minimo:>9.4f} {maximo:>11.4f} {veces:>13.1f}x{marca}"
        )

    sospechosas = [
        m for m in df.columns
        if max_tipico > 0 and float(maximos[m]) / max_tipico >= factor
    ]
    if sospechosas:
        avisos.append(
            f"Muestra(s) con valores fuera de escala (máximo >= {factor:g}x el "
            f"típico): {sospechosas}. Revisar antes de correr el PCA: una sola "
            f"columna en otra escala puede dominar los componentes principales."
        )

    return lineas, avisos


def chequear_columnas_duplicadas(df):
    """
    Busca muestras con valores exactamente idénticos entre sí, columna por columna.

    Es importante porque dos réplicas idénticas no son dos mediciones: son la misma
    medición contada dos veces. Eso hace que la "consistencia entre réplicas" se vea
    perfecta sin que eso signifique nada biológico. En este proyecto ya se sabe que
    pasa en algunas condiciones (ver docs/design_decisions.md), pero conviene tener
    la lista completa y actualizada cada vez que cambia el dato fuente.
    """
    lineas = []
    avisos = []

    pares_iguales = []
    for a, b in itertools.combinations(df.columns, 2):
        if df[a].equals(df[b]):
            pares_iguales.append((a, b))

    if not pares_iguales:
        lineas.append("No hay muestras idénticas entre sí: OK")
        return lineas, avisos

    # Agrupar los pares en grupos de muestras todas iguales entre sí.
    grupos = []
    for a, b in pares_iguales:
        for grupo in grupos:
            if a in grupo or b in grupo:
                grupo.update([a, b])
                break
        else:
            grupos.append({a, b})

    lineas.append(f"Grupos de muestras con valores idénticos: {len(grupos)}")
    for grupo in grupos:
        ordenado = sorted(grupo, key=lambda c: list(df.columns).index(c))
        lineas.append(f"  - {', '.join(ordenado)}")

    total_muestras_afectadas = sum(len(g) for g in grupos)
    avisos.append(
        f"{total_muestras_afectadas} muestras son duplicados exactos de otra "
        f"({len(grupos)} grupo(s)). Esas réplicas no son mediciones independientes: "
        f"su consistencia no es evidencia biológica. Ver docs/design_decisions.md."
    )

    return lineas, avisos


def chequear_ceros_y_deteccion(df, factor):
    """
    Perfila los ceros de la matriz. Acá el 0 significa "proteína no detectada", no
    "abundancia cero", así que su distribución es información valiosa y no ruido.

    Reporta tres cosas distintas que se confunden fácil:
    - Cuántas proteínas detecta cada muestra (¿alguna detecta muchas más que el resto?)
    - En cuántas muestras se detecta cada proteína (¿son casi todas raras?)
    - Proteínas que no se detectan en NINGUNA muestra (filas inútiles para el PCA)

    Este chequeo habría explicado desde el principio por qué `P_RM_R1` (697 proteínas
    detectadas contra una mediana de ~100) se disparaba en el gráfico.
    """
    lineas = []
    avisos = []

    detectado = df != 0
    pct_ceros = 100.0 * (1.0 - detectado.values.mean())
    lineas.append(f"Porcentaje de ceros en toda la matriz: {pct_ceros:.1f}%")

    por_proteina = detectado.sum(axis=1)
    lineas.append(
        f"Cada proteína se detecta en promedio en {por_proteina.mean():.1f} de "
        f"{df.shape[1]} muestras (mediana: {int(por_proteina.median())})"
    )

    nunca = int((por_proteina == 0).sum())
    lineas.append(f"Proteínas no detectadas en ninguna muestra: {nunca}")
    if nunca > 0:
        avisos.append(
            f"{nunca} proteína(s) están en 0 en las {df.shape[1]} muestras. No "
            f"aportan nada al PCA y su desvío estándar es 0, lo que puede dar "
            f"problemas al estandarizar. Conviene excluirlas."
        )

    # Cuántas proteínas quedarían con cada umbral de filtrado (Etapa 2 del plan).
    lineas.append("")
    lineas.append("Proteínas que sobrevivirían a cada umbral de filtrado:")
    for umbral in (1, 2, 3, 5, 10):
        quedan = int((por_proteina >= umbral).sum())
        pct = 100.0 * quedan / df.shape[0]
        lineas.append(f"  detectada en >= {umbral:>2} muestras: {quedan:>4} ({pct:.0f}%)")

    # Detección por muestra: acá aparecen las muestras "demasiado profundas".
    por_muestra = detectado.sum(axis=0)
    mediana = float(por_muestra.median())
    lineas.append("")
    lineas.append(f"Proteínas detectadas por muestra (mediana: {int(mediana)}):")
    lineas.append("")
    lineas.append("Muestra          Detectadas   Veces la mediana")
    lineas.append("-" * 50)
    for muestra in df.columns:
        n = int(por_muestra[muestra])
        veces = n / mediana if mediana > 0 else float("nan")
        marca = "  <-- ATÍPICA" if veces >= factor or veces <= 1.0 / factor else ""
        lineas.append(f"{muestra:<15} {n:>10} {veces:>15.1f}x{marca}")

    atipicas = [
        m for m in df.columns
        if mediana > 0 and (
            int(por_muestra[m]) / mediana >= factor
            or int(por_muestra[m]) / mediana <= 1.0 / factor
        )
    ]
    if atipicas:
        avisos.append(
            f"Muestra(s) con una cantidad atípica de proteínas detectadas "
            f"(>= {factor:g}x o <= 1/{factor:g} de la mediana): {atipicas}. Suele "
            f"ser una causa técnica (profundidad de la corrida), no biológica, y "
            f"puede dominar el PCA al estandarizar."
        )

    return lineas, avisos


def chequear_totales(df, tolerancia):
    """
    Suma cada muestra para ver si la matriz ya viene normalizada a un total fijo.
    Saberlo cambia la interpretación: si todas las muestras suman lo mismo, las
    diferencias de abundancia total NO existen en este dato, y una muestra que
    detecta más proteínas necesariamente tiene valores individuales más chicos.
    """
    lineas = []
    avisos = []

    totales = df.sum()
    lineas.append(f"Total mínimo:  {totales.min():.4f}  ({totales.idxmin()})")
    lineas.append(f"Total máximo:  {totales.max():.4f}  ({totales.idxmax()})")
    lineas.append(f"Total mediano: {totales.median():.4f}")

    rango = float(totales.max() - totales.min())
    if rango <= tolerancia:
        lineas.append("")
        lineas.append(
            f"Todas las muestras suman prácticamente lo mismo (diferencia total: "
            f"{rango:.6f}). La matriz ya viene normalizada a un total fijo."
        )
        lineas.append(
            "Implicancia: no hay diferencias de abundancia total que corregir, pero "
            "sí hay que tener presente que una muestra con más proteínas detectadas "
            "reparte ese mismo total entre más proteínas."
        )
    else:
        lineas.append("")
        lineas.append(
            f"Los totales por muestra difieren (rango: {rango:.4f}). La matriz NO "
            f"parece estar normalizada a un total fijo, así que las diferencias de "
            f"abundancia total sí pueden influir en el PCA."
        )
        avisos.append(
            f"Los totales por muestra no son iguales (rango: {rango:.4f}). Decidir "
            f"si hace falta normalizar antes del PCA."
        )

    return lineas, avisos


# ---------------------------------------------------------------------------
# Armado del informe
# ---------------------------------------------------------------------------

def armar_informe(df, ruta, factor_escala, factor_deteccion, tolerancia):
    """
    Corre todos los chequeos en orden y devuelve el informe completo como texto,
    con los avisos juntos al final para que se puedan leer de un vistazo.
    """
    secciones = [
        ("1. Forma de la matriz y diseño experimental", chequear_forma(df)),
        ("2. Integridad básica (vacíos, negativos, tipos)", chequear_integridad(df)),
        ("3. Rango de valores por muestra", chequear_rango_por_muestra(df, factor_escala)),
        ("4. Muestras duplicadas", chequear_columnas_duplicadas(df)),
        ("5. Ceros y detección", chequear_ceros_y_deteccion(df, factor_deteccion)),
        ("6. Totales por muestra (normalización)", chequear_totales(df, tolerancia)),
    ]

    salida = []
    salida.append("=" * 70)
    salida.append("  CHEQUEO DE CALIDAD DE LA MATRIZ")
    salida.append(f"  Archivo: {ruta}")
    salida.append("=" * 70)

    todos_los_avisos = []
    for titulo, (lineas, avisos) in secciones:
        salida.append("")
        salida.append(f"--- {titulo} ---")
        salida.extend(lineas)
        todos_los_avisos.extend(avisos)

    salida.append("")
    salida.append("=" * 70)
    if todos_los_avisos:
        salida.append(f"  AVISOS: {len(todos_los_avisos)} cosa(s) para revisar")
        salida.append("=" * 70)
        for i, aviso in enumerate(todos_los_avisos, start=1):
            salida.append("")
            salida.append(f"[AVISO {i}] {aviso}")
    else:
        salida.append("  Sin avisos: la matriz pasó todos los chequeos.")
        salida.append("=" * 70)

    salida.append("")
    salida.append("=" * 70)
    salida.append(
        "Recordatorio: un aviso no es necesariamente un error. Es algo que hay que "
        "mirar y decidir\nqué hacer antes de interpretar el PCA. Las decisiones que "
        "se tomen van a docs/design_decisions.md."
    )
    salida.append("=" * 70)

    return "\n".join(salida), todos_los_avisos


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Chequea la calidad de la matriz de proteómica antes de analizarla. "
            "Solo lee: nunca modifica el archivo fuente."
        )
    )
    parser.add_argument(
        "--input", type=str, default=DATA_PATH,
        help=f"Matriz a chequear (default: {DATA_PATH})",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Si se indica, guarda el informe en este archivo (.md o .txt)",
    )
    parser.add_argument(
        "--factor-escala", type=float, default=FACTOR_FUERA_DE_ESCALA,
        help=(
            "Cuántas veces el máximo típico tiene que superar una muestra para "
            f"marcarla como fuera de escala (default: {FACTOR_FUERA_DE_ESCALA:g})"
        ),
    )
    parser.add_argument(
        "--factor-deteccion", type=float, default=FACTOR_DETECCION,
        help=(
            "Cuántas veces la detección mediana tiene que superar (o quedar por "
            f"debajo de) una muestra para marcarla como atípica (default: "
            f"{FACTOR_DETECCION:g})"
        ),
    )
    parser.add_argument(
        "--tolerancia-totales", type=float, default=TOLERANCIA_TOTALES,
        help=(
            "Diferencia máxima entre totales por muestra para considerar que la "
            f"matriz viene normalizada (default: {TOLERANCIA_TOTALES:g})"
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.exists(args.input):
        print(f"No se encontró el archivo: {args.input}")
        return 1

    # index_col deja las proteínas como índice, así que df queda con solo las
    # 27 columnas de muestras: proteínas en filas, muestras en columnas.
    df = pd.read_csv(args.input, index_col=INDEX_COL)

    informe, avisos = armar_informe(
        df, args.input,
        args.factor_escala, args.factor_deteccion, args.tolerancia_totales,
    )
    print(informe)

    if args.output:
        carpeta = os.path.dirname(args.output)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("# Chequeo de calidad de la matriz\n\n")
            f.write(f"Archivo chequeado: `{args.input}`\n\n")
            f.write("```\n")
            f.write(informe)
            f.write("\n```\n")
        print(f"\nInforme guardado en {args.output}")

    # Código de salida 0 siempre: los avisos son para leer y decidir, no errores
    # que deban cortar un pipeline.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
