
#======================================================================================#
#     Libraires                                                                        #
#======================================================================================#

#=== Flask ============================================================================#

from flask import Flask, redirect, render_template, request, jsonify, send_from_directory, send_file
from datetime import datetime 
import json, os
from datetime import datetime                
import openai

from openai import OpenAI

from flask_cors import CORS
from dotenv import load_dotenv

from pathlib import Path

# routes_regimes.py
from flask import Blueprint, current_app

#=== FIN DES LIBRAIRIES    =================================================================#
# Initialisation de notre Controleur (Initiaalisation de Flask)

#===========================================================================================#

main = Flask(__name__)
CORS(main) 

#==========   CONSTRUCTEUR DU FLASK    =====================================================#

# Configuration des clés API

load_dotenv()
key =  os.getenv("OPENAI_API_KEY")
openai.api_key = key

client = OpenAI()

#===========================================================================================#
# chemins robustes, indépendants du cwd
#===========================================================================================#

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "dossier_des_JSON_internes"
DATA_DIR.mkdir(parents=True, exist_ok=True)   # crée le dossier s’il n’existe pas

REGIMES_JSON = BASE_DIR / "dossier_des_JSON_internes" / "les_types_de_regimes.json"
ALIMENTS_JSON = BASE_DIR / "dossier_des_JSON_internes" / "meilleurs_et_pires_aliments.json"

# fichiers
SUIVIS_FILE = DATA_DIR / "suivis.json"
TRANSIT_IA_FILE = DATA_DIR / "transit_IA.json"
CUISINE_LIBRE_FILE = DATA_DIR / "from_scrappy_cuisinelibre_org.json"

#===========================================================================================#
#     Quelques FONCTIONS UTILES                                                              #
#===========================================================================================#

# === Carrousel (images de régions) ============================================
CAROUSEL_DIR = BASE_DIR / "static" / "img" / "caroussel"
ALLOWED_IMG = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

def build_carousel_items():
    """
    Retourne une liste de dicts:
      { 'slug': 'cuisine_africaine', 'display': 'cuisine africaine', 'url': '/static/img/caroussel/cuisine_africaine.jpeg' }
    """
    items = []
    if CAROUSEL_DIR.exists():
        for p in sorted(CAROUSEL_DIR.iterdir()):
            if p.is_file() and p.suffix.lower() in ALLOWED_IMG:
                slug = p.stem  # 'cuisine_africaine'  (sans extension)
                display = slug.replace("_", " ")
                url = f"/static/img/caroussel/{p.name}"
                items.append({"slug": slug, "display": display, "url": url})
    return items


def register_region_routes(app):
    """
    Crée dynamiquement une route par image:
      'cuisine_africaine.jpeg' -> /cuisine_africaine  (endpoint: region_cuisine_africaine)
    Rendu: on réutilise index.html en lui passant selected_region.
    """
    for item in build_carousel_items():
        slug = item["slug"]
        display = item["display"]
        endpoint_name = f"region_{slug}"

        def _view(slug=slug, display=display):
            # Ici tu peux un jour filtrer des recettes selon la région si tu veux.
            return render_template(
                "index.html",
                selected_region=display.title(),
                carousel_images=build_carousel_items()
            )

        # Évite de redéclarer si code rechargé en debug
        if endpoint_name not in app.view_functions:
            app.add_url_rule(f"/{slug}", endpoint=endpoint_name, view_func=_view)


# Récupérer la date actuelle
def date_de_requette():
    current_date = datetime.now().isoformat()
    print(current_date)
    print("\n\tReformatage de la date en cours...\n")
    print("\tRemplacement du T par un tirait...\n")
    t1 = current_date.replace("T"," / ")
    print("\tRetrait des millisecondes...\n")
    t2 = t1.split(".")[0]
    print(t2)
    return t2


# Nettoyer du gros texte comme par exemple la liste des ingrésiens, ou même les étaes de préparation. 
def nettoyer_texte(t):
    #print("Nettoyage du texte en cours...\n")
    #print("\tRetrait des chaînes bizarres xa0...\n")
    t1 = t.replace("\xa0", " ")  # Remplace les espaces insécables par des espaces normaux
    #print("\tRetrait des anti-slash de retour à la ligne...\n")
    t2 = t1.replace("\n", " ")
    #print("\tRetrait des espaces inutiles...\n")
    t3 = t2.strip()
    return t3

