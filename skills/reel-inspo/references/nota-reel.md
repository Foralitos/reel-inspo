# Plantilla — nota visual del reel

Ruta: `<vault>/<base>/reels/<formato-slug>/<YYYY-MM-DD>-<handle>-<slug>.md`

`<base>` sale de la config (default `10-INSPO`). La subcarpeta es el formato en kebab-case
(`storytelling/`, `demo-de-producto/`, `tutorial-rapido/`…); créala si no existe.

Las capturas se llaman `<nombre-de-esta-nota-sin-.md>-1.jpg` … `-4.jpg`, en el orden en que las
pases a `canvas.py --cuadros`. Embébelas por nombre (Obsidian las encuentra solas).

```markdown
---
type: inspo-reel
date: YYYY-MM-DD
tags: [inspo, reel, <formato-slug>, <estilo-slugs>]
fuente: <url>
autor: "@handle"
plataforma: instagram|tiktok|youtube
duracion-s: <n>
tomas: <n>
cortes-por-segundo: <n>
formato: "<formato>"
tono: <default|polished|yc-parody|chaotic|deadpan|cinematic|app-store|otro: ...>
estilo: [<2-6 tags visuales reusables>]
vistas: <n o n/d>
likes: <n o n/d>
publicado: YYYY-MM-DD
guion: "[[<base>/guiones/<tipo-slug>/<nota de guion>]]"
---

# <título corto: qué es, no de qué trata>

## Contexto
Reel de @handle guardado el YYYY-MM-DD como inspiración de cómo hacer videos. Desglosado por
reel-inspo (cuadros vistos + tomas medidas con ffmpeg + transcript whisper local).
<Nota del usuario si hubo. Si parece publicidad, dilo.>

![[<base-nota>-1.jpg|160]] ![[<base-nota>-2.jpg|160]] ![[<base-nota>-3.jpg|160]] ![[<base-nota>-4.jpg|160]]

## Por qué lo guardé
<nota del usuario verbatim, o "_Sin nota._">

## Gancho (0-2 s)
- Imagen: <qué se ve en el primer cuadro>
- Texto en pantalla: "<verbatim>"
- Voz: "<verbatim de los primeros segundos o 'sin voz'>"
- Por qué engancha: <una línea>

## Storyboard medido
| # | Tiempo | Dura | Qué pasa | Texto en pantalla | Transición |
|---|---|---|---|---|---|

## Ritmo
<tomas, cortes/s, toma promedio; dónde acelera o frena y para qué. Si el promedio engaña
(ráfaga, pantalla dividida), dilo.>

## Lenguaje visual
- Tipografía: <familia aproximada, peso, tamaño relativo, posición, cuánto dura en pantalla>
- Color: <paleta>
- Cámara / composición: <plano, movimiento, encuadre 9:16>
- Cómo muestra el producto/tema: <UI real, screen recording, mano, b-roll, avatar...>
- Movimiento/animación: <zooms, kinetic type, máscaras...>

## Sonido
<voz o no, música (si viene en metadata), sfx, volumen medio, cómo se sincroniza con los cortes>

## Receta (qué me robo)
<2-5 bullets accionables y reusables. Nunca "copiar el objeto que sale".>

## Para hacer mi video
- Tono: <preset más cercano y por qué>
- Gancho reusable: <plantilla con hueco: "X hace Y en Z segundos">
- Estructura: <hook Ns → ... → outro Ns>
- En un video de 20 s: <cómo se vería esta receta aplicada a un lanzamiento corto>

## Relacionado
[[<base>/reels/_index|Inspo de reels]] · Guion completo: [[<nota de guion>]] · <otras inspo con mismo formato/estilo>
```

Formatos de arranque (crea otros si no encaja): demo de producto, tutorial rápido,
antes/después, lista/top, storytelling, dato/gancho de cifra, meme/humor, behind the scenes,
talking head, motion graphics puro, transición/edición showcase.

Los tonos son los presets de video corto más comunes (los mismos que usa la skill brag):
`default` punchy · `polished` sobrio, tomas largas · `yc-parody` deadpan startup · `chaotic`
rápido y en mayúsculas · `deadpan` seco · `cinematic` tráiler · `app-store` tarjetas por feature.
