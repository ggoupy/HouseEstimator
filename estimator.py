import sys, random, getopt
import pandas as pd
import numpy as np
random.seed(1)


# Liste ordonnée des descripteurs utilisés pour le SRaPC
# L'ordre est important car il permet de définir l'ordre des noeuds du graphe produit
DESCRIPTEURS = [
    "quartier",
    "pieces",
    "surface",
    "terrain"
]


# Fonction de similarité pour comparer des string
# Retourne la string exacte ou toutes les valeurs
def strict_fn(values, val):
    return [val] if val in values else list(values)

# Fonction de similarité pour comparer des nombres
# Retourne les valeurs où la distance absolue est minimum
def closest_fn(values, val):
    absolute_difference_function = lambda list_value : abs(list_value - val)
    minimum = min(values, key=absolute_difference_function)
    return [val for val in values if val == minimum]

# Fonction de similarité associée à chaque descripteur, permettant de trouver les valeurs les plus proches
# /!\ Doit être de la même taille que DESCRIPTEURS
DESCRIPTEURS_FN = [
    strict_fn,
    closest_fn,
    closest_fn,
    closest_fn
]
assert(len(DESCRIPTEURS) == len(DESCRIPTEURS_FN))

# Poids associé à chaque descripteur, permettant de réaliser l'adaptation
# /!\ Doit être de la même taille que DESCRIPTEURS
wq = -1000 # Pour les quartiers
DESCRIPTEURS_WEIGHTS = [
    {"Cenon":5*wq,"LeBoutaa":2*wq,"Talence":3*wq,"Pessac":4*wq,"Begles":6*wq,"Bordeaux":1*wq}, # classement des quartiers
    -100, # pieces
    -1, # surface
    -1, # terrain
]
assert(len(DESCRIPTEURS) == len(DESCRIPTEURS_WEIGHTS))



# Base de données <=> base de cas non indexée
DB = pd.read_csv('./db.csv', sep=',')



def compute_price(rows):
    '''
    @summary: Calcule le prix au m2 par rapport à une (sous) base de cas (généralement 1 seul).
              Nous utilisons la moyenne mais on pourrait choisir le minimum / maximum / autre.

    @param rows: Dataframe contenant la (sous) base de cas
    @return: Prix au m2 calculé
    '''
    return int(rows["prix"].sum() / rows["surface"].sum())



def create_graph_from_db(db):
    '''
    @summary: Crée un graphe récursivement à partir d'une base de cas. (Indexation)

    @param db: Dataframe contenant la base de cas
    @return: Base de cas indexée
    '''
    # Fonction de récursion
    def create_graph_sub(db, desc):
        # (Automn) leave => cas d'arrêt
        # Calcule le prix au m2 pour le(s) cas trouvé(s) apres avoir separé la BD selon les criteres donnés (descripteurs)
        # Devrait trouver 1 seul cas dans la plupart des cas, mais si plusieurs sont trouvés, on fait le choix de les fusionner
        if len(desc) == 0:
            return compute_price(db)
        # Ajout de nouveaux noeuds
        else:
            return {
                d : create_graph_sub(db[db[desc[0]] == d], desc[1:])
                for d in db[desc[0]]
            }

    # Lancement de la récursion
    # Retourne le graphe produit
    return {
        desc0 : create_graph_sub(db[db[DESCRIPTEURS[0]] == desc0], DESCRIPTEURS[1:])
        for desc0 in db[DESCRIPTEURS[0]]
    }



def knearest_desc(values, desc, similarity_fn, k=None):
    '''
    @summary: Applique une fonction de similarité pour trouver les valeurs les plus proches d'une valeur donnée associée à un descripteur.
              Si k est spécifié, choisit les k-nearest valeurs les plus proches.

    @param values: Liste de valeurs possibles pour un descripteur
    @param desc: Valeur du descripteur que l'on cherche
    @param similarity_fn: Fonction de similarité associée au descripteur
    @param k: Nombre de valeurs à retourner ('None' pour tout retourner)
    @return: Liste de valeurs les plus proches de la valeur donnée
    '''
    n = similarity_fn(values, desc)
    if k == None: #Toutes les valeurs
        return n
    else: #K-nearest valeurs
        return random.sample(values, k)



