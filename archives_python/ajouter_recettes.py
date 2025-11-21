import json

# Charger les recettes existantes
fichier_json = "dossier_des_JSON_internes/recettes_avec_images.json"

def charger_recettes(fichier):
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def enregistrer_recettes(fichier, recettes):
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(recettes, f, indent=4, ensure_ascii=False)

def ajouter_recette(nouvelle_recette):
    recettes = charger_recettes(fichier_json)
    recettes.append(nouvelle_recette)
    enregistrer_recettes(fichier_json, recettes)
    print("Recette ajoutée avec succès !")

# Exemple de nouvelle recette
nouvelle_recette = {
    "titre": "titre 4",
    "url": "url 4",
    "url_image": "url image 4",
    "recette": {
        "Titre de la recette": "Tarte aux fraises",
        "Temps de cuisson": "30 minutes",
        "Nombre de personnes": 6,
        "Durée de préparation": "20 minutes",
        "Durée de cuisson": "30 minutes",
        "Liste des ingrédients": [
            "250g de farine",
            "125g de beurre",
            "50g de sucre",
            "1 œuf",
            "500g de fraises",
            "Crème pâtissière"
        ],
        "Les étapes de préparation": [
            "Préparer la pâte brisée en mélangeant la farine, le beurre, le sucre et l'œuf.",
            "Laisser reposer 30 minutes au frais.",
            "Étaler la pâte et la cuire à blanc pendant 15 minutes à 180°C.",
            "Garnir de crème pâtissière et disposer les fraises.",
            "Servir frais."
        ]
    }
}

# Ajouter la nouvelle recette
ajouter_recette(nouvelle_recette)
