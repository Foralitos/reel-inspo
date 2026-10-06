#!/usr/bin/env python3
"""Reel -> video + cortes medidos + cuadros clave + transcript. Todo local, sin API keys.

Uso: python3 extraer.py <url> [--out DIR]
Imprime un manifest JSON (también lo deja en DIR/manifest.json).
Basado en pipeline.py de reel-brain (github.com/ImTonyS/reel-brain) de Tony.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config  # noqa: E402

CFG = config.load(required=False)
YTDLP = config.ytdlp_cmd()
WHISPER = config.whisper_cmd()
WHISPER_MODEL = Path(CFG["whisper_model"])
MAX_SECONDS = 240
SCENE_THRESHOLD = 0.3
MAX_FRAMES = 8


def run(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)


def slug(text, n=40):
    import unicodedata
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:n].strip("-") or "reel"


def download(url, workdir):
    if not YTDLP:
        sys.exit("Falta yt-dlp. Corre: python3 setup.py --check")
    info = run([*YTDLP, "-J", "--no-warnings", url])
    if info.returncode != 0:
        sys.exit(f"yt-dlp no pudo leer el reel: {info.stderr.strip()[-400:]}")
    meta = json.loads(info.stdout)
    if (meta.get("duration") or 0) > MAX_SECONDS:
        sys.exit(f"El video dura {meta['duration']}s, más de {MAX_SECONDS}s.")
    r = run([*YTDLP, "--no-warnings", "-q", "-f", "mp4/bestvideo+bestaudio/best",
             "--merge-output-format", "mp4", "-o", workdir / "video.%(ext)s", url])
    if r.returncode != 0:
        sys.exit(f"yt-dlp no pudo bajar el video: {r.stderr.strip()[-400:]}")
    video = next(workdir.glob("video.*"))
    return video, {
        "url": url,
        "id": meta.get("id"),
        "plataforma": meta.get("extractor_key"),
        "handle": meta.get("channel") or meta.get("uploader_id") or meta.get("uploader") or "",
        "autor": meta.get("uploader") or "",
        "caption": (meta.get("description") or "")[:1500],
        "duracion": meta.get("duration"),
        "vistas": meta.get("view_count"),
        "likes": meta.get("like_count"),
        "fecha_publicado": meta.get("upload_date"),
        "musica": " - ".join(x for x in (meta.get("artist") or meta.get("creator"), meta.get("track")) if x) or None,
    }


def probe(video):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=width,height,r_frame_rate:format=duration", "-of", "json", video])
    d = json.loads(r.stdout)
    s = d["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return {"ancho": s["width"], "alto": s["height"], "fps": round(int(num) / int(den), 2),
            "duracion": float(d["format"]["duration"])}


def cuts(video, duration):
    """Timestamps de cada cambio de escena -> tomas con duración real."""
    r = run(["ffmpeg", "-i", video, "-vf", f"select='gt(scene,{SCENE_THRESHOLD})',showinfo",
             "-f", "null", "-"])
    times = [float(t) for t in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    bounds = [0.0] + [t for t in times if t > 0.15] + [duration]
    shots = [{"inicio": round(a, 2), "fin": round(b, 2), "dura": round(b - a, 2)}
             for a, b in zip(bounds, bounds[1:]) if b - a > 0.05]
    return shots


def frame_at(video, t, out):
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
         "-vf", "scale=540:-2,format=yuvj420p", "-q:v", "3", out])
    return out if out.exists() else None


def keyframes(video, shots, duration, workdir):
    """Gancho (0.3s y 1.5s) + cobertura pareja en el tiempo, anclada a las tomas.

    Una toma larga (talking head de 26 s) cambia por dentro aunque no haya corte:
    se muestrea cada ~6 s. Los bursts de cortes rápidos se representan con 1-2 cuadros.
    """
    hook = [0.3, min(1.5, duration * 0.3)]
    budget = max(MAX_FRAMES, min(14, int(duration / 6) + 4)) - len(hook)
    cands = []
    for s in shots:
        n = max(1, int(s["dura"] // 6))
        cands += [s["inicio"] + s["dura"] * (k + 0.5) / n for k in range(n)]
    cands = sorted(t for t in cands if t > 2.0)
    if len(cands) > budget:  # elige el candidato más cercano a cada punto parejo en el tiempo
        span = duration - 2.0
        targets = [2.0 + span * (k + 0.5) / budget for k in range(budget)]
        cands = sorted({min(cands, key=lambda c: abs(c - t)) for t in targets})
    times = hook + cands
    frames = []
    for i, t in enumerate(sorted(set(round(t, 2) for t in times))):
        f = frame_at(video, t, workdir / f"f{i:02d}_{t:05.1f}s.jpg")
        if f:
            frames.append({"t": t, "archivo": str(f)})
    return frames


def audio_info(video, workdir):
    wav = workdir / "audio.wav"
    r = run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav])
    if r.returncode != 0 or not wav.exists():
        return None, {"tiene_audio": False}
    vol = run(["ffmpeg", "-i", wav, "-af", "volumedetect", "-f", "null", "-"]).stderr
    mean = re.search(r"mean_volume: ([-\d.]+)", vol)
    return wav, {"tiene_audio": True, "volumen_medio_db": float(mean.group(1)) if mean else None}


def transcribe(wav, workdir):
    if not wav or not WHISPER or not WHISPER_MODEL.exists():
        return {"texto": "", "segmentos": [],
                "aviso": "sin audio, sin whisper.cpp o sin modelo (python3 setup.py --check)"}
    base = workdir / "transcript"
    r = run([WHISPER, "-m", WHISPER_MODEL, "-f", wav, "-l", "auto", "-oj", "-of", base, "-np"])
    j = Path(f"{base}.json")
    if r.returncode != 0 or not j.exists():
        return {"texto": "", "segmentos": [], "aviso": r.stderr.strip()[-300:]}
    data = json.loads(j.read_text())
    segs = [{"t": round(s["offsets"]["from"] / 1000, 1), "texto": s["text"].strip()}
            for s in data.get("transcription", []) if s["text"].strip()]
    return {"idioma": data.get("result", {}).get("language"),
            "texto": " ".join(s["texto"] for s in segs), "segmentos": segs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default=CFG["cache"])
    a = ap.parse_args()

    url = a.url.split("?")[0]
    workdir = Path(a.out) / slug(url.rstrip("/").split("/")[-1], 30)
    workdir.mkdir(parents=True, exist_ok=True)
    for old in workdir.glob("f*.jpg"):
        old.unlink()

    video, meta = download(url, workdir)
    tec = probe(video)
    shots = cuts(video, tec["duracion"])
    frames = keyframes(video, shots, tec["duracion"], workdir)
    wav, audio = audio_info(video, workdir)
    transcript = transcribe(wav, workdir)

    durs = [s["dura"] for s in shots]
    manifest = {
        **meta,
        "tecnico": tec,
        "ritmo": {
            "tomas": len(shots),
            "cortes_por_segundo": round((len(shots) - 1) / tec["duracion"], 2) if tec["duracion"] else 0,
            "toma_promedio_s": round(sum(durs) / len(durs), 2) if durs else None,
            "toma_mas_corta_s": min(durs) if durs else None,
            "toma_mas_larga_s": max(durs) if durs else None,
        },
        "tomas": shots,
        "cuadros": frames,
        "audio": audio,
        "transcript": transcript,
        "workdir": str(workdir),
        "video": str(video),
    }
    (workdir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    print(json.dumps(manifest, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
