"""Configuración compartida: dónde está tu vault y dónde viven las herramientas.

Se guarda en ~/.config/reel-inspo/config.json (la crea `setup.py --vault <ruta>`).
"""
import json
import shutil
import sys
from pathlib import Path

CONFIG = Path.home() / ".config" / "reel-inspo" / "config.json"
DEFAULTS = {
    "vault": None,                 # ruta absoluta al vault de Obsidian (o cualquier carpeta)
    "base": "10-INSPO",            # carpeta dentro del vault
    "whisper_model": str(Path.home() / ".cache" / "whisper" / "ggml-large-v3-turbo-q5_0.bin"),
    "cache": str(Path.home() / ".cache" / "reel-inspo"),
}


def load(required=True):
    cfg = dict(DEFAULTS)
    if CONFIG.exists():
        cfg.update(json.loads(CONFIG.read_text()))
    if required and not cfg["vault"]:
        sys.exit("reel-inspo no está configurado. Corre: python3 setup.py --vault <ruta-a-tu-vault>")
    return cfg


def save(cfg):
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2))


def ytdlp_cmd():
    """yt-dlp como binario o como módulo de python, lo que haya."""
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    try:
        import yt_dlp  # noqa: F401
        return [sys.executable, "-m", "yt_dlp"]
    except ImportError:
        return None


def whisper_cmd():
    """Binario de whisper.cpp (brew lo instala como whisper-cli; versiones viejas, whisper-cpp)."""
    return next((n for n in ("whisper-cli", "whisper-cpp") if shutil.which(n)), None)
