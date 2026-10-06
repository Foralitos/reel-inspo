---
name: reel-inspo
description: Desglosa reels de Instagram, TikToks y YouTube Shorts que al usuario le gustaron — cómo están hechos (gancho, tomas medidas, ritmo, tipografía, sonido, receta a robar) y su guion completo por bloques — y los guarda en su vault de Obsidian como notas + tarjetas en dos canvas (reels por formato, guiones por tipo), detectando los patrones de su gusto con el tiempo. Todo local, sin API keys. Úsalo cuando el usuario pegue un link de reel, TikTok o Short, o diga "guarda este reel", "inspo", "desglósalo", "me gustó este reel", "cómo está hecho este video", "qué guion usa".
---

# reel-inspo

El usuario pega un link de reel (opcionalmente con una nota: "me gustó el gancho"). Lo bajas,
**lo ves tú** (lees los cuadros; no hay modelo externo ni API key) y lo archivas en su vault en
dos notas: **cómo se ve** y **qué dice**. Con cada reel se actualizan los conteos y aparecen los
patrones de su gusto.

Idea original: [reel-brain](https://github.com/ImTonyS/reel-brain) de Tony (bot de Telegram +
OpenAI). Esta versión corre dentro de Claude Code, sin Telegram y sin OpenAI.

El objetivo NO es resumir de qué trata el reel. Es entender **cómo está hecho**, para hacer
videos mejores después. Escribe en el idioma del usuario, directo, sin emojis.

`SKILL_DIR` = el directorio base de esta skill (Claude Code lo muestra al cargarla). Los scripts
están en `SKILL_DIR/scripts/` y las plantillas en `SKILL_DIR/references/`.

## 0. Primera vez

```bash
python3 SKILL_DIR/scripts/setup.py --check
```

Si falta algo, el script dice cómo instalarlo. Sin configurar:
1. **Vault**: pregúntale al usuario la ruta de su vault de Obsidian (o cualquier carpeta) y
   corre `python3 SKILL_DIR/scripts/setup.py --vault <ruta>`. Todo cae en `<vault>/10-INSPO/`
   (se cambia con `--base`).
2. **Dependencias**: `ffmpeg`, `yt-dlp` y `whisper.cpp`. En macOS: `brew install ffmpeg yt-dlp
   whisper-cpp`. No las instales sin preguntar.
3. **Modelo de whisper** (~550 MB, una vez): `python3 SKILL_DIR/scripts/setup.py --download-model`.
   Sin modelo funciona igual, pero sin guion.

## 1. Extraer (determinista, local)

```bash
python3 SKILL_DIR/scripts/extraer.py "<url>"
```

Devuelve un manifest JSON (también en `<cache>/<id>/manifest.json`):
- **Metadata**: handle, caption, vistas, likes, fecha y música (Instagram a veces no da vistas
  ni música: pon n/d).
- **Técnico**: resolución, fps y duración.
- **Tomas medidas**: cada corte con su segundo, detectado con ffmpeg. Ritmo: cortes por
  segundo, toma promedio, más corta y más larga.
- **Cuadros**: los del gancho (0.3 s y 1.5 s) y cobertura pareja en el tiempo. El segundo va en
  el nombre del archivo (`fNN_TT.Ts.jpg`).
- **Transcript** con timestamps (whisper.cpp local).

La descarga va **sin sesión**, a propósito. Si Instagram la bloquea (pasa tras varias seguidas),
dilo y pide reintentar luego. **Nunca** uses las cookies del navegador del usuario.

## 2. Ver y analizar

Lee **todos** los cuadros, en orden, junto con las tomas, el transcript y el caption. Para ir
rápido, júntalos en tiras de 6-7 (`ffmpeg -i a.jpg -i b.jpg … -filter_complex "hstack=inputs=N"
tira.jpg`) y lee las tiras. Los dos primeros son el gancho: míralos con más cuidado. Lee el texto
en pantalla verbatim. Si el usuario dejó nota, centra el análisis en eso; su nota gana.

Las cifras de tomas y ritmo son **medidas**: úsalas tal cual. Pero revisa dos trampas:
- **Ráfaga**: varias tomas de <1 s seguidas. Saca cuadros extra en ese rango
  (`ffmpeg -ss <t> -i video.mp4 -frames:v 1 -vf scale=300:-2 x.jpg`). Ahí suele estar la
  edición más deliberada, y el muestreo parejo la pierde.
- **Toma larga (>10 s) con pantalla dividida o panel fijo**: la detección no ve los cambios de
  una sola mitad. Recorta esa zona y muestrea cada ~2 s
  (`-vf "crop=iw:ih*0.36:0:0,scale=300:-2"` para el tercio de arriba). Cuenta los cambios
  reales y dilo en la nota.

La detección también falla con fundidos o cámara en mano. Si los cuadros contradicen el conteo,
dilo.

## 3. Nota visual

Escríbela con la plantilla de `SKILL_DIR/references/nota-reel.md`. Va en
`<vault>/<base>/reels/<formato-slug>/`.

## 4. Nota de guion (si el reel tiene voz)

Escríbela con la plantilla de `SKILL_DIR/references/nota-guion.md`. Va en
`<vault>/<base>/guiones/<tipo-slug>/`. Lleva el guion **completo**, por bloques, con los
recursos que usa y una plantilla con huecos. Cada nota linkea a la otra.

## 5. Canvas

**Orden obligatorio: primero las notas, después el canvas.** Si Obsidian tiene el canvas
abierto y una tarjeta apunta a una nota que todavía no existe, se queda en "could not be found"
aunque la nota aparezca después. Por eso el script no corre si la nota no existe.

```bash
# tarjeta visual con 3-4 capturas (la del gancho primero)
python3 SKILL_DIR/scripts/canvas.py --nota "<base>/reels/<formato-slug>/<nota>.md" \
  --formato "<formato>" --cuadros <cuadro1> <cuadro2> <cuadro3> <cuadro4>

# tarjeta del guion
python3 SKILL_DIR/scripts/canvas.py --seccion guiones \
  --nota "<base>/guiones/<tipo-slug>/<nota>.md" --formato "<tipo>"
```

- Las capturas se copian a `<base>/reels/_capturas/<nota>-N.jpg`, que son los nombres que ya
  pusiste en los embeds.
- Una columna por formato o por tipo.
- Correrlo otra vez con la misma nota la reacomoda, sin duplicarla.

## 6. Índices y patrones

Actualiza `<base>/reels/_index.md` y `<base>/guiones/_index.md` siguiendo
`SKILL_DIR/references/indices.md`. Los **patrones** (algo que aparece 3 o más veces) son lo
que más vale. Cuando un reel nuevo hace subir un conteo, díselo al usuario.

## 7. Responder

Tarjeta corta en el chat:
- Título, formato y tipo de guion.
- El gancho verbatim.
- La receta en 2-3 líneas.
- Los patrones que subieron.
- Las rutas de las dos notas.

Si el usuario pega varios links: extrae todos en paralelo, analiza uno por uno y actualiza los
índices una sola vez al final.

## Notas
- Los videos y cuadros originales quedan en el cache (`~/.cache/reel-inspo/`), fuera del
  vault. Solo las 3-4 capturas elegidas entran al vault. El cache se puede borrar cuando sea.
- Si el usuario tiene reglas propias del vault (frontmatter obligatorio, preámbulos, bitácora
  de cambios), síguelas encima de estas plantillas.
