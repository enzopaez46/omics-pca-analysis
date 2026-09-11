---
name: explicar-metodologia
description: Explicar en lenguaje simple qué hace un método o una decisión del análisis, y por qué. Usar cuando se pregunta "¿qué es el PCA?", "¿por qué se estandariza?", "¿qué significa este loading?", "explicame esto simple", "¿cómo le explico esto a la directora?", o cuando hay que justificar una decisión de preprocesamiento ante otra persona.
---

## Cuándo usarla

- Cuando no queda claro qué hace un paso del análisis o por qué se hace.
- Cuando hay que explicarle el método a la directora o a alguien que no sigue el detalle.
- Cuando una decisión de preprocesamiento necesita justificarse.

Este proyecto avanza mientras se aprende PCA (ver `CLAUDE.md`). Preguntar qué significa
algo no es una interrupción del trabajo: es parte del trabajo.

## Proceso

1. **Preguntar para quién es la explicación**, porque cambia todo:
   - **Para entenderlo vos** → analogía primero, después el mecanismo, después el detalle
     técnico. Sin apuro y con ejemplos de esta matriz concreta.
   - **Para la directora** → qué decisión se tomó, por qué, y qué habría cambiado con la
     alternativa. Ella conoce el dominio; no hace falta explicar biología.
   - **Para el registro escrito** → preciso y corto, en `docs/design_decisions.md`.

2. **Explicar en tres capas, en este orden.** Nunca arrancar por la fórmula:
   - **Qué problema resuelve** — para qué existe este método.
   - **Cómo lo resuelve, en criollo** — el mecanismo, con una analogía si ayuda.
   - **Qué supone y qué puede salir mal** — las condiciones bajo las que funciona.

3. **Usar siempre los datos de este proyecto en el ejemplo**, no ejemplos genéricos. "Las
   975 proteínas son 975 variables y el PCA busca combinarlas en unos pocos ejes" enseña
   más que cualquier ejemplo abstracto.

4. **Nombrar la alternativa que no se eligió.** Una decisión se entiende cuando se ve
   contra qué se decidió. "Se estandariza cada proteína porque si no, las proteínas más
   abundantes dominarían PC1 solo por su magnitud; el costo es que una proteína detectada
   en una sola muestra pesa igual que una detectada en las 27."

5. **Decir qué NO hace el método.** Es la parte que más se malinterpreta. El PCA no
   testea hipótesis, no da p-valores, no separa grupos a propósito: solo reordena la
   variación que ya está en los datos. Si los grupos no se separan, el PCA no "falló".

6. **Cerrar con la implicancia práctica para este análisis**: qué se puede concluir a
   partir de este método y qué no.

## Qué necesito de vos

- Qué método, paso o decisión hay que explicar.
- Para quién es (vos / la directora / el registro escrito).
- Si es para explicarle a alguien: cuánto sabe de estadística y cuánto de proteómica.

## Qué produce

- Explicación en tres capas, en español simple, con ejemplos de esta matriz.
- La alternativa que no se eligió y qué habría cambiado.
- Lo que el método no puede responder.
- Si va al registro: entrada lista para `docs/design_decisions.md`.
- Si es para la reunión: versión de 3-4 oraciones que se pueda decir en voz alta.

## Ojo con

- **No simplificar hasta que quede falso.** Si una simplificación cambia la conclusión,
  no sirve: mejor una explicación un poco más larga y correcta.
- **No usar jerga para sonar riguroso.** "Multicolinealidad" no explica nada que no
  explique "hay proteínas que se mueven juntas y aportan la misma información".
- **No dar por sentado que PCA se entiende porque se usó tres veces.** Explicarlo de nuevo
  cuesta dos minutos.