def sauvegarder_ingrediens_dans_JSON(la_date, liste):
    """Append {'date': ..., 'ingrediens': [...]} dans suivis.json, en créant le dossier/fichier si besoin."""
    # Charger l'existant (si fichier corrompu ou vide -> liste vide)
    try:
        data = json.loads(SUIVIS_FILE.read_text(encoding="utf-8")) if SUIVIS_FILE.exists() and SUIVIS_FILE.stat().st_size > 0 else []
    except json.JSONDecodeError:
        data = []

    data.append({'date': la_date, 'ingrediens': liste})

    # Sauvegarder
    SUIVIS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
    print("Sauvegarde de la requête dans JSON terminée.")

def verifier_si_100_100_correspondance(liste_des_ingrediens_rentres, liste_ingrediens_json):
    #noms = ['Alice', 'Bonnet', 'Coline', 'David', 'geremie']
    #phrases = ['alice mange bien', 'rené a un bonnet', 'la coline est haute', 'david contre Goliath', 'suzanne et geremie']
    boolean = False   
    
    # Vérifier si chaque élément de la liste noms est présent dans au moins une phrase
    noms_present = all(any(ingredien_rentre.lower() in ingredien_json.lower() for ingredien_json in liste_ingrediens_json) for ingredien_rentre in liste_des_ingrediens_rentres)

    # Vérifier si chaque phrase contient au moins un des noms
    phrases_couvertes = all(any(ingredien_rentre.lower() in ingredien_json.lower() for ingredien_rentre in liste_des_ingrediens_rentres) for ingredien_json in liste_ingrediens_json)

    # Résultat final
    boolean = noms_present and phrases_couvertes

    # Affichage du résultat
    print(f"Tous les noms sont présents et toutes les phrases ont un correspondant : {boolean}")
    return boolean
"""
Keyword arguments : 
         meme principe que tantôt. À la différence que beaucoup d'éléments en input : [ Oignon - Oeuf - Tomate - Piment - ... ]
         Je peux faire des Omelettes avec Oignon et oeuf UNIQUEMENT. 
         Je ne veux pas que mes utilisateurs rattent des menus parcequ'ils ont ajouté trop d'éléments.
         Ils devraient pouvoir extraire des menus contenant : [ Oeuf et Oignon ]. 
         Autrement dit : On doit extraire des Menu contenu partie ou totalité des ingrédiens rentrés ==> Très important comme considération

Return : return_description
"""
def verifier_si_JSON_correspondance(liste_des_ingrediens_rentres, liste_ingrediens_json):
    #noms = ['Alice', 'Bonnet', 'Coline', 'David', 'geremie']
    #phrases = ['alice mange bien', 'rené a un bonnet', 'la coline est haute', 'david contre Goliath', 'suzanne et geremie']
    boolean = False

    # Vérifier si chaque phrase contient au moins un des ingrediens
    phrases_couvertes = all(any(ingredien_rentre.lower() in ingredien_json.lower() for ingredien_rentre in liste_des_ingrediens_rentres) for ingredien_json in liste_ingrediens_json)

    # Résultat final
    boolean = phrases_couvertes

    # Affichage du résultat
    print(f"Tous les noms sont présents et toutes les phrases ont un correspondant : {boolean}")
    return boolean

"""
    Vérifie si le pourcentage de correspondance entre les ingrédients rentrés et ceux du JSON dépasse un seuil donné.
    Arguments:
        liste_des_ingrediens_rentres (list): Liste des ingrédients donnés par l'utilisateur.
        liste_ingrediens_json (list): Liste des ingrédients disponibles dans le JSON.
        seuil (float): Seuil de correspondance (entre 0 et 1).
    Retours:
        bool: True si le pourcentage de correspondance dépasse le seuil, False sinon.
    """
def pourcentage_correspondance(liste_des_ingrediens_rentres, liste_ingrediens_json, seuil):
    
    # Calcul du nombre d'ingrédients correspondants
    correspondances = sum(
        any(ingredien_rentre.lower() in ingredien_json.lower() for ingredien_json in liste_ingrediens_json)
        for ingredien_rentre in liste_des_ingrediens_rentres
    )

    # Calcul du pourcentage de correspondance
    pourcentage = correspondances / len(liste_des_ingrediens_rentres) if liste_des_ingrediens_rentres else 0

    # Vérification si le pourcentage dépasse le seuil
    return pourcentage >= seuil

