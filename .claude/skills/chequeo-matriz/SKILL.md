---
name: chequeo-matriz
description: Chequeo de calidad de la matriz de datos antes de analizarla. Usar cuando se va a empezar una variante nueva de PCA, cuando cambió master_matrix.csv, cuando un resultado sorprende y hay que descartar que sea un problema del dato, o cuando aparece una muestra que se comporta raro. También ante dudas del tipo "¿estos datos son confiables?", "¿por qué esta muestra se dispara?", "¿esto es un error del archivo?".
---

## Cuándo usarla

- Antes de correr una variante nueva de PCA (cualquier etapa del plan).
- Cada vez que `data/master_matrix.csv` cambia, por cualquier motivo.
- Cuando un resultado sorprende: antes de buscar una explicación biológica, hay que
  descartar que sea un problema del dato.
- Cuando aparece una muestra en una posición extraña del gráfico.

**Por qué existe esta skill**: en la Etapa 1 los tres problemas de la matriz (la columna
`F1_PIN_R2` fuera de escala, las réplicas idénticas, y la enorme cantidad de ceros)
aparecieron de a uno, *después* de haber corrido el PCA, y cada uno costó un script de
investigación aparte. Los tres se detectan de una sola vez y antes de analizar.

## Proceso

1. **Correr el chequeo** — `python scripts/check_matrix.py`. Si el resultado se va a
   discutir o guardar, agregar `--output results/<variante>/chequeo_matriz.md`.

2. **Leer los avisos, no solo los números.** El script imprime un bloque `[AVISO N]` al
   final. Cada aviso es algo para mirar, no necesariamente un error.

3. **Clasificar cada aviso en una de tres categorías**, y decirlo explícitamente:
   - **Error del dato** → hay que corregirlo antes de analizar (ej. valores fuera de
     escala, celdas vacías, negativos).
   - **Característica real del dato** → no se corrige, se documenta y se tiene en cuenta
     al interpretar (ej. las réplicas idénticas, la matriz ya normalizada a total fijo).
   - **Pregunta abierta** → no se puede resolver con los datos que hay; necesita
     información del diseño experimental o de la directora (ej. por qué una muestra
     detecta muchas más proteínas que el resto).

4. **No corregir nada en silencio.** Si un aviso es un error del dato, plantear 2-3
   alternativas de qué hacer en términos simples y esperar la decisión, según la regla 6
   de `CLAUDE.md`. Nunca modificar `data/master_matrix.csv`.

5. **Registrar la decisión** de cada aviso que llevó a una decisión en
   `docs/design_decisions.md`, con su implicancia para la interpretación (no solo qué se
   decidió, sino qué cambia eso al leer el PCA).

6. **Recién ahora analizar.** Si quedaron avisos sin resolver, decirlo antes de mostrar
   cualquier resultado: "este PCA se corrió con estos N avisos pendientes".

## Qué necesito de vos

- Nada obligatorio: el script corre solo sobre `data/master_matrix.csv`.
- Si un aviso es un error del dato, la decisión de qué hacer con él.
- Si un aviso es una pregunta abierta, cualquier información del laboratorio que ayude
  (tandas, lotes, días de corrida, cambios de protocolo).

## Qué produce

- Informe en pantalla, y opcionalmente en `results/<variante>/chequeo_matriz.md`.
- Cada aviso clasificado como error / característica real / pregunta abierta.
- Entradas nuevas en `docs/design_decisions.md` para las decisiones que se tomen.
- Luz verde (o roja) explícita para seguir con el análisis.

## Ojo con

- **Un aviso no es un error.** El script marca lo que se sale del patrón; interpretarlo
  es trabajo humano.
- **Los umbrales son puntos de partida**, no verdades. Se ajustan con `--factor-escala`,
  `--factor-deteccion` y `--tolerancia-totales`.
- **Que no haya avisos no garantiza que el dato esté bien.** Garantiza que no tiene los
  problemas que el script sabe buscar.
