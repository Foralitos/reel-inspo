#!/usr/bin/env python3
"""Configura reel-inspo y revisa que todo esté instalado.

  python3 setup.py --vault ~/mi-vault      # guarda la ruta del vault (una vez)
  python3 setup.py --check                 # solo revisa dependencias
  python3 setup.py --download-model        # baja el modelo de whisper (~550 MB)
  python3 setup.py --base 10-INSPO         # cambia la carpeta dentro del vault
"""
import argparse
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config  # noqa: E402

MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin"
INSTALL_HINTS = {
    "ffmpeg": "macOS: brew install ffmpeg · Linux: sudo apt install ffmpeg",
    "yt-dlp": "macOS: brew install yt-dlp · cualquiera: python3 -m pip install -U yt-dlp",
    "whisper.cpp": "macOS: brew install whisper-cpp · Linux: https://github.com/ggml-org/whisper.cpp",
}


def check(cfg):
    ok = True
    rows = [
        ("ffmpeg", bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))),
        ("yt-dlp", config.ytdlp_cmd() is not None),
        ("whisper.cpp", config.whisper_cmd() is not None),
    ]
    for name, found in rows:
        print(f"{'ok ' if found else 'FALTA'}  {name}" + ("" if found else f"   → {INSTALL_HINTS[name]}"))
        ok &= found or name == "whisper.cpp"  # sin whisper funciona, solo sin transcript
    model = Path(cfg["whisper_model"])
    print(f"{'ok ' if model.exists() else 'FALTA'}  modelo whisper ({model})"
          + ("" if model.exists() else "   → python3 setup.py --download-model"))
    vault = cfg.get("vault")
    print(f"{'ok ' if vault and Path(vault).is_dir() else 'FALTA'}  vault: {vault or 'sin configurar'}"
          + ("" if vault else "   → python3 setup.py --vault <ruta>"))
    if vault:
        print(f"      notas en: {Path(vault) / cfg['base']}/reels  y  {cfg['base']}/guiones")
    return ok and bool(vault)


def download_model(cfg):
    dest = Path(cfg["whisper_model"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    print(f"Bajando {MODEL_URL}\n  → {dest} (~550 MB)")
    if shutil.which("curl"):  # curl reanuda si se corta
        r = subprocess.run(["curl", "-L", "-C", "-", "--retry", "5", "-o", str(tmp), MODEL_URL])
        if r.returncode != 0:
            sys.exit("Se cortó la descarga. Vuelve a correr el comando: reanuda donde se quedó.")
    else:
        urllib.request.urlretrieve(MODEL_URL, tmp)
    tmp.rename(dest)
    print("Listo.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault")
    ap.add_argument("--base")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--download-model", action="store_true")
    a = ap.parse_args()

    cfg = config.load(required=False)
    if a.vault:
        v = Path(a.vault).expanduser().resolve()
        if not v.is_dir():
            sys.exit(f"No existe la carpeta {v}")
        cfg["vault"] = str(v)
    if a.base:
        cfg["base"] = a.base.strip("/")
    if a.vault or a.base:
        config.save(cfg)
        print(f"Guardado en {config.CONFIG}")
    if a.download_model:
        download_model(cfg)
    sys.exit(0 if check(cfg) else 1)


if __name__ == "__main__":
    main()