def chercher_correspondance_dans_fichier(input_file, liste_des_ingrediens_rentres):
    with open(input_file, "r", encoding="utf-8") as f:
         recipes = json.load(f)

    # Filtrer les recettes avec uniquement les ingrédients envoyés par le formulaire
    filtered_recipes = []

    for recipe in recipes:
        liste_ingrediens_json = recipe['recette']['Ingrediens']
        print(recipe['recette']['Ingrediens'])
        print("\n")

        # On verifie s'il y a des recettes qui contiennent uniquement tous les ingrédiens rentrés.
        bool1 = verifier_si_100_100_correspondance(liste_des_ingrediens_rentres, liste_ingrediens_json)
        if bool1 :
            filtered_recipes.append(recipe)
            print(recipe['recette']['Ingrediens'])
            print("\n")
    
        # On verifie s'il y a des recettes qui sont constitués uniquement de quelques ingrédiens rentrés. Dans ce cas on serait capable de le cuisiner.
        bool2 = verifier_si_JSON_correspondance(liste_des_ingrediens_rentres, liste_ingrediens_json)
        if bool2 :
            filtered_recipes.append(recipe)
            print(recipe['recette']['Ingrediens'])
            print("\n")

    return filtered_recipes

#===========    FONCTIONS POUR L'IA     ====================================================#

def obtenir_recettes(liste_ingredients, nombre_recettes):
    """
    Génère des recettes à partir d'une liste d'ingrédients en utilisant ChatOpenAI.
    
    Args:
        liste_ingredients (list): Liste des ingrédients de base.
        nombre_recettes (int): Nombre de recettes à générer.

    Returns:
        list: Liste de dictionnaires contenant les détails des recettes.
    """
    prompt = (
        f"Trouve au moins {nombre_recettes} recettes de cuisine contenant un ou plusieurs des ingrédients suivants : {', '.join(liste_ingredients)}.\n"
        "Pour chacune des recettes produis les champs suivants : \n"
        "- Titre de la recette \n"
        "- Temps de cuisson \n"
        "- Nombre de personnes \n"
        "- Durée de préparation \n"
        "- Durée de cuisson \n"
        "- Liste des ingrédients (avec un apport energétique correspondant en face de chaque ingrédient) \n"
        "- Étapes de préparation \n"
        "- Image : None  \n"
        "NE DONNE PAS DE RÉPONSES EN DEHORS DU JSON \n"
        "NE DONNE PAS DE RÉPONSES INCOMPLÈTES. N'AJOUTE AUCUN COMMENTAIRE après le ``` final"
    )
    
    # Définir les messages pour le modèle
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages = [
            {"role": "system", "content": "Tu es un chef cuisinier expert. Tu connais les plats consommés dans tous les pays à travers le monde."},
            {"role": "user", "content": prompt}
        ]
    )
    try:
        
        content = response.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()

        print("--------  reponse dans la fonction de l'IA  ---------")
        print(content)
        print("-----------------------------------------------------")

        recettes = json.loads(content)
        print("FIN de la reponse générée par l'IA \n")

    except json.JSONDecodeError as jde:
        print("Erreur de décodage JSON. Veuillez vérifier le format de la réponse.")
        print(f"Détail de l'erreur : {jde}")
        recettes = []
    except Exception as e:
        print(f"Une erreur est survenue lors de la génération des recettes : {e}")
        recettes = []
    
    print("Le type de retour de l'objet est un : ", type(recettes))
    return recettes


