
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
    os.getenv("OPENAI_API_KEY")
    or os.getenv("OPENAI_API_KEY_2")
    or os.getenv("OPENAI_API_KEY_3")
)
if not API_KEY:
    raise RuntimeError("Aucune clé API trouvée dans .env (OPENAI_API_KEY).")

# Client OpenAI (SDK >= 1.x)
client = OpenAI(api_key=API_KEY)

IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")   # dall-e-3

IMAGE_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "1024x1024" or "1024x1536" or "1536x1024" or "auto")
# valeurs valides: "1024x1024" | "1024x1536" | "1536x1024" | "auto"

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "mon_image"

# ========== Cuisine italienne ========================= #
OUT_DIR_ITALIEN = BASE_DIR / "dossier_des_JSON_internes/cuisine_italienne"             # dossier de sortie demandé
ITALIEN_JSON = BASE_DIR / "dossier_des_JSON_internes/cuisine_italienne/cuisine_italienne.json"           # chemin du JSON fourni
SORTIE_MAPPING = BASE_DIR / "dossier_des_JSON_internes/cuisine_italienne/generer_toutes_les_images.json" # mapping final {titre: chemin}

# ========== requirements: pip install Pillow (Pour passer de .png àa .jpg) ======================= #
from pathlib import Path
from PIL import Image

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
            prompt="Boudin poêlé aux pommes",
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
        print(f"[CHECK] OK via {kind}. Fichier: {IMAGES_DIR / ('0.jpg' if kind=='url' else '0.png')}")  #or ('0.png' if kind=='url' else '0.jpg')
    except Exception as e:
        print("[CHECK] Échec:", e)

# ========================= Cuisine italienne ========================= #

def lire_cuisine_italienne(json_path: Path):
    """
    Ouvre le fichier JSON et renvoie:
      - data: list[dict]
      - titres: list[str]
      - indices_images: list[int] (valeur 'Image' de chaque entrée si présente, sinon 1..N)
    """
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    titres = []
    indices_images = []
    for i, rec in enumerate(data, start=1):
        titre = rec.get("Titre de la recette", f"Recette {i}")
        # Dans ton JSON, la clé s’appelle "Image" (un entier 1..N)
        idx = rec.get("Image", i)
        titres.append(titre)
        indices_images.append(int(idx))

    return data, titres, indices_images


def generer_image_pour_titre(titre: str):
    """
    Génère une image via l'API en utilisant le titre comme prompt.
    Retourne un tuple ("url", url) ou ("b64", b64_str) ou (None, None) en cas d’erreur.
    """
    prompt = (
        f"Photographie culinaire réaliste, éclairage doux, fond neutre, gros plan appétissant : {titre}. "
        f"Style éditorial magazine food, composition soignée."
    )
    try:
        resp = client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt,
            size=IMAGE_SIZE,
            n=1
        )
        d0 = resp.data[0]

        if getattr(d0, "b64_json", None):
            print('cest avec b-64 que l image a ete generee')
            return ("b64", d0.b64_json)
        if getattr(d0, "url", None):   # cest ici que je decide si je veux en URL ou je bascule en b_64
            print('cest avec URL que l image a ete generee')
            return ("url", d0.url)
      
        print(f"[WARN] Réponse inattendue pour «{titre}»:", d0)
        return (None, None)
    except Exception as e:
        print(f"[ERREUR] Génération pour «{titre}» : {e}")
        return (None, None)


def generer_images_cuisine_italienne():
    """
    1) Lit le JSON 'cuisine_xxxx.json'
    2) Génère une image par titre et la sauve dans 'cuisine_xxxx/'
       - si l'API renvoie une URL: nom = {index}.jpg
       - si l'API renvoie du base64: nom = {index}.png
    3) Écrit le mapping final { titre: 'cuisine_italiennes/{index}.(jpg|png)' } dans generer_toutes_les_images.json
    4) Retourne (titres, indices_images, mapping)
    """
    data, titres, indices = lire_cuisine_italienne(ITALIEN_JSON)

    OUT_DIR_ITALIEN.mkdir(parents=True, exist_ok=True)
    mapping = {}

    for titre, idx in zip(titres, indices):
        kind, value = generer_image_pour_titre(titre)
        if not kind:
            # on skippe mais on garde une trace
            mapping[titre] = None
            continue

        # Sauvegarde selon la logique existante (URL -> .jpg, base64 -> .png)
        if kind == "url":
            telecharger_et_sauvegarder_article(value, idx, OUT_DIR_ITALIEN)
            rel_path = OUT_DIR_ITALIEN.name + f"/{idx}.jpg"
        else:
            sauvegarder_image_b64(value, idx, OUT_DIR_ITALIEN)
            rel_path = OUT_DIR_ITALIEN.name + f"/{idx}.png"

        mapping[titre] = rel_path
        print(f"[OK] {titre} → {rel_path}")

    # Écrit le fichier récapitulatif
    with SORTIE_MAPPING.open("w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Mapping écrit dans {SORTIE_MAPPING}")
    return titres, indices, mapping


def pngs_to_jpgs(out_dir: Path = OUT_DIR_ITALIEN, quality: int = 90,
                 overwrite: bool = True, background=(255, 255, 255)) -> dict:
    """
    Convertit toutes les images *.png d'un dossier en copies *.jpg du même nom.
    - quality: qualité JPEG (1..95)
    - overwrite: True pour écraser les .jpg existants
    - background: couleur RGB pour remplir la transparence (par ex. blanc)

    Retourne un petit rapport: {"created": n, "skipped": m, "errors": [(fichier, msg), ...]}
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    created = 0
    skipped = 0
    errors = []

    for png_path in sorted(out_dir.glob("*.png")):
        jpg_path = png_path.with_suffix(".jpg")

        if jpg_path.exists() and not overwrite:
            skipped += 1
            continue

        try:
            img = Image.open(png_path).convert("RGBA")
            # Si l'image a un canal alpha, on la colle sur un fond uni
            if img.mode in ("RGBA", "LA"):
                bg = Image.new("RGB", img.size, background)  # fond blanc par défaut
                bg.paste(img, mask=img.split()[-1])          # utilise l'alpha comme masque
                rgb = bg
            else:
                rgb = img.convert("RGB")

            rgb.save(jpg_path, format="JPEG", quality=quality, optimize=True)
            created += 1
            print(f"[OK] {png_path.name} -> {jpg_path.name}")
        except Exception as e:
            errors.append((png_path.name, str(e)))
            print(f"[ERREUR] {png_path.name}: {e}")

    return {"created": created, "skipped": skipped, "errors": errors}


# report = pngs_to_jpgs()  # utilise OUT_DIR_ITALIEN par défaut
# print(report)

# generer_images_cuisine_italienne()

_sanity_check_image_api()