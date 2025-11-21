
#from scrapper_all_recipes import *     # les fichiers scrappables sur ces sites sont inexistants
from Trouvez_Des_Recettes.archives_python.scrapper_cuisine_libre import *
#from scrapper_epicurious import *
#from scrapper_marmitton import *
#from scrapper_open_recipes import *    # les fichiers scrappables sur ces sites sont inexistants
#from scrapper_tasty_co import *        # Il faut juste SCRAPPER TASTYCO pour avoir ce site en ANGLAIS.

def tout_rescrapper() :
    
    print("===============================================================")
    print("|      Scrapper les sites pour produire des JSON              |")
    print("===============================================================")

    #scrapper_all_recipes()

    scrapper_cuisine_libre()

    #scrapper_epicurious()

    #scrapper_marmitton()

    #scrapper_open_recipes()
    
    #scrapper_tasty_co()






