def obtenir_recettes_quelconques(proposition_recette_quelconque, temps_proposition_recette_quelconque):
    """
    Génère des recettes à partir d'une liste d'ingrédients en utilisant ChatOpenAI.
    
    Args:
        liste_ingredients (list): Liste des ingrédients de base.
        nombre_recettes (int): Nombre de recettes à générer.

    Returns:
        list: Liste de dictionnaires contenant les détails des recettes.
    """
    prompt = (
        f"Proposes-moi quelques recettes de {proposition_recette_quelconque} \n" 
        "que je peux faire en {temps_proposition_recette_quelconque} \n"
        "Pour chacune des recettes produis les champs suivants : \n"
        "- Titre de la recette \n"
        "- Temps de cuisson \n"
        "- Nombre de personnes \n"
        "- Durée de préparation \n"
        "- Durée de cuisson \n"
        "- Liste des ingrédients (avec un apport energétique correspondant en face de chaque ingrédient) \n"
        "- Étapes de préparation \n"
        "- Image : None  \n"
        "NE DONNE PAS DE RÉPONSES EN DEHORS DU JSON \n"
        "NE DONNE PAS DE RÉPONSES INCOMPLÈTES. N'AJOUTE AUCUN COMMENTAIRE après le ``` final"
    )
    
    # Définir les messages pour le modèle
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages = [
            {"role": "system", "content": "Tu es un chef cuisinier expert. Tu connais les plats consommés dans tous les pays à travers le monde."},
            {"role": "user", "content": prompt}
        ]
    )
    try:
        
        content = response.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()

        print("--------  reponse dans la fonction de l'IA  ---------")
        print(content)
        print("-----------------------------------------------------")

        recettes = json.loads(content)
        print("FIN de la reponse générée par l'IA \n")

    except json.JSONDecodeError as jde:
        print("Erreur de décodage JSON. Veuillez vérifier le format de la réponse.")
        print(f"Détail de l'erreur : {jde}")
        recettes = []
    except Exception as e:
        print(f"Une erreur est survenue lors de la génération des recettes : {e}")
        recettes = []
    
    print("Le type de retour de l'objet est un : ", type(recettes))
    return recettes


def generer_image_recette(titre_recette):
    """
    Génère une image pour une recette en utilisant l'API OpenAI Images.
    Retourne prioritairement une URL http(s). Si l'API renvoie du base64,
    on retourne une Data-URL 'data:image/png;base64,...'. Aucun fichier local.
    """
    try:
        resp = client.images.generate(
            model="gpt-image-1",
            prompt=f"Belle photo appétissante du plat « {titre_recette} », vue de dessus, fond clair, très nette.",
            # tailles valides: "1024x1024", "1024x1536", "1536x1024", ou "auto"
            size="1024x1024",
            n=1,
        )
        item = resp.data[0]

        # 1) Soit URL pour generer notre image de recette IA
        if getattr(item, "url", None):
            return item.url

        # 2) Soit le base64 pour générer notre image de recette IA
        b64 = getattr(item, "b64_json", None)
        if b64:
            return f"data:image/png;base64,{b64}"

        return None

    except Exception as e:
        print(f"Erreur lors de la génération de l'image pour {titre_recette}: {e}")
        return None
                    
def enregistrer_recettes(recettes, fichier_sortie):
    """
    Enregistre les recettes avec les URLs des images dans un fichier JSON.
    Args:
        recettes (list): Liste des recettes.
        fichier_sortie (str): Chemin du fichier de sortie.
    """
    
    # Écrire dans le fichier JSON
    try:
        with open(fichier_sortie, 'w', encoding='utf-8') as f:
             json.dump(recettes, f, ensure_ascii=False, indent=4)
        print(f"Les recettes avec images : None ont été enregistrées dans {fichier_sortie}")

    except Exception as e:
        print(f"Erreur lors de l'écriture dans le fichier {fichier_sortie}: {e}")

# Charger les recettes depuis le fichier JSON au démarrage de l'application.
# Ajoute une variable modifie = False au début de la boucle et écris le JSON si une image a été ajoutée.
def charger_recettes():
    try:
        with TRANSIT_IA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[charger_recettes] Fichier introuvable: {TRANSIT_IA_FILE}")
        return []
    except json.JSONDecodeError as e:
        print(f"[charger_recettes] JSON invalide: {e}")
        return []

    # Normaliser la structure: on veut une liste de dicts
    if isinstance(data, dict):
        # Cas 1: le dict contient une clé 'recettes' qui est une liste
        if "recettes" in data and isinstance(data["recettes"], list):
            data = data["recettes"]
        else:
            # Cas 2: un seul objet recette au lieu d'une liste
            data = [data]
    elif not isinstance(data, list):
        print(f"[charger_recettes] Format inattendu ({type(data).__name__}), on retourne liste vide.")
        return []

    recettes = []
    modifie = False

    for idx, element in enumerate(data):
        if not isinstance(element, dict):
            print(f"[charger_recettes] Entrée ignorée à l'index {idx}: type {type(element).__name__}")
            continue

        # Compléter l'image si absente / vide
        img = element.get("Image")
        if img in (None, "", "None", "null"):
            # Sécuriser le titre
            titre = element.get("Titre de la recette") or element.get("titre") or "Recette"
            try:
                element["Image"] = generer_image_recette(titre)  # ta fonction existante
                modifie = True
                print(f"[charger_recettes] Image générée pour: {titre}")
            except Exception as e:
                print(f"[charger_recettes] Génération image échouée pour '{titre}': {e}")

        recettes.append(element)

    # Si on a enrichi le JSON, on réécrit (facultatif)
    if modifie:
        try:
            with TRANSIT_IA_FILE.open("w", encoding="utf-8") as f:
                json.dump(recettes, f, ensure_ascii=False, indent=4)
            print("[charger_recettes] Fichier mis à jour avec les nouvelles images.")
        except Exception as e:
            print(f"[charger_recettes] Impossible d’écrire {TRANSIT_IA_FILE}: {e}")

    return recettes


