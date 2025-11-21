#=== Flask ============================================================================#

from flask import Flask, redirect, render_template, request, jsonify, send_from_directory, send_file
from datetime import datetime 
import json            
import os
import io
import sys
from flask_cors import CORS
import base64

from sqlalchemy import null

#=== FIN DES LIBRAIRIES    =================================================================#

# Initialisation de notre Controleur (Initialisation de Flask)
mainImage_assistant = Flask(__name__)
CORS(mainImage_assistant)

#===========================================================================================#

import openai
from dotenv import load_dotenv

#===========================================================================================#

# Configuration des clés API
load_dotenv()
key =  os.getenv("OPENAI_API_KEY_1")
openai.api_key = key

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
        f"Trouve {nombre_recettes} recettes de cuisine faites uniquement à partir des ingrédients suivants : {', '.join(liste_ingredients)}.\n"
        "Pour chacune des recettes produis les champs suivants : \n"
        "- Titre de la recette \n"
        "- Temps de cuisson \n"
        "- Nombre de personnes \n"
        "- Durée de préparation \n"
        "- Durée de cuisson \n"
        "- Liste des ingrédients \n"
        "- Les étapes de préparation \n"
        "- Image : None  \n"
        "NE DONNE PAS DE RÉPONSES EN DEHORS DU JSON \n"
        "NE DONNE PAS DE RÉPONSES INCOMPLÈTES. N'AJOUTE AUCUN COMMENTAIRE après le ``` final"
    )
    
    # Définir les messages pour le modèle
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages = [
            {"role": "system", "content": "Tu es un chef cuisinier expert."},
            {"role": "user", "content": prompt}
        ]
    )
    try:
        content = response['choices'][0]['message']['content']
        content = content.replace("```json", "").replace("```", "").strip()

        print("----------------------------------------------------")
        print(content)
        print("----------------------------------------------------")

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
    Génère une image pour une recette en utilisant l'API DALL·E d'OpenAI.
    
    Args:
        titre_recette (str): Titre de la recette.

    Returns:
        str: URL de l'image générée.
    """
    
    try:
        response = openai.Image.create(
            prompt=f"Une belle présentation de {titre_recette}.",
            n=1,
            size="256x256"
        )
        image_url = response['data'][0]['url']
        print("L'url d'une des images est : ", image_url)
        return image_url
    
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

# Charger les recettes depuis le fichier JSON au démarrage de l'application
def charger_recettes():
    fichier_json = 'dossier_des_JSON_internes/recettes_doc_1.json'
    try:
        with open(fichier_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        #recettes = recettes["recettes"]   
        
        for index, element in enumerate(data):
            print(f"Index {index}:")
            for cle, valeur in element.items():
                if isinstance(valeur, list):
                    print(f"  {cle}:")
                    for item in valeur:
                        print(f"    - {item}")
                else:
                    # Vérifie si la clé est "Image" et que sa valeur est null (None en Python)
                    if cle == "Image" and (valeur == "None"):
                        element[cle] = generer_image_recette(element["Titre de la recette"])  # Mise à jour de la valeur
                        print(f"  {cle}: {element[cle]}")  # Affiche la valeur mise à jour
                    else:
                        print(f"  {cle}: {valeur}")

            print("\n")  # Ligne vide pour séparer les entrées

        return data
    
    except FileNotFoundError:
        print(f"Le fichier {fichier_json} n'a pas été trouvé.")
        return []
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON : {e}")
        return []

#===========================================================================================#

@mainImage_assistant.route('/')
def index_Image():
    recettes = charger_recettes()
    return render_template('index_Image.html', recettes=recettes)


@mainImage_assistant.route("/index_IA_Image", methods=['GET', 'POST'])                                          
def index_IA_Image():

    # Définir les ingrédients
    liste_ingredients = ["poivron", "concombre", "poisson", "tomate", "Attiéké", "Oignon"]
    
    # Obtenir les recettes
    recettes = obtenir_recettes(liste_ingredients, 4)
    print("===========================================================================")
    print(recettes)
    print("===========================================================================")

    if recettes :
        # Enregistrer les recettes avec sans images
        fichier_sortie = 'dossier_des_JSON_internes/recettes_doc_1.json'
        enregistrer_recettes(recettes, fichier_sortie)

        # Recupérer le fichier des recettes et collez-y des images aec l'IA.
        recettes = charger_recettes()
        return render_template("index_IA_Image.html", recettes=recettes)
    else:
        print("Aucune recette n'a été générée.")
    return render_template("index_IA_Image.html")


if __name__ == "__main__":
    mainImage_assistant.run(debug=True)