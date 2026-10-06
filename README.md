# reel-inspo

Ver reels en la cama no es tiempo perdido, es investigación que se te olvida. **reel-inspo**
la guarda.

Le pegas a Claude Code el link de un reel, TikTok o YouTube Short que te gustó, y él:

1. lo baja y **mide** cómo está editado (cada corte con su segundo, el ritmo y las ráfagas),
2. **lo ve** cuadro por cuadro y lo transcribe,
3. lo guarda en tu vault de Obsidian en dos notas:
   - **cómo se ve**: gancho, storyboard medido, tipografía, color, sonido y la receta que te robas;
   - **qué dice**: el guion completo por bloques, los recursos que usa y una plantilla con huecos
     para reusarlo.
4. Lo acomoda en dos canvas, uno de **reels por formato** y otro de **guiones por tipo**.
5. Con el tiempo te muestra tu gusto: *"3er reel con palabra clave gigante: ya es parte de tu
   estilo"*.

Todo corre en tu máquina. No necesita API keys ni bot, y nunca usa tu sesión de Instagram.

## Instalar

En Claude Code:

```
/plugin marketplace add Foralitos/reel-inspo
/plugin install reel-inspo@reel-inspo
```

Dependencias (macOS):

```bash
brew install ffmpeg yt-dlp whisper-cpp
```

En Linux: `ffmpeg` de tu gestor de paquetes, `pip install yt-dlp` y
[whisper.cpp](https://github.com/ggml-org/whisper.cpp).

La primera vez, Claude te va a preguntar dónde está tu vault y va a bajar el modelo de whisper
(~550 MB, una sola vez). También lo puedes hacer a mano:

```bash
python3 skills/reel-inspo/scripts/setup.py --vault ~/mi-vault --download-model
```

## Usar

Pega el link en Claude Code y, si quieres, di por qué te gustó:

```
https://www.instagram.com/reel/XXXX/  me gustó cómo pone el texto detrás de ella
```

Funciona con varios links a la vez.

## Qué queda en tu vault

```
10-INSPO/
  reels/
    _index.md            tabla + conteos + patrones de tu estilo
    reels.canvas         tablero visual, una columna por formato
    _capturas/           3-4 cuadros por reel
    storytelling/  lista-top/  tutorial-rapido/  ...
  guiones/
    _index.md            tabla + recursos + patrones
    guiones.canvas       una columna por tipo de guion
    historia-personal/  lista-top/  tutorial-hacks/  ...
```

La carpeta `10-INSPO` se cambia con `setup.py --base <carpeta>`.

## Para qué sirve después

Las notas están escritas en el idioma de un editor de video: gancho, tomas con duración, tono,
transiciones y sonido. Así, cualquier skill que haga videos (por ejemplo `/brag`) o que escriba
guiones las puede leer y basarse en algo que de verdad te gustó.

## Créditos

La idea y la base del pipeline (bajar con `yt-dlp`, cuadros por cambio de escena con `ffmpeg`,
el perfil de gusto por conteo de tags) vienen de [reel-brain](https://github.com/ImTonyS/reel-brain)
de **Tony** ([@ImTonyS](https://github.com/ImTonyS)), hecho en el DevDay Exchange Community Hack
Day de Taipei (2026-10-04). reel-inspo lo pasa a una skill de Claude Code, sin Telegram ni
OpenAI, mide las tomas en lugar de estimarlas y agrega la sección de guiones.
