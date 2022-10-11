import pandas as pd
df = pd.read_csv(r'calles_de_medellin_con_acoso.csv', sep=";")
def crearGrafo():
    grafo = {}
    for origin in uOrigin:
        grafo[origin] = {}
    for index in df.index:
        if df['destination'][index] in grafo:
            if df['oneway'][index]:
                grafo[df['origin'][index]] = {df['destination'][index]:(df['length'][index],df['harassmentRisk'][index])}
                grafo[df['destination'][index]] = {df['origin'][index]:(df['length'][index],df['harassmentRisk'][index])}
            else: grafo[df['origin'][index]] = {df['destination'][index]:(df['length'][index],df['harassmentRisk'][index])}
        else:
            if df['oneway'][index]:
                grafo[df['destination']] = {}
                grafo[df['origin'][index]] = {df['destination'][index]:(df['length'][index],df['harassmentRisk'][index])}
                grafo[df['destination'][index]] = {df['origin'][index]:(df['length'][index],df['harassmentRisk'][index])}
            else: grafo[df['origin'][index]] = {df['destination'][index]:(df['length'][index],df['harassmentRisk'][index])}
    return grafo