#===========================================================================================#

#===========================================================================================#
#     Les différentes ROUTES de notre controleur FLASK                                      #
#===========================================================================================#

#from tout_rescrapper import *
#from tout_json_online_recuperer import *

@main.route("/healthz")  # ON met cette route lorsque l'objet ne s'appelle pas app.py
def healthz():
    return "ok", 200

@main.route("/", methods=['GET', 'POST'])                                          
def index():
    if request.method == 'POST':
        # Récupérer la liste des ingrédients envoyés par le formulaire
        liste_des_ingrediens_rentres = request.form.getlist('ingredient') 
        print("liste_des_ingrediens : ", liste_des_ingrediens_rentres)
        
        # Récupérer la date actuelle
        current_date = date_de_requette()
        
        # Sauvegarder les données dans un fichier JSON
        sauvegarder_ingrediens_dans_JSON(current_date, liste_des_ingrediens_rentres)
        
        #===================================================================================#
        #   Chercher des correspondances dans les fichiers avec les ingrediens rentrés      #
        #===================================================================================#
        
        # fichier < from_scrappy_cuisinelibre_org.json >
        #input_file = "dossier_des_JSON_internes/from_scrappy_cuisinelibre_org.json"
        filtered_recipes = chercher_correspondance_dans_fichier(CUISINE_LIBRE_FILE, liste_des_ingrediens_rentres)
       
        # fichier < ............................ >

        # fichier < ............................ >

        # fichier < ............................ >

        # Appel au modèle IA pour obtenir son résultat
        ai_msg = obtenir_recettes(liste_des_ingrediens_rentres, 3)
        print("===========================================================================")
        print(ai_msg)
        print("===========================================================================")

        if ai_msg :
            # Enregistrer les recettes dans le fichier sans images
            enregistrer_recettes(ai_msg, TRANSIT_IA_FILE)

            # Recupérer le fichier des recettes sans-images et collez-y des images genetrees par l'IA.
            recettes = charger_recettes()

            # Passer les données à la page integrer_IA.html
            return render_template("index.html",
                                    current_date=current_date,
                                    liste_des_ingrediens=liste_des_ingrediens_rentres,
                                    #
                                    # tout autre fichier .JSON qui aurait des données de recettes recupérables.
                                    #
                                    recipes_cuisinelibre=filtered_recipes,
                                    #
                                    # tout autre fichier .JSON qui aurait des données de recettes recupérables.
                                    #
                                    results_IA=recettes,
                                    carousel_images=build_carousel_items()
                                )
        else:
            print("Aucune recette n'a été générée.")

    return render_template("index.html", carousel_images=build_carousel_items())
  

@main.route("/apercu_video")                                          
def apercu_video():               
    return render_template("apercu_video.html")


@main.route("/region_cuisine_africaine_2")                                          
def region_cuisine_africaine_2():               
    return render_template("cuisine_africaine.html")

@main.route("/region_cuisine_asiatique_2")                                          
def region_cuisine_asiatique_2():               
    return render_template("cuisine_asiatique.html")


@main.route("/region_cuisine_espagnol_2")                                          
def region_cuisine_espagnole_2():               
    return render_template("cuisine_espagnole.html")


@main.route("/region_cuisine_francaise_2")                                          
def region_cuisine_francaise_2():               
    return render_template("cuisine_francaise.html")


@main.route("/region_cuisine_italienne_2")                                          
def region_cuisine_italienne_2():               
    return render_template("cuisine_italienne.html")


@main.route("/region_cuisine_quebecoise_2")                                          
def region_cuisine_quebecoise_2():               
    return render_template("cuisine_quebecoise.html")


@main.route("/api/regimes")
def api_regimes():
    try:
        with REGIMES_JSON.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": f"Fichier introuvable: {REGIMES_JSON}"}), 404
    except json.JSONDecodeError as e:
        return jsonify({"error": f"JSON invalide: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Erreur serveur: {e}"}), 500


@main.route("/api/aliments-organe")
def api_aliments_organe():
    try:
        with ALIMENTS_JSON.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": f"Fichier introuvable: {ALIMENTS_JSON}"}), 404
    except json.JSONDecodeError as e:
        return jsonify({"error": f"JSON invalide: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Erreur serveur: {e}"}), 500


# l'index IA. Seuls les administrateurs ont accès à cette route.
@main.route("/index_IA", methods=['GET', 'POST'])                                          
def index_IA():
    if request.method == 'POST':
        # Récupérer la liste des ingrédients envoyés par le formulaire
        liste_des_ingrediens = request.form.getlist('ingredient') 
        print(liste_des_ingrediens)

        # Récupérer la date actuelle
        current_date = date_de_requette()
        
        # Sauvegarder les données dans un fichier JSON
        sauvegarder_ingrediens_dans_JSON(current_date, liste_des_ingrediens)
        
        # Appel au modèle IA pour obtenir son résultat
        ai_msg = obtenir_recettes(liste_des_ingrediens, 4)

        print("===========================================================================")
        print(ai_msg)
        print("===========================================================================")

        if ai_msg :
            # Enregistrer les recettes avec sans images
            fichier_sortie = 'dossier_des_JSON_internes/transit_IA.json'
            enregistrer_recettes(ai_msg, TRANSIT_IA_FILE)

            # Recupérer le fichier des recettes et collez-y des images aec l'IA.
            recettes = charger_recettes()
            return render_template("index_IA.html",
                                    current_date = current_date,
                                    liste_des_ingrediens = liste_des_ingrediens,
                                    results_IA = recettes,
                                    carousel_images=build_carousel_items()
                                  )
        else:
            print("Aucune recette n'a été générée.")

    return render_template("index_IA.html", carousel_images=build_carousel_items())


# l'index IA. Seuls les administrateurs ont accès à cette route.
@main.route("/propose_moi_une_recette", methods=['GET', 'POST'])                                          
def propose_moi_une_recette():
    if request.method == 'POST':
        # Récupérer la proposition_recette_quelconque envoyée par le formulaire
        proposition_recette_quelconque = request.form.get('proposition_recette_quelconque') 
        temps_proposition_recette_quelconque = request.form.get('proposition_recette_quelconque')
        print(proposition_recette_quelconque, " en ", temps_proposition_recette_quelconque, " min")

        # Récupérer la date actuelle
        current_date = date_de_requette()

        # Je cree une liste des ingredients qui contiendra le SEUL INGREDIENT
        liste_des_ingrediens = []
        liste_des_ingrediens.append(proposition_recette_quelconque)

        # Sauvegarder les données dans un fichier JSON
        sauvegarder_ingrediens_dans_JSON(current_date, liste_des_ingrediens)
        
        # Appel au modèle IA pour obtenir son résultat

        ai_msg = obtenir_recettes_quelconques(proposition_recette_quelconque, temps_proposition_recette_quelconque)

        print("===========================================================================")
        print(ai_msg)
        print("===========================================================================")

        if ai_msg :
            # Enregistrer les recettes avec sans images
            enregistrer_recettes(ai_msg, TRANSIT_IA_FILE)

            # Recupérer le fichier des recettes et collez-y des images aec l'IA.
            recettes = charger_recettes()
            return render_template("proposes_moi.html",
                                    current_date = current_date,
                                    results_IA = recettes,
                                    carousel_images=build_carousel_items()
                                  )
        else:
            print("Aucune recette n'a été générée.")

    return render_template("proposes_moi.html", carousel_images=build_carousel_items())


# l'index administrateur. À partir de cette route, l'administrateur a accès à TOUT.
@main.route("/index_admin", methods=['GET', 'POST'])                                          
def index_admin():
    if request.method == 'POST':
        # Récupérer la liste des ingrédients envoyés par le formulaire
        liste_des_ingrediens_rentres = request.form.getlist('ingredient') 
        print("liste_des_ingrediens : ", liste_des_ingrediens_rentres)

        # Récupérer la date actuelle
        current_date = date_de_requette()
        
        # Sauvegarder les données dans un fichier JSON
        sauvegarder_ingrediens_dans_JSON(current_date, liste_des_ingrediens_rentres)
        
        #===================================================================================#
        #   Chercher des correspondances dans les fichiers avec les ingrediens rentrés      #
        #===================================================================================#
        
        # fichier < from_scrappy_cuisinelibre_org.json >
        input_file_1 = "dossier_des_JSON_internes/from_scrappy_cuisinelibre_org.json"
        filtered_recipes = chercher_correspondance_dans_fichier(CUISINE_LIBRE_FILE, liste_des_ingrediens_rentres)
        
        # fichier < from_scrappy_cuisinelibre_org.json >
        input_file_2 = "dossier_des_JSON_internes/from_scrappy_all_recipes_com.json"
       
        
        # fichier < ............................ >

        # fichier < ............................ >

        # Appel au modèle IA pour obtenir son résultat
        ai_msg = obtenir_recettes(liste_des_ingrediens_rentres, 4)

        print("===========================================================================")
        print(ai_msg)
        print("===========================================================================")

        if ai_msg :
            # Enregistrer les recettes avec sans images
            fichier_sortie = 'dossier_des_JSON_internes/transit_IA.json'
            enregistrer_recettes(ai_msg, TRANSIT_IA_FILE)

            # Recupérer le fichier des recettes et collez-y des images aec l'IA.
            recettes = charger_recettes()

                # Passer les données à la page integrer_IA.html
            return render_template("index_admin.html",
                                    current_date=current_date,
                                    liste_des_ingrediens=liste_des_ingrediens_rentres,
                                    #
                                    # tout autre fichier .JSON qui aurait des données de recettes recupérables.
                                    #
                                    recipes_cuisinelibre=filtered_recipes,
                                    #
                                    # tout autre fichier .JSON qui aurait des données de recettes recupérables.
                                    #
                                    results_IA=recettes,
                                    carousel_images=build_carousel_items()
                                  )
        else:
            print("Aucune recette n'a été générée.")  

    return render_template("index_admin.html", carousel_images=build_carousel_items())


@main.route("/vos_impressions")                                          
def vos_impressions():
    return render_template("vos_impressions.html")


@main.route("/similarweb_pdf")                                          
def similarweb_pdf():                                       
    # Chemin du fichier PDF
    pdf_path = 'static/files/Similarweb_Pour_observer_le_traffic_sur_un_site_web_2023-12-04.pdf'
    # Envoyer le PDF SANS téléchargement
    return send_file(pdf_path, mimetype='application/pdf')


@main.route("/formulaire_de_satisfaction")                                          
def formulaire_de_satisfaction():                                       
    # Chemin du vers le formulaire web
    url = "https://forms.office.com/pages/designpagev2.aspx?origin=OfficeDotCom&lang=fr-CA&sessionid=167640ce-fbad-4f19-8407-4b8021e4c7da&route=CreateCenter&subpage=design&id=sXh5yUy9tUSbuyAhXv32Ebw-rZdK0KJLtTpSvuZeICJUOFFSNVVGNjc4RkEwM0tETk1QUDBOMVhPOS4u&topview=Preview"
    return redirect(url)


@main.route("/tout_rescrapper")                                          
def tout_rescrapper():
    return render_template("index_admin.html")   


@main.route("/tout_json_online_recuperer", methods=['GET', 'POST'])                                          
def tout_json_online_recuperer():                            
    return render_template("index_admin.html")   


@main.route("/faire_le_suivis", methods=['GET', 'POST'])                                          
def faire_le_suivis():
    # Chemin du fichier JSON
    json_file = 'dossier_des_JSON_internes/suivis.json'
    
    # Charger les données depuis le fichier JSON
    if os.path.exists(SUIVIS_FILE):
        with open(SUIVIS_FILE, 'r') as f:
             suivis_data = json.load(f)
    else:
        suivis_data = []  # Si le fichier n'existe pas, renvoyer une liste vide
    # Transmettre les données au template
    return render_template("faire_le_suivis.html", suivis_data=suivis_data)


if __name__ == "__main__":
   # écoute sur 0.0.0.0 pour que Docker puisse exposer le port
   main.run(host="0.0.0.0", port=5000, debug=True)

