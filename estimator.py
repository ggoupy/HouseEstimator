import sys, random
import pandas as pd
import numpy as np
random.seed(1)


# Liste ordonnée des descripteurs utilisés pour le SRaPC
# L'ordre permet de définir les noeuds du graphe produit
DESCRIPTEURS = [
    "quartier",
    "pieces",
    "surface",
    "terrain"
]
# Fonction de similarité associée à chaque descripteur, permettant de comparer le plus proche
# Doit être de la même taille que DESCRIPTEURS
def strict_fn(values, val): #La valeur ou rien
    return [val if (val in values) else values[random.randrange(len(values))]]
def closest_fn(values, val): #Les valeurs les plus proches
    absolute_difference_function = lambda list_value : abs(list_value - val)
    minimum = min(values, key=absolute_difference_function)
    return [val for val in values if val == minimum]
DESCRIPTEURS_FN = [
    strict_fn,
    closest_fn,
    closest_fn,
    closest_fn
]
assert(len(DESCRIPTEURS) == len(DESCRIPTEURS_FN))
# Poids associé à chaque descripteur, permettant de réaliser l'adaptation
# Doit être de la même taille que DESCRIPTEURS
wq = -5000 # Pour les quartiers
DESCRIPTEURS_WEIGHTS = [
    {"Cenon":6*wq,"LeBoutaa":2*wq,"Talence":3*wq,"Pessac":4*wq,"Bègles":5*wq,"Bordeaux":1*wq}, # classement des quartiers
    -400, # pieces
    -50, # surface
    -20, # terrain
]
assert(len(DESCRIPTEURS) == len(DESCRIPTEURS_WEIGHTS))


# Base de données
DB = pd.read_csv('./db.csv', sep=',')



def compute_price(db):
    '''
    @summary: Calcule le prix au m2 par rapport à une base de cas.
              Nous utilisons la moyenne mais on pourrait choisir le minimum / maximum / autre.

    @param db: Dataframe contenant la base de cas
    @return: Prix au m2 par rapport aux cas donnés
    '''
    return int(db["prix"].sum() / db["surface"].sum())



def create_graph_from_db(db):
    '''
    @summary: Crée un graphe récursivement à partir d'une base de cas. (Indexation)

    @param db: Dataframe contenant la base de cas
    @return: Base de cas indexées
    '''
    # Fonction de récursion
    def create_graph_sub(db, desc):
        # (Automn) leave == cas d'arrêt
        # Calcule le prix au m2 pour le(s) cas trouvé(s) apres avoir separé la BD selon les criteres donnés (descripteurs)
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
    @summary: Applique une fonction de similarité pour trouver les k-nearest valeurs les plus proches d'une valeur donnée.

    @param values: Liste de valeurs possibles pour un descripteur
    @param desc: Valeur du descripteur
    @param similarity_fn: Fonction de similarité du descripteur
    @param k: Nombre de valeurs à retourner
    @return: Liste de valeurs les plus proches de la valeur donnée
    '''
    n = similarity_fn(values, desc)
    if k == None:
        return n
    else:
        return random.sample(values, k)



def find_similar(graph, search):
    '''
    @summary: Remémoration d'un cas source similaire au problème cible.

    @param graph: Dict sous forme de graph contenant les cas sources
    @param search: Dict contenant le problème cible
    @return: Prix minimum parmi les cas les plus proches au problème cible
    '''
    # Fonction de récursion
    def find_similar_sub(subgraph, search, desc, desc_fns):
        # Cas d'arrêt
        if len(desc) == 0:
            return (subgraph, {"prix": subgraph})
        # Parcours le graph
        else:
            closests = knearest_desc(subgraph.keys(), search[desc[0]], desc_fns[0])
            subs = [find_similar_sub(subgraph[closest], search, desc[1:], desc_fns[1:]) for closest in closests]
            prices, descs_vals = zip(*subs)
            return (np.min(prices), descs_vals[np.argmin(prices)] | { desc[0]: closests[np.argmin(prices)] })
            
    # Lancement de la récursion
    # Retourne le prix du cas le plus proche au problème cible
    closests = knearest_desc(graph.keys(), search[DESCRIPTEURS[0]], DESCRIPTEURS_FN[0])
    subs = [find_similar_sub(graph[closest], search, DESCRIPTEURS[1:], DESCRIPTEURS_FN[1:]) for closest in closests]
    prices, descs_vals = zip(*subs)
    return (np.min(prices), descs_vals[np.argmin(prices)] | { DESCRIPTEURS[0]: closests[np.argmin(prices)] })



def estimate(search, result):
    '''
    @summary: Adaptation après résolution du problème avec un cas source similaire.

    @param search: Dict contenant le problème cible
    @param result: Dict conentant le cas source choisi
    @return: Nouveau prix estimé
    '''
    dprice = 0
    for i in range(len(DESCRIPTEURS)):
        desc = DESCRIPTEURS[i]
        weight = DESCRIPTEURS_WEIGHTS[i]
        delta = 0
        # Pour des descripteurs string
        if type(weight) == dict:
            delta += weight[result[desc]] - weight[result[desc]]
        # Pour des descripteurs number
        else:
            delta += (result[desc] - search[desc]) * weight
        print(f"Delta {desc} = {delta}")
        dprice += delta
    return result["prix"] + dprice


# TODO memorisation du cas résolu




def run():
    graph = create_graph_from_db(DB)
    search = {"quartier":"Cenon","pieces":3,"surface":96,"terrain":264}
    price, result = find_similar(graph, search)
    print(f"Critères de recherche : {search}")
    print(f"Cas source trouvé : {result}")
    price = estimate(search, result)
    print(f"Prix estimé au m2 : {price}")



run()
#Cenon,3490,53,118,2
#Cenon,4000,70,0,4
#Cenon,2065,92,264,4
#Cenon,4980,82,662,4
#Cenon,3505,85,0,4
#Cenon,3750,101,357,4
#Cenon,3559,59,237,5
#Cenon,3392,102,420,5