def find_similar(graph, search):
    '''
    @summary: Remémoration d'un cas source similaire au problème cible.

    @param graph: Dict sous forme de graph contenant les cas sources
    @param search: Dict contenant le problème cible
    @return: Retourne le cas le plus proche au problème cible
    ''' # Note : on choisit le prix minimum mais on pourrait prendre le prix max / mean    
    # Fonction de récursion
    # Retourne le tuple <prix, cas_source> afin de faciliter les calculs dans la récursion
    def find_similar_sub(subgraph, search, desc, desc_fns):
        # Cas d'arrêt
        # subgraph contient le prix du cas source
        if len(desc) == 0:
            return (subgraph, {"prix": subgraph})
        # Parcours le graph
        else:
            # Récupère les valeurs du descripteur traité les plus proches à la valeur du problème cible
            closests = knearest_desc(subgraph.keys(), search[desc[0]], desc_fns[0])
            # Récursion sur chaque sous graphe à partir des valeurs trouvées
            subs = [find_similar_sub(subgraph[closest], search, desc[1:], desc_fns[1:]) for closest in closests]
            # Trouve le cas le plus proche dans les sous graphes
            prices, descs_vals = zip(*subs)
            return (np.min(prices), descs_vals[np.argmin(prices)] | { desc[0]: closests[np.argmin(prices)] })
            
    # Lancement de la récursion
    # Récupère les valeurs du 1er descripteur les plus proches à la valeur du problème cible
    closests = knearest_desc(graph.keys(), search[DESCRIPTEURS[0]], DESCRIPTEURS_FN[0])
    # Récursion sur chaque sous graphe à partir des valeurs trouvées
    subs = [find_similar_sub(graph[closest], search, DESCRIPTEURS[1:], DESCRIPTEURS_FN[1:]) for closest in closests]
    # Trouve le cas le plus proche dans le sous graphe
    prices, descs_vals = zip(*subs)
    return descs_vals[np.argmin(prices)] | { DESCRIPTEURS[0]: closests[np.argmin(prices)] }



def estimate(search, result, debug=True):
    '''
    @summary: Adaptation de la solution du cas source pour le problème cible.

    @param search: Dict contenant le problème cible
    @param result: Dict conentant le cas source choisi
    @return: Nouveau prix estimé
    '''
    if debug:
        print("Adaptation :")
    dprice = 0
    for i in range(len(DESCRIPTEURS)):
        desc = DESCRIPTEURS[i]
        weight = DESCRIPTEURS_WEIGHTS[i]
        delta = 0
        # Pour des descripteurs string
        if type(weight) == dict:
            #SSI la valeur est connue dans les poids associés
            if search[desc] in weight:
                delta += weight[result[desc]] - weight[search[desc]]
        # Pour des descripteurs number
        else:
            delta += (result[desc] - search[desc]) * weight
        if debug:
            print(f"\tDelta {desc} = {delta}")
        dprice += delta
    return int(result["prix"] + dprice)
    # TODO memorisation du cas résolu



def run(graph, search, debug=False):
    '''
    @summary: Résout le problème donné à partir de la base de cas indexée.

    @param graph: Dict contenant la base de cas indexée
    @param search: Dict contenant le problème cible à résoudre
    '''
    # Remémoration d'un cas source similaire au problème cible
    result = find_similar(graph, search)
    if debug:
        print(f"Comparaison cas source | Problème cible:")
        for desc in DESCRIPTEURS:
            print(f"\t{desc} : {result[desc]} | {search[desc]}")
        print()
    # Adaptation de la solution du cas source pour le problème cible
    price = estimate(search, result, debug)
    if debug:
        print(f"\n=>Prix estimé au m2 : {price}")
    else:
        print(price)



# Méthode qui test le modèle X fois sur des données dont on connait le prix réel
# Choisit aléatoirement une ligne, l'enlève de la DB, estime sa valeur
# avec le modèle et calcule le pourcentage de différence avec la réalité
def test_model(nb_epochs=10, debug=True):
    moy_err = 0
    for i in range(nb_epochs):
        # Prend une ligne au hasard
        row = DB.sample()
        # Code très moche qui convertit l'ouput de pandas en search dict (= le cas à traiter)
        search = {key: list(val.values())[0] for key,val in row.to_dict().items()}
        search["prix"] = int(search["prix"] / search["surface"]) # Preprocess le prix pour le calcul
        # Base de cas sans la ligne tirée
        db = DB.drop(index=row.index)
        # Base de cas indexée
        graph = create_graph_from_db(db)
        # Rememoration - Trouve le cas source
        result = find_similar(graph, search)
        # Adaptation - Estime le prix en fonction du cas source
        price = estimate(search, result, debug=debug)
        # Calcule le pourcentage de différence avec la réalité
        #diff = round( (abs(search['prix'] - price) / ((search['prix'] + price)/2) * 100) , 2)
        diff = round( ( (price - search['prix']) / search['prix'] ) * 100, 2)
        # Affichage
        if debug:
            print(f"Problème cible : {search}")
            print(f"Problème source trouvé : {result}")
            print(f"Prix estimé : {price}")
            print(f"Prix réel : {search['prix']}")
            print(f"=> Taux de variation : {diff}%")
            print()
        moy_err += abs(diff)
    moy_err = round(moy_err/nb_epochs,2)
    if debug:
        print(f"Erreur moyenne dans la prédiciton : {moy_err}%\n")
    return moy_err



