# HOUSE ESTIMATOR


## Contexte

*House Estimator* est un projet réalisé dans le cadre de l'UE "Dynamique des connaissances" du Master 2 IA de [l'université Claude Bernard Lyon 1](https://www.univ-lyon1.fr/). Il a été encadré par [Béatrice Fuchs](https://perso.liris.cnrs.fr/beatrice.fuchs/) et aborde la thématique du raisonnement à partir de cas. 


## Objectif 

L'objectif du projet était de concevoir un système simple de raisonnement à partir de cas. Le but de ce système est de ésoudre de nouveaux problèmes, en réutilisant des solutions de problèmes antérieurs résolus.


## Conception

### Base de cas
TODO

### Programme
TODO


## Execution

### Pré-requis
- [Python3](https://www.python.org/downloads/)
- modules complémentaires : [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/) (`pip install pandas numpy`)

### Run 
Pour estimer le prix d'une maison :
```
python3 ./estimator.py 
    --quartier=<str>
    --pieces=<int>
    --surface=<int>
    --terrain=<int>
    [ optional --debug ]
```
=> Applique le raisonnement *Remémoration* - *Adaptation* pour estimer le prix du bien selon les critères donnés, à partir de la base de cas.

Pour tester le modèle sur la base de cas : 
```
python3 ./estimator.py 
    --test_model=<nb_epochs>
```
=> Test la précision du modèle `nb_epochs` fois en estimant des biens dont on connait le prix.
