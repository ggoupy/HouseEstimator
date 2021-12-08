# HOUSE ESTIMATOR


## Contexte

*House Estimator* est un projet réalisé dans le cadre de l'UE "Dynamique des connaissances" du Master 2 IA de [l'université Claude Bernard Lyon 1](https://www.univ-lyon1.fr/). Il a été encadré par [Béatrice Fuchs](https://perso.liris.cnrs.fr/beatrice.fuchs/) et aborde la thématique du raisonnement à partir de cas. 


## Objectif 

L'objectif du projet était de concevoir un système simple de raisonnement à partir de cas. Le but de ce système est de résoudre de nouveaux problèmes, en réutilisant des solutions de problèmes antérieurs résolus. Ici, nous allons nous intéresser au cas de l'estimation des biens immobilers, et en particulier des maisons dans la région Bordelaise.


## Conception

### Base de cas
La base de cas a été constituée manuellement, à partir du site [seloger.com](https://www.seloger.com/). Elle est composée de de **50 exemples**, contenant les caractéristiques suivantes :
- **Quartier** : position géographique du bien (regroupe quartiers et communes limitrophes)
- **Pièces** : nombre de pièces
- **Surface** : surface habitable en m<sup>2</sup>
- **Terrain** : terrain en m<sup>2</sup>
- **Prix** : total, en euros

### Programme
TODO


## Execution

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
