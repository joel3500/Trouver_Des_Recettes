noms = ['Alice', 'Bonnet', 'Coline', 'David']
phrases = ['alice mange bien', 'rené a un bonnet', 'la coline est haute', 'david contre Goliath', 'suzanne et geremie']

# Vérifier si chaque élément de la liste noms est présent dans au moins une phrase
boolean = all(any(nom.lower() in phrase.lower() for phrase in phrases) for nom in noms)

# Affichage du résultat
print(f"Tous les noms sont présents : {boolean}")