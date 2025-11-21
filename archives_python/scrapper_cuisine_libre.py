def scrapper_cuisine_libre():
    import requests
    from bs4 import BeautifulSoup
    import json
    import re
    import os
    import time

    # https://stackabuse.com/guide-to-parsing-html-with-beautifulsoup-in-python/

    # Vider le fichier "from_scrappy_allrecipes_com.json" : Il est absomument necessaire de le vider avant de
                                                          # le remplir à nouveau de sorte à NE PAS avoir l'information en double.
    open('dossier_des_JSON_internes/from_scrappy_cuisinelibre_org.json', 'w').close()

    # Le site web d'où j'ai scrappé toutes ces données
    BASE_URL = "https://www.cuisine-libre.org/"

    print("\nLe Scrapping du site ( https://www.cuisine-libre.org/ ) a été démarré. \n")

    # Le fichier JSON interne de référence
    fichier_json = "dossier_des_JSON_internes/from_scrappy_cuisinelibre_org.json"

    def telecharger_et_sauvegarder_image(url):
        response = requests.get(url)
        filenmame = url.split("/")[-1]
        index_point_interrogation = filenmame.find("?")
        if index_point_interrogation != -1:
            filenmame = filenmame[:index_point_interrogation]
        if response.status_code == 200:
            with open(filenmame, 'wb') as f:
                f.write(response.content)

    def nettoyer_texte(t):
        #print("Nettoyage du texte en cours...\n")
        #print("\tRetrait des chaines bizarres xa0...\n")
        t1 = t.replace("\xa0", "")
        #print("\tRetrait des anticlash de retour à la ligne...\n")
        t2 = t1.replace("\n", "")
        #print("\tRetrait des balises de type <p>...\n")
        t3 = t2.replace("<p>", "")
        #print("\tRetrait des balises de type </p>...\n")
        t4 = t3.replace("</p>", "")
        #print("\tRetrait des balises de type <br/>...\n")
        t5 = t4.replace("<br/>", "")
        #print("\tRetrait des balises de type <div>...\n")
        t6 = t5.replace("<div>", "")
        #print("\tRetrait des balises de type </div>...\n")
        t7 = t6.replace("</div>", "")
        #print("\tRetrait des espaces inutiles...\n")
        t8 = t7.strip()
        return t8

    # Récupérer la licence, l'indicateur du droit de scrapper     FONCTIONNE TRES BIEN
    def recuperer_licence(soup):
        print("\nRécupérer la licence, l'indicateur du droit de scrapper...\n")
        
        license_text = soup.find("footer", id="license").text
        license_valide = "cc0" in license_text.lower() or "domaine public" in license_text.lower()

        return license_valide

    # Récupérer le titre de la recette                            FONCTIONNE TRES BIEN
    def recuperer_titre(soup):
        print("Titre de la recette : ")
        titre = soup.find('h1').text # ou ou text.strip() ou get_text()  ou encore .text.strip().encode("ascii", "ignore").decode("ascii")
        print(titre)
        return titre

    # Récupérer le nombre de personnes                            FONCTIONNE TRES BIEN
    def nombre_personnes(soup):
    #    print("Nombre de personnes : ")
        personnes = soup.find("span", itemprop="recipeYield")
        les_personnes = personnes.text if personnes else "Non_specifie"
    #    print("Nettoyer texte --> Nombre de personnes : ")
        les_personnes = nettoyer_texte(les_personnes)
        print(les_personnes)
        return les_personnes

    # Récupérer la durée de préparation                           FONCTIONNE TRES BIEN
    def duree_preparation(soup):
        print()
        # Récupérer la durée de preparation                       FONCTIONNE TRES BIEN
    #    print("Duree de préparation : ")
        duree_preparation = soup.find("span", class_="cond duree_preparation prepTime")
        time_prepa = duree_preparation.find("time").text if duree_preparation else "Non_specifie"
    #    print("Nettoyer texte --> Durée de préparation : ")
        time_prepa = nettoyer_texte(time_prepa).replace("?", "")  # Il arrive souvent qu'on y voit des ?
        print(time_prepa)
        return time_prepa

    # Récupérer la durée de cuisson                               FONCTIONNE TRES BIEN
    def duree_cuisson(soup):
        print()
        # Récupérer la durée de cuisson                           FONCTIONNE TRES BIEN
    #    print("Durée de cuisson : ")
        duree_cuisson = soup.find("span", class_="cond duree_cuisson cookTime")
        time_cuis = duree_cuisson.find("time").text if duree_cuisson else "Non_specifie"
        time_cuis = nettoyer_texte(time_cuis)
        print(time_cuis)
        return time_cuis

    # Récupérer la liste des ingrédients                          FONCTIONNE TRES BIEN
    def liste_ingrediens(soup):
        # Récupérer la liste des Ingrediens                       FONCTIONNE TRES BIEN
    #    print("\n====================================")
    #    print("|  La liste des ingrédiens :       |")
    #    print("====================================")
        ul_les_Ingrediens = soup.find("ul", class_="spip") # [etape.get_text() for etape in soup.find_all("div", text="instruction")]
        list_ingrediens = ul_les_Ingrediens.find_all("li")
        
    #    print("Nettoyer texte --> Liste des Ingrédiens : ")
        ingrediens = [nettoyer_texte(ingredien.text) for ingredien in list_ingrediens]
        
        #for ingredien in list_ingrediens :  # question de voir sur le terminal
        #    print("- ", ingredien)
        return ingrediens

    # Récupérer les étapes de préparation                         FONCTIONNE TRES BIEN
    def etapes_preparation(soup):
    #    print("\n=======================")
    #    print("|  les Étapes :       |")
    #    print("=======================")
        div_preparation = soup.find("div", class_=re.compile(r"^crayon article-texte")) # ou encore [etape.get_text() for etape in soup.find_all("div", text="instruction")]
        list_etapes = div_preparation.find_all("p") # ca se peut que le formatage soit en li et non en p
        etapes = [etape.get_text(strip=True) for etape in list_etapes]
        
        # il arrive que ce ne soit pas dans des balises <p> mais dans des balises <li>
        if len(list_etapes) == 0 :
            list_etapes = div_preparation.find_all("li")
            etapes = [etape.get_text(strip=True) for etape in list_etapes]

        #for etape in etapes :                 # ou etape in list_etapes : # question de voir sur le terminal
        #    print("- ", etape)
        return etapes

    # Récupérer une recette à la fois                             FONCTIONNE TRES BIEN
    def extraire_recette(url):
        # Envoyer une requête pour récupérer le contenu de la page
        response = requests.get(url)
        response.encoding = "utf-8"
        response.raise_for_status()  # Vérifier si la requête a réussi

        # Parser le contenu HTML de la page
        soup = BeautifulSoup(response.content, "html.parser") # soup = BeautifulSoup(response.text, "html.parser")
        
        # Fonctions pour extraire les données de la recette
        recette = {}

        license_valide = recuperer_licence(soup)              # Cruciale pour l'extraction. 
                                                            # Si ce n'est pas valide, le dictionnaire retourné sera vide
        if  not license_valide :
            print("La license n'est pas CC0 ou Domaine public ==> Ne SCRAPPEZ PAS cette page !! \n")
        else :
            print("La page PEUT être SCRAPPÉE")
        
        print("J'ai quand-même TOUT SCRAPPÉ, car je n'avais pas assez de page libre de SCRAPPE... \n" + 
            "Faudrait peut-être que j'écrive à Cuisine-Libre.org pour qu'ils m'en donnent la permission ??")

        titre = recuperer_titre(soup)
        personnes  = nombre_personnes(soup)
        time_prepa = duree_preparation(soup)
        time_cuis  = duree_cuisson(soup)
        ingrediens = liste_ingrediens(soup)
        etapes  = etapes_preparation(soup)
        #infos   = {"duree_preparation"    : time_prepa , "duree_cuisson" : time_cuis}
        recette = {"Titre"                 : titre,
                    "Nombre_de_personnes"  : personnes,
                    #"Infos"               : infos,      #infos = {"duree_preparation" : time_prepa , "duree_cuisson" : time_cuis}
                    "Duree_preparation"    : time_prepa , 
                    "Duree_cuisson"        : time_cuis,
                    "Ingrediens"           : ingrediens,
                    "Etapes"               : etapes
        }

        return recette

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

    def ajouter_une_recette_init():
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
        #ajouter_recette(nouvelle_recette)

    liste_resultats = charger_recettes(fichier_json)

    def extraire_liste_recettes(liste_url):
        # { "titre": "", "url": "", "url_image": "", "recette": ""}
        response = requests.get(liste_url)
        soup = BeautifulSoup(response.text, "html.parser")

        div_recettes = soup.find("div", id="recettes")
        ul_recettes = div_recettes.find("ul", recursive=False)
        li_recettes = ul_recettes.find_all("li")
        
        for li in li_recettes:
            a = li.find("a")
            strong = a.find("strong")
            titre = nettoyer_texte(strong.text)
            url = BASE_URL + a["href"]
            img = a.find("img")
            url_image = BASE_URL + img["src"]
                  
            try :
                recette = extraire_recette(url)
                if recette:
                    liste_resultats.append({"titre": titre, "url": url, "url_image": url_image, "recette": recette })      
                    print("Recette ajoutée à la liste avec succès !")
                    time.sleep(0.1) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.
            except Exception as e :
                print(f"Erreur lors de l'extraction de la recette depuis {url} : {e}")
            
            enregistrer_recettes(fichier_json, liste_resultats)

            # time.sleep(0.1) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.

    def enregistrement_de_la_liste(fichier_json, liste_recettes):
        data_existante = []
        # Charger le contenu du fichier dans la variable < data_existante >
        with open(fichier_json, 'r', encoding="utf-8") as f:
            # move the file pointer from 0th position to end position
            f.seek(0, os.SEEK_END)

            # return the current position of file pointer
            file_size = f.tell()

            # if file size is 0, it is empty
            if file_size == 0:
                print("File is empty")
            else:
                print("File is NOT empty")
                data_existante = json.load(f)

        # Écrire la liste mise à jour dans le fichier
        if  liste_recettes :
            # Ajouter les nouvelles recettes
            for recette in liste_recettes :
                data_existante.append({ recette })

            with open(fichier_json, 'w', encoding="utf-8") as f:
                json.dump(data_existante, f, ensure_ascii=False, indent=4)      # Sérialiser et écrire dans le fichier 'dossier_des_JSON_internes/from_scrappy_cuisinelibre_org.json'
                                                                                # La fonction json.dumps() sérialise un objet Python et renvoie une chaîne de caractères JSON, au lieu de l'écrire dans un fichier.     
                print(f"La recette a été bien enregistrée dans { fichier_json }")
        else :  
                print("Aucune recette trouvée.")
        return
        
    print("#===================================================================#")
    print("#    EXTRACTION DES RECETTES des différentes rubriquesn en ligne    #")
    print("#===================================================================#\n")

    #============ Extraction de quelques RECETTES DE BASE
    print("prochaine Extraction : quelques RECETTES DE BASE...")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.
    extraire_liste_recettes("https://www.cuisine-libre.org/cremerie?max=400")
    time.sleep(1) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.


    #============ Extraction de quelques BOULANGERIES-PATISSERIES
    print("prochaine Extraction : quelques BOULANGERIES-PATISSERIES...")
    time.sleep(3)
    extraire_liste_recettes("https://www.cuisine-libre.org/boulangerie-et-patisserie?mots%5B%5D=83&lang=&max=600")
    time.sleep(1) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.


    #============ Extraction de quelques CRÊMERIES
    print("prochaine Extraction : quelques GARNITURES...")
    time.sleep(3)
    extraire_liste_recettes("https://www.cuisine-libre.org/cremerie?max=200")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.


    #============ Extraction de quelques TARTINES ET SANDWICHES
    print("prochaine Extraction : quelques TARTINES ET SANDWICHES...")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.
    extraire_liste_recettes("https://www.cuisine-libre.org/tartines-et-sandwichs?max=120")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.


    #============ Extraction de quelques ENTRÉES
    print("prochaine Extraction : quelques ENTRÉES...")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.
    extraire_liste_recettes("https://www.cuisine-libre.org/entrees?max=200")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.


    #============ Extraction de quelques SALADES
    print("prochaine Extraction : quelques SALADES...")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.
    extraire_liste_recettes("https://www.cuisine-libre.org/salades?max=200")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.


    #============ Extraction de quelques SOUPES ET POTEES ET RAGOUTS
    print("prochaine Extraction : quelques SOUPES ET POTEES ET RAGOUTS...")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.
    extraire_liste_recettes("https://www.cuisine-libre.org/soupes-et-potees?max=300")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.


    #============ Extraction de quelques PATES, PILAFS ET RISOTTOS
    print("prochaine Extraction : quelques PATES, PILAFS ET RISOTTOS...")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.
    extraire_liste_recettes("https://www.cuisine-libre.org/pilafs-et-risottos?max=100")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.


    #============ Extraction de quelques ROTIS DET GRATINS
    print("prochaine Extraction : quelques ROTIS DET GRATINS...")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.
    extraire_liste_recettes("https://www.cuisine-libre.org/enfournez?max=300")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.


    #============ Extraction de quelques POELÉES ET GRILLADES
    print("prochaine Extraction : quelques POELÉES ET GRILLADES...")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.
    extraire_liste_recettes("https://www.cuisine-libre.org/poele-et-grill?max=200")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.


    #============ Extraction de quelques GARNITURES
    print("prochaine Extraction : quelques GARNITURES...")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.
    extraire_liste_recettes("https://www.cuisine-libre.org/garnitures?max=200")
    time.sleep(3) # pour ne pas surcharger le serveur. On ne veut pas attirer l'attention.

    # données  ==> sérialise en JSON    ==> Texte
    # texte    ==> désérialise le JSON  ==> données

    #json_string_liste_recettes_1 = json.dumps(liste_recettes_1, indent=4)
    #print(json_string_liste_recettes_1)  # Dans cet exemple, json.dumps() convertit l'objet data en une chaîne JSON et la retourne, que l'on peut ensuite afficher ou utiliser comme une variable.
    #json_string_liste_recettes_2 = json.dumps(liste_recettes_2, indent=4)
    #print(json_string_liste_recettes_2)  # Dans cet exemple, json.dumps() convertit l'objet data en une chaîne JSON et la retourne, que l'on peut ensuite afficher ou utiliser comme une variable.
    #json_string_liste_recettes_3 = json.dumps(liste_recettes_3, indent=4)
    #print(json_string_liste_recettes_3)  # Dans cet exemple, json.dumps() convertit l'objet data en une chaîne JSON et la retourne, que l'on peut ensuite afficher ou utiliser comme une variable.

    #===================================================================#
    #    EXTRACTION DES RECETTES des différentes rubriquesn en ligne    #
    #===================================================================#

    #enregistrement_de_la_liste(liste_recettes_1)
    #enregistrement_de_la_liste(liste_recettes_2)
    #enregistrement_de_la_liste(liste_recettes_3)
    #enregistrement_de_la_liste(liste_recettes_4)
    #enregistrement_de_la_liste(liste_recettes_5)
    #enregistrement_de_la_liste(liste_recettes_6)
    #enregistrement_de_la_liste(liste_recettes_7)
    #enregistrement_de_la_liste(liste_recettes_8)
    #enregistrement_de_la_liste(liste_recettes_9)
    #enregistrement_de_la_liste(liste_recettes_10)

    #===============================================================================#
    #         2e méthode pour Sérialiser qui ne sera pas utilisée ici               #
    #===============================================================================#

    #liste_recettes_json_1 = json.dump(liste_recettes_1)
    #liste_recettes_json_2 = json.dumps(liste_recettes_2)
    #liste_recettes_json_3 = json.dumps(liste_recettes_3)
    #f = open("dossier_des_JSON_internes/from_scrappy_cuisinelibre_org.json", "w")
    #f.write(liste_recettes_json_1)
    #f.write(liste_recettes_json_2)
    #f.write(liste_recettes_json_3)
    #f.close()

    #============  FIN de la 2e méthode de Sérialisation  ==========================#

    def replace_outer_quotes_recipe(s):
        def replace(match):
            inner = match.group(1)
            inner = inner.replace("\\'", "{{SINGLE_QUOTE}}")
            inner = inner.replace("'", "\\'")
            inner = inner.replace("{{SINGLE_QUOTE}}", "\\'")
            return f'"{inner}"'

        pattern = r"'((?:[^'\\]|\\.)*?)'(?=\s*,\s*'|$)"
        return re.sub(pattern, replace, s)


## scrapper_cuisine_libre()