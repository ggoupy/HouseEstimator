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



# Base de données
DB = pd.read_csv('./db.csv', sep=',')



def compute_price(db):
    '''
    @summary: Calcule le prix au m2 par rapport à une base de cas. Nous utilisons la moyenne.

    @param db: Dataframe contenant la base de cas
    '''
    return int(db["prix"].sum() / db["surface"].sum())



def create_graph_from_db(db):
    '''
    @summary: Crée un graphe récursivement à partir d'une base de cas. (Indexation)

    @param db: Dataframe contenant la base de cas
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

    @param values: liste de valeurs possibles pour un descripteur
    @param desc: valeur du descripteur
    @param similarity_fn: fonction de similarité du descripteur
    @k: nombre de valeurs à retourner
    '''
    n = similarity_fn(values, desc)
    if k == None:
        return n
    else:
        return random.sample(values, k)



def estimate(graph, search):
    '''
    @summary: Remémoration d'un cas source similaire au problème cible.

    @param graph: Dict sous forme de graph contenant les cas sources
    @param search: Dict contenant le problème cible
    @return: Prix minimum parmi les cas les plus proches au problème cible
    '''
    # Fonction de récursion
    def estimate_sub(subgraph, search, desc, desc_fns):
        # Cas d'arrêt
        if len(desc) == 0:
            return (subgraph, {"prix": subgraph})
        # Parcours le graph
        else:
            closests = knearest_desc(subgraph.keys(), search[desc[0]], desc_fns[0])
            subs = [estimate_sub(subgraph[closest], search, desc[1:], desc_fns[1:]) for closest in closests]
            prices, descs_vals = zip(*subs)
            return (np.min(prices), descs_vals[np.argmin(prices)] | { desc[0]: closests[np.argmin(prices)] })
            
    # Lancement de la récursion
    # Retourne le prix du cas le plus proche au problème cible
    closests = knearest_desc(graph.keys(), search[DESCRIPTEURS[0]], DESCRIPTEURS_FN[0])
    subs = [estimate_sub(graph[closest], search, DESCRIPTEURS[1:], DESCRIPTEURS_FN[1:]) for closest in closests]
    prices, descs_vals = zip(*subs)
    return (np.min(prices), descs_vals[np.argmin(prices)] | { DESCRIPTEURS[0]: closests[np.argmin(prices)] })


def adaptation(search, result):
    '''
    @summary: Adaptation après résolution du problème avec un cas source similaire.

    @param search: Dict contenant le problème cible
    @param result: Dict conentant le cas source choisi
    @return: TODO
    '''
    return 0

# TODO memorisation du cas résolu



graph = create_graph_from_db(DB)

search = {"quartier":"Cenon","pieces":3,"surface":96,"terrain":264}


price, result = estimate(graph, search )

adaptation(search, result)


#Cenon,3490,53,118,2
#Cenon,4000,70,0,4
#Cenon,2065,92,264,4
#Cenon,4980,82,662,4
#Cenon,3505,85,0,4
#Cenon,3750,101,357,4
#Cenon,3559,59,237,5
#Cenon,3392,102,420,5