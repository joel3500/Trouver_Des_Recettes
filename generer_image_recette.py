
import os
import json
import base64  # (utile si jamais tu veux basculer en b64)
import requests
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# ========================= Configuration ========================= #

load_dotenv()

API_KEY = (
    os.getenv("OPENAI_API_KEY_1")
    or os.getenv("OPENAI_API_KEY_2")
    or os.getenv("OPENAI_API_KEY_3")
)
if not API_KEY:
    raise RuntimeError("Aucune clé API trouvée dans .env (OPENAI_API_KEY).")

# Client OpenAI (SDK >= 1.x)
client = OpenAI(api_key=API_KEY)

IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

IMAGE_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "1024x1024" or "1024x1536" or "1536x1024" or "auto")
# valeurs valides: "1024x1024" | "1024x1536" | "1536x1024" | "auto"

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images_poissons"

# ===================== Téléchargement/sauvegarde ===================== #

def telecharger_et_sauvegarder_article(url_image: str, i: int, out_dir: Path):
    r = requests.get(url_image, timeout=60)
    print(url_image)   ## ICI on n'a pas d'URL, donc ce PRINT N'IMPRIME RIEN
    if r.status_code == 200:
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{i}.jpg"
        with path.open("wb") as f:
            f.write(r.content)
        print(f"[OK] Image (URL) : {path}")
    else:
        print(f"[ERREUR] Téléchargement URL : HTTP {r.status_code}")


def sauvegarder_image_b64(b64_str: str, i: int, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{i}.png"
    with path.open("wb") as f:
        f.write(base64.b64decode(b64_str))
    print(f"[OK] Image (base64) : {path}")

# ========================= Teste ======================================= #

def _sanity_check_image_api():
    kind, value = ("", "")
    try:
        resp = client.images.generate(
            model=IMAGE_MODEL,
            prompt="Foutou banane èa la sauce graine",
            size=IMAGE_SIZE,
            n=1
        )
        d0 = resp.data[0]
        url = getattr(d0, "url", None)
        b64 = getattr(d0, "b64_json", None)

        if url :
            kind, value = "url", d0.url
            telecharger_et_sauvegarder_article(value, 0, IMAGES_DIR)
            
        else:
            kind, value = "b64", d0.b64_json
            sauvegarder_image_b64(value, 0, IMAGES_DIR)
        print(f"[CHECK] OK via {kind}. Fichier: {IMAGES_DIR / ('0.jpg' if kind=='url' else '0.png')}")
    except Exception as e:
        print("[CHECK] Échec:", e)