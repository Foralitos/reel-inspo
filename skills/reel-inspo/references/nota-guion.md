# Plantilla — nota de guion

Ruta: `<vault>/<base>/guiones/<tipo-slug>/<YYYY-MM-DD>-<handle>-guion-<slug>.md`

El **tipo de guion** es la estructura de lo que se dice, que no siempre coincide con el formato
visual. Tipos de arranque: historia personal, lista/top, tutorial / hacks, opinión / hot take,
dato curioso, comparación, review, reacción, behind the scenes. Reusa los del `_index.md`.

Solo se escribe si el reel tiene voz. Corrige los errores obvios de whisper en nombres propios
(marcas, personas, tipografías) y anótalo en el Contexto.

Palabras por minuto = palabras del transcript ÷ duración en segundos × 60.

```markdown
---
type: inspo-guion
date: YYYY-MM-DD
tags: [inspo, guion, <tipo-slug>, <recursos-slug>]
fuente: <url>
autor: "@handle"
idioma: <es|en|es-ES…>
tipo-guion: "<tipo>"
duracion-s: <n>
palabras: <n>
palabras-por-minuto: <n>
recursos: [<recursos retóricos reusables>]
reel: "[[<base>/reels/<formato-slug>/<nota visual>]]"
---

# Guion: "<la fórmula en una frase>" (<tipo>)

## Contexto
<quién, cuándo se guardó, idioma, correcciones de whisper, link a la nota visual>

## Guion por bloques
| Bloque | Tiempo | Texto (verbatim) | Función |
|---|---|---|---|
<TODO el guion, sin saltarte frases, partido en bloques con nombre (Gancho, Objeción, Punto 1,
Giro, Remate, CTA…) y qué hace cada bloque>

## Recursos que usa
- **<recurso>**: <cómo funciona> — "<ejemplo verbatim>"

## Ritmo verbal
<palabras, palabras/min, largo de frases, dónde frena y por qué>

## Plantilla
> <el guion con huecos [entre corchetes], en el idioma del usuario, listo para llenar>

## Relacionado
[[<base>/guiones/_index|Inspo de guiones]] · Desglose visual: [[<nota visual>]]
```
