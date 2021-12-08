# HOUSE ESTIMATOR


## Contexte

*House Estimator* est un projet réalisé dans le cadre de l'UE "Dynamique des connaissances" du Master 2 IA de [l'université Claude Bernard Lyon 1](https://www.univ-lyon1.fr/). Il a été encadré par [Béatrice Fuchs](https://perso.liris.cnrs.fr/beatrice.fuchs/) et aborde la thématique du raisonnement à partir de cas. 


## Objectif 

L'objectif du projet était de concevoir un système simple de raisonnement à partir de cas. Le but de ce système est de résoudre de nouveaux problèmes, en réutilisant des solutions de problèmes antérieurs résolus. Ici, nous allons nous intéresser au cas de l'estimation des biens immobilers, et en particulier des maisons dans la région Bordelaise.


## Implémentation

### Base de cas
La base de cas a été constituée manuellement, à partir du site [seloger.com](https://www.seloger.com/). Elle est composée de de **50 exemples**, contenant les caractéristiques suivantes :
- **Quartier** : position géographique du bien (regroupe quartiers et communes limitrophes)
- **Pièces** : nombre de pièces
- **Surface** : surface habitable en m<sup>2</sup>
- **Terrain** : terrain en m<sup>2</sup>
- **Prix** : total, en euros

### Programme
Cette section détaille le cycle suivit par le système.  

#### Indexation de la base de cas
La base de cas est stockée dans le fichier `db.csv`. À l'exécution, le système lit la base de donnée à l'aide du module `pandas` et construit une base de cas indexée (*graph*), sous la forme d'un dictionnaire python. La création du graphe est réalisée par la fonction `create_graph_from_db(db)`, construisant les noeuds récursivement à l'aide des descripteurs (caractéristiques) définis dans la constante `DESCRIPTEURS`. Leur ordre est important car il correspond à l'ordre des noeuds dans la base indexée. Dans le cas (très rare) où plusieurs cas seraient similaires, ils sont fusionnés (fonction `compute_price(rows)`) et le prix stocké est calculé par moyenne de ces cas. À noter que ce n'est pas la seule manière de calculer ce prix (*max, min, etc.*). Par ailleurs, les prix sont sont convertis en prix / m<sup>2</sup> dans la base indexée, afin d'améliorer la précision dans l'adaptation.
#### Remémoration 
La remémoration d'un cas source à partir du problème cible donné est réalisée par la fonction `find_similar(graph,search)`, l'argument `graph` étant la base de cas indexée et l'argument `search` un dictionnaire python contenant le problème cible. Cette fonction cherche dans le graphe le cas source le plus similaire à un problème cible, selon des critères de similarité définis. Pour cela, à chaque niveau (représentant un descripteur), les valeurs du descripteur les plus similaires/proches à celle du problème cible sont choisies par la fonction `knearest_desc` (*note: en spécifiant `k`, au plus `k` valeurs seront choisies, sinon toutes seront renvoyées*). Les sous graphes obtenus avec ces valeurs sont parcourus de la même manière, puis la valeur amenant le prix le plus faible est retenue. Le critère du prix le plus faible a été choisi, mais d'autres critères pourraient être imaginés (*max, mean, etc.*). Cela dépend de l'utilisation que l'on a du système. Dans notre cas, nous chercherons à obtenir l'estimation minimale d'un bien. La fonction permet donc de récupérer récursivement le cas source. Par ailleurs, les critères de similarité sont définis dans la constante `DESCRIPTEURS_FN`, associant une fonction de similarité à un descripteur.
#### Adaptation
L'adaptation du cas source pour le problème cible est réalisée par la fonction `estimate(search,result)`, l'argument `search` étant un dictionnaire python contenant le problème cible et l'argument `result` un dictionnaire python contenant le cas source choisi. Le prix estimé est calculé en ajoutant une valeur D<sub>price</sub> à au prix du cas source : 
<p align="center">
    <img src="https://render.githubusercontent.com/render/math?math=P_{estimate}=P_{source} %2B D_{price}"> 
</p>  
<p align="center">
    <img src="https://render.githubusercontent.com/render/math?math=$D_{price} = \sum_{n=d}^{descripteurs} (result_d - search_d) * weight_d$">  
</p>  

Les poids associés à un descripteur sont stockés dans la constante `DESCRIPTEURS_WEIGHTS`. À noter que pour des descripteurs contenant des valeurs de type *string*, le poids associé est un dictionnaire contenant (ou non) un déficit pour la valeur. Par exemple : pour le descripteur *quartier*, le dictionnaire contient des déficits chaque valeur (Talence, Cenon, etc.), plus le quartier est recherché, plus le déficit est faible. Ainsi, si un cas source se trouve dans un quartier plus rercherché que le problème cible, son déficit sera moins élevé que celui du problème, donc la valeur du prix diminuera. Et inversement.

## Expériences et résultats
- test_model
- grid_search
- résultats de merde


## Exécution

### Pré-requis
- [Python3](https://www.python.org/downloads/)
- modules complémentaires : [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/) (`pip install pandas numpy`)

### Run 
Pour estimer le prix d'une maison :  
*Applique le raisonnement Remémoration - Adaptation pour estimer le prix du bien selon les critères donnés, à partir de la base de cas.*
```
python3 ./estimator.py 
    --quartier=<str>
    --pieces=<int>
    --surface=<int>
    --terrain=<int>
    [ optional --debug ]
```
  
Pour tester le modèle sur la base de cas :  
*Test la précision du modèle `nb_epochs` fois en estimant des biens dont on connait le prix.*
```
python3 ./estimator.py 
    --test_model=<nb_epochs>
```


## Documentation
Une documentation du code est disponible dans le fichier `estimator.html` (pour la visualiser: `firefox estimator.html`)


## Auteurs 
- Gaspard GOUPY
- Titouan KNOCKAERT


# Licence
Voir [Licence](LICENCE.md)
