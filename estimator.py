import sys
import pandas as pd
import networkx as nx

# Descripteurs 
# On se focalise sur des maisons
# Ville / Quartier
# Prix 
# Surface 
# Terrain 
# Pieces


data = pd.read_csv('./db.csv', sep=',')


def compute_mean_price(data, search):
    data_sub = get_rows_by(data,search)
    return int(data_sub["prix"].sum() / data_sub["surface"].sum())


def get_rows_by(data, search):
    rows = data
    for key in search:
        rows = rows[rows[key] == search[key]]
    return rows


def create_graph_db():
    graph = {key: {} for key in data["quartier"]}   

    for quartier in graph:
        data_sub = get_rows_by(data,{"quartier":quartier})
        graph[quartier] = {
            pieces: {
                surface: {
                    terrain: {
                       compute_mean_price(data, {"quartier":quartier, "surface":surface, "terrain":terrain, "pieces":pieces} )
                    }
                    for terrain in get_rows_by(data,{"quartier":quartier, "surface":surface, "pieces":pieces})["terrain"]
                }
                for surface in get_rows_by(data,{"quartier":quartier, "pieces":pieces})["surface"]
            }
        for pieces in data_sub["pieces"]}

    return graph



def search_in_graph(graph, search):
    sub_graph = graph
    for key in search:
        sub_graph = sub_graph[key]
    return sub_graph


def get_similars(graph, pb):
    sub_graph = search_in_graph(graph, {pb["quartier"],pb["pieces"]})
    return sub_graph

#print(data)
graph_dict = create_graph_db()
#print(graph_dict)

sims = get_similars (
    graph_dict, {
        "quartier":"Cenon",
        "pieces":4,
    }
)
print(sims)



#g = nx.DiGraph(graph_dict)
#print(g)

#nx.draw_networkx(g)