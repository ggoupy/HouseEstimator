# HOUSE ESTIMATOR


## Contexte

*House Estimator* est un projet réalisé dans le cadre de l'UE "Dynamique des connaissances" du Master 2 IA de [l'université Claude Bernard Lyon 1](https://www.univ-lyon1.fr/). Il a été encadré par [Béatrice Fuchs](https://perso.liris.cnrs.fr/beatrice.fuchs/) et aborde la thématique du raisonnement à partir de cas. 


## Objectif 

L'objectif du projet était de concevoir un système simple de raisonnement à partir de cas. Ces systèmes sont utilisés pour résoudre de nouveaux problèmes, en réutilisant des solutions de problèmes antérieurs résolus. Ici, nous nous sommes intéressé au cas de l'estimation des biens immobiliers, et en particulier des maisons dans la région Bordelaise.


## Exécution

### Pré-requis
- [Python3](https://www.python.org/downloads/)
- [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/) (`pip install pandas numpy`)

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
*Test la précision du modèle `nb_epochs` fois, en estimant des biens dont on connait déjà le prix.*
```
python3 ./estimator.py 
    --test_model=<nb_epochs>
```


## Implémentation

### Base de cas
La base de cas a été constituée manuellement, à partir du site [seloger.com](https://www.seloger.com/). Elle est composée de **50 exemples**, dotés des caractéristiques (descripteurs) suivantes :
- **Quartier** : position géographique du bien (regroupe quartiers et communes limitrophes)
- **Pièces** : nombre de pièces dans l'habitation
- **Surface** : surface habitable en m<sup>2</sup>
- **Terrain** : terrain en m<sup>2</sup>
- **Prix** : prix de vente, en euros

### Programme
Cette section détaille le cycle suivi par le système.  

#### 1. Indexation de la base de cas
La base de cas est stockée dans le fichier `db.csv`. À l'exécution, le système lit la base de donnée à l'aide du module `pandas` et construit une base de cas indexée (*graphe*), sous la forme d'un dictionnaire python. La création du graphe est réalisée par la fonction `create_graph_from_db(db)`, construisant les noeuds récursivement à l'aide des descripteurs (caractéristiques) définis dans la constante `DESCRIPTEURS`. L'ordre dans la liste est important car il correspond à l'ordre des noeuds dans la base indexée. Dans l'éventualité *-très rare-* où plusieurs cas seraient similaires, ils sont fusionnés (fonction `compute_price(rows)`) et le prix stocké est calculé par la moyenne de ces cas. À noter que ce n'est pas la seule manière de calculer ce prix (*max, min, etc.*). Par ailleurs, les prix sont sont convertis en prix / m<sup>2</sup> dans la base indexée, afin d'améliorer la précision du modèle lors de l'adaptation. L'idée est de "normaliser" les prix pour pouvoir les comparer. 

#### 2. Remémoration 
La remémoration d'un cas source à partir du problème cible donné est réalisée par la fonction `find_similar(graph,search)`; l'argument `graph` étant la base de cas indexée et l'argument `search` un dictionnaire python contenant le problème cible. Cette fonction cherche dans le graphe le cas source le plus similaire à un problème cible, selon des critères de similarité définis. Pour cela, à chaque niveau (représentant un descripteur), les valeurs du descripteur les plus proches à celle du problème cible sont choisies par la fonction `knearest_desc` (*nb: en spécifiant `k`, au plus `k` valeurs seront choisies, sinon toutes seront renvoyées*). Les sous graphes obtenus avec ces valeurs sont parcourus de la même manière, puis la valeur amenant le prix le plus faible est retenue. La fonction permet donc de récupérer récursivement un cas source. Le critère du prix le plus faible a été choisi, mais d'autres critères pourraient être imaginés (*max, mean, etc.*). Cela dépend de l'utilisation que l'on a du système : dans notre cas, nous cherchons à minimiser l'estimation d'un bien, afin d'imaginer sa valeur possible, par exemple. Par ailleurs, les critères de similarité sont définis dans la constante `DESCRIPTEURS_FN`, associant une fonction de similarité à un descripteur. Pour les valeurs de type *number* (*i.e pieces, surface, terrain, prix*), il n'est pas nécessaire de définir des valeurs symboliques, la hiérarchisation se faisant sur le nombre en lui-même. Pour les valeurs de type *string* (*quartier*), aucune représentation symbolique n'a été réalisée car cela impliquerait de noter chaque quartier possible, ce qui est exhaustif... Nous avons tout de même procédé ainsi pour l'adaptation, afin d'obtenir plus de cohérence dans nos résultats. Pour conclure sur ce point, il serait intéressant d'intégrer une abstraction/généralisation des valeurs. En effet, les comparaisons sur des entiers (notamment pour les descripteurs *terrain et surface*) peuvent réduire grandement le nombre de cas similaires trouvés. Ces valeurs pourraient être converties en ordre de grandeur (*eg: Petit, moyen, grand*).

#### 3. Adaptation
L'adaptation du cas source pour le problème cible est réalisée par la fonction `estimate(search,result)`; l'argument `search` étant un dictionnaire python contenant le problème cible et l'argument `result` un dictionnaire python contenant le cas source choisi. Le prix estimé est calculé en ajoutant une valeur D<sub>price</sub> au prix du cas source : 
<p align="center">
    <img src="https://render.githubusercontent.com/render/math?math=P_{estimate}=P_{source} %2B D_{price}"> 
</p>  
<p align="center">
    <img src="https://render.githubusercontent.com/render/math?math=$D_{price} = \sum_{n=d}^{descripteurs} (result_d - search_d) * weight_d$">  
</p>  

Les poids associés à un descripteur sont stockés dans la constante `DESCRIPTEURS_WEIGHTS`. À noter que pour des descripteurs contenant des valeurs de type *string*, le poids associé est un dictionnaire contenant (ou non) un déficit pour la valeur. Par exemple : pour le descripteur *quartier*, le dictionnaire contient des déficits chaque quartier (Talence, Cenon, etc.). Plus le quartier est recherché, plus le déficit est faible. Ainsi, si un cas source se trouve dans un quartier plus rercherché que le problème cible, son déficit sera moins élevé que celui du problème, donc la valeur du prix diminuera. Et inversement.

#### 4. Mémorisation
Les résultats obtenus (voir *Expériences et résultats*) n'étant pas assez précis, aucune mémorisation n'a été implémenté, afin de ne pas altérer la base de cas. Cependant, cette étape consisterait seulement à ajouter une nouvelle ligne dans `db.csv` et à mettre à jour la base indexée.



## Expériences et résultats
Cette section détaille les expériences réalisées pour tester la précision du système.  
La fonction `test_model(nb_epochs)` permet de mesurer l'erreur moyenne dans la prédiction sur `nb_epochs`. Pour cela, à chaque itération, une cas est tiré aléatoirement et uniformément, puis retiré de la base de cas. Son prix est déjà connu mais le système va l'estimer en suivant le cycle décrit dans la section [Programme](#Programme). Ainsi, le pourcentage de différence (variation) entre le prix réel et le prix estimé peut être calculé par la formule :   
<p align="center">
    <img src="https://render.githubusercontent.com/render/math?math=error = \frac{p_{reel} - p_{estimate}}{p_{estimate}} * 100">  
</p>   
La moyenne des différences (en valeur absolue) est ensuite calculée, afin d'estimer la précision globale du système. Il faut tout de même mentionner que cette précision est relative à la base de cas et peut varier sur des problèmes nouveaux.  
   
Afin de trouver des poids adaptés, la fonction `grid_search()` a été implémentée. Elle permet de tester des combinaisons de poids données, pour chaque descripteur, afin de trouver la meilleure. Pour cela, des plages de valeurs sont définies pour tous les poids, et la fonction mesure la précision pour chaque combinaison possible, avec la fonction `test_model(nb_epochs=30)`. Ensuite, il suffit de choisir la combinaison optimale, *c.a.d* celle ayant le pourcentage d'erreur minimum. Il est là aussi important de mentionner que ces paramètres s'adaptent à la base de cas connue, les tests étant réalisés dessus. Si celle-ci venait à changer, les poids pourraient ne pas donner des résultats précis. *Nb: la fonction grid_search n'est pas très élégante, ni modulable, mais a été implémentée dans le but d'automatiser la recherche de poids.*  
Les poids optimaux trouvés sont :
- **Quartier** : *-3000 * rang du quartier*
- **Pièces** : *-200*
- **Surface** : *-3*
- **Terrain** : *-2*
    
En utilisant les poids optimaux, sur 100 estimations, nous obtenons un pourcentage d'erreur moyen de **~30.96%**. Concrètement, si le prix réel d'un bien est de 3000 € / m<sup>2</sup>, le prix estimé pourra être de 2300 € / m<sup>2</sup>. Sur une maison de 100m<sup>2</sup>, on passe donc d'une valeur de 300,000 € à 230,000 € ! *Sacrée promotion...* Les estimations obtenues ne sont donc pas très fiables. Cela s'explique par plusieurs points, pouvant faire l'objet d'améliorations futures : 
- La base de cas est trop petite et les données ne sont pas assez fiables (prix sur/sous-estimé).
- Le nombre de descripteurs n'est pas assez élevé, ne permettant pas une bonne généralisation par l'Adaptation.
- Les paramètres d'adaptation (poids) pourraient être affinés.
- Certaines valeurs de descripteurs devraient être abstraits/généralisés (*eg: surface et terrain*).
- La Remémoration pourrait renvoyer le cas le plus proche ayant le prix le plus élevé (au lieu de celui ayant le prix le plus faible), ou en faisant une moyenne des prix.



## Documentation
Une documentation du code est disponible dans le fichier `estimator.html` (pour la visualiser: `firefox estimator.html`)


## Auteurs 
- Gaspard GOUPY
- Titouan KNOCKAERT


# Licence
Voir [Licence](LICENCE.md)