# Méthode bourrin pour tester les combinaisons de poids et trouver celles les plus efficaces (sur notre dataset)
def grid_search():
    # Valeurs à tester pour chaque poids
    params = [
        [i for i in range(-5000,-999,1000)], #quartier
        [i for i in range(-500,-99,100)], #pieces
        [i for i in range(-5,0,1)], #surface
        [i for i in range(-5,0,1)], #terrain
    ]

    # Mega boucle bien complexe
    res = {}
    for i in range(len(params[0])):
        wq = params[0][i]
        for j in range(len(params[1])):
            DESCRIPTEURS_WEIGHTS[1] = params[1][j]
            for k in range(len(params[2])):
                DESCRIPTEURS_WEIGHTS[2] = params[2][k]
                for l in range(len(params[3])):
                    DESCRIPTEURS_WEIGHTS[3] = params[3][l]
                    # Test le modèle et stocke l'erreur moyenne pour une combinaison de paramètres 
                    moy_err = test_model(30,False)
                    key = "("+str(wq)+","+str(DESCRIPTEURS_WEIGHTS[1])+","+str(DESCRIPTEURS_WEIGHTS[2])+","+str(DESCRIPTEURS_WEIGHTS[3])+")"
                    res = res | { key: moy_err }

    # Affichage des résultats
    for k in sorted(res, key=res.get):
        print(k, " -> ", res[k])
    #(-1000,-100,-1,-1)  ->  21.01
    #(-5000,-200,-1,-2)  ->  21.54
    #(-3000,-300,-1,-1)  ->  22.53
    #(-1000,-400,-2,-2)  ->  22.56
    #(-3000,-100,-4,-1)  ->  22.83
    #(-5000,-500,-4,-2)  ->  23.1
    #(-4000,-300,-5,-3)  ->  23.1
    #(-5000,-100,-3,-1)  ->  23.11
    #(-1000,-100,-3,-2)  ->  23.42




# ----------------------------------------------------------------------------- #
# ---------------------------     Main       ---------------------------------- #
# ----------------------------------------------------------------------------- #

def usage():
    print(f"Usage : <executable> \n\t\t--quartier=<str> \n\t\t--pieces=<int> \n\t\t--surface=<int> \n\t\t--terrain=<int> \n\t\t[ optional --debug ]")
    print(f"Pour tester le modèle : <executable> --test_model=<nb_epochs>")


def main(argv):
    
    # Paramètres du programme
    debug = False
    search = {
        "quartier": None,
        "pieces": None,
        "surface": None,
        "terrain": None
    }
    test_model_epochs = -1

    # Récupération des paramètres passés en ligne de commande
    try:                                
        opts, _ = getopt.getopt(argv, "", ["quartier=", "pieces=", "surface=", "terrain=", "debug", "test_model="])
        #Pas très romantique mais bon on fait avec...
        for (opt,val) in opts:
            if opt == "--quartier":
                search["quartier"] = val
            if opt == "--pieces" and int(val) > 0:
                search["pieces"] = int(val)
            if opt == "--surface" and int(val):
                search["surface"] = int(val)
            if opt == "--terrain" and int(val) > 0:
                search["terrain"] = int(val)
            if opt == "--debug":
                debug = True
            if opt == "--test_model":
                if int(val) > 0:
                    test_model_epochs = int(val)
                else:
                    raise ValueError()
        if test_model_epochs == -1:
            for key in search.keys():
                if search[key] == None:
                    raise ValueError()
    except getopt.GetoptError:
        print("Error : Impossible de lancer le programme...")
        usage()
        sys.exit(2)
    except ValueError:
        print("Error : Impossible de lancer le programme...")
        usage()
        sys.exit(2)

    
    graph = create_graph_from_db(DB)

    # Estimation du problème donné 
    if test_model_epochs == -1:
        run(graph, search, debug)
    else:
        test_model(test_model_epochs,True)



if __name__ == '__main__':
    #grid_search()
    main(sys.argv[1:])
