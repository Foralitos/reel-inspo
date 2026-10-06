#!/usr/bin/env python3
"""Mete un reel (o su guion) ya analizado al canvas de inspo del vault.

Uso: python3 canvas.py [--seccion reels|guiones] --nota <ruta-nota-en-vault.md> \
        --formato "<columna>" [--cuadros f00.jpg f03.jpg f05.jpg] [--texto "tarjeta corta"]

--seccion reels (default): canvas <base>/reels/reels.canvas, columna = formato visual.
--seccion guiones: canvas <base>/guiones/guiones.canvas, columna = tipo de guion,
  tarjeta más alta y sin cuadros (es texto).

- Copia los cuadros a <base>/reels/_capturas/<slug-nota>-N.jpg
- Agrega al canvas: la tarjeta de la nota (nodo file) + los cuadros al lado,
  en la columna del formato (una columna por formato, como reel-brain agrupa por tema).
- Imprime los nombres de las capturas para embeberlas en la nota.
Basado en vault.py de reel-brain (github.com/ImTonyS/reel-brain) de Tony.
"""
import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config  # noqa: E402

CFG = config.load()
VAULT = Path(CFG["vault"])
B = CFG["base"]
CAPTURAS = f"{B}/reels/_capturas"
SECCIONES = {
    "reels": {"canvas": f"{B}/reels/reels.canvas", "card_h": 520,
              "titulo": "# Inspo de reels\nReels que me gustaron, desglosados por cómo están hechos "
                        "(gancho, ritmo, tomas, sonido). Una columna por formato. "
                        f"Skill: `reel-inspo`. Guiones: [[{B}/guiones/_index]]"},
    "guiones": {"canvas": f"{B}/guiones/guiones.canvas", "card_h": 760,
                "titulo": "# Inspo de guiones\nLo que dicen los reels que me gustaron, palabra por palabra, "
                          "partido en bloques. Una columna por tipo de guion. "
                          f"Skill: `reel-inspo`. Visual: [[{B}/reels/_index]]"},
}

COL_W = 1000      # ancho de cada columna
CARD_W = 420
IMG_W, IMG_H = 170, 302  # 9:16
GAP = 40


def slug(text, n=40):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:n].strip("-") or "x"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nota", required=True, help="ruta relativa al vault de la nota .md")
    ap.add_argument("--formato", required=True, help="columna del canvas (ej. 'demo de producto')")
    ap.add_argument("--cuadros", nargs="*", default=[])
    ap.add_argument("--seccion", choices=list(SECCIONES), default="reels")
    ap.add_argument("--texto", default="", help="tarjeta de texto opcional en vez de la nota")
    a = ap.parse_args()
    sec = SECCIONES[a.seccion]
    CANVAS, CARD_H = sec["canvas"], sec["card_h"]

    nota = a.nota.removeprefix(str(VAULT) + "/")
    if not a.texto and not (VAULT / nota).exists():
        # Obsidian cachea "could not be found" si el canvas apunta a una nota que aún no existe.
        raise SystemExit(f"Escribe la nota primero: no existe {nota}")
    base = Path(nota).stem
    names = []
    if a.cuadros:
        (VAULT / CAPTURAS).mkdir(parents=True, exist_ok=True)
    for i, f in enumerate(a.cuadros[:4], 1):
        name = f"{base}-{i}.jpg"
        (VAULT / CAPTURAS / name).write_bytes(Path(f).read_bytes())
        names.append(name)

    path = VAULT / CANVAS
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas = json.loads(path.read_text()) if path.exists() else {"nodes": [], "edges": []}
    nodes = canvas["nodes"]
    if not nodes:
        nodes.append({"id": "inspo-title", "type": "text", "x": 0, "y": -260, "width": 700, "height": 180,
                      "text": sec["titulo"]})

    # Si el reel ya estaba, quítalo para re-colocarlo (re-análisis).
    rid = f"r-{slug(base, 50)}"
    nodes[:] = [n for n in nodes if not n["id"].startswith(rid)]

    col_id = f"col-{slug(a.formato, 30)}"
    col = next((n for n in nodes if n["id"] == col_id), None)
    if not col:
        ncols = sum(1 for n in nodes if n["id"].startswith("col-"))
        col = {"id": col_id, "type": "text", "x": ncols * (COL_W + GAP), "y": 0,
               "width": COL_W - GAP, "height": 80, "text": f"## {a.formato}"}
        nodes.append(col)
    members = [n for n in nodes if n["id"].startswith("r-") and n.get("x", 0) >= col["x"]
               and n.get("x", 0) < col["x"] + COL_W]
    y = max([n["y"] + n["height"] for n in members], default=col["y"] + col["height"]) + GAP

    card = ({"id": rid, "type": "text", "text": a.texto} if a.texto
            else {"id": rid, "type": "file", "file": nota})
    card.update(x=col["x"], y=y, width=CARD_W, height=CARD_H)
    nodes.append(card)
    for i, n in enumerate(names):
        nodes.append({"id": f"{rid}-img{i}", "type": "file", "file": f"{CAPTURAS}/{n}",
                      "x": col["x"] + CARD_W + 20 + (i % 3) * (IMG_W + 10),
                      "y": y + (i // 3) * (IMG_H + 10), "width": IMG_W, "height": IMG_H})

    path.write_text(json.dumps(canvas, ensure_ascii=False, indent="\t"))
    print(json.dumps({"canvas": CANVAS, "nodo": rid, "columna": a.formato, "capturas": names,
                      "at": datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
