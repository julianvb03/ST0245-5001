import pandas as pd
df = pd.read_csv(r'calles_de_medellin_con_acoso.csv', sep=";")
deSara = {(6.2060586, -75.5687224): (37.34, 0.3021730539710254, 18.821086526985514), (6.2063043, -75.5681218): (63.401, 0.3021730539710254, 31.851586526985514), (6.2073652, -75.5685931): (108.671, 0.3021730539710254, 54.48658652698552), (6.2063061, -75.5715105): (334.387, 0.3021730539710254, 167.34458652698552)}
demio ={'(-75.5687224, 6.2060586)': (37.34, 0.3021730539710254), '(-75.5681218, 6.2063043)': (63.401, 0.3021730539710254), '(-75.5685931, 6.2073652)': (108.671, 0.3021730539710254), '(-75.5715105, 6.2063061)': (334.387, 0.3021730539710254)}
print(deSara.keys())
print(demio.keys())


def crearGrafo() -> dict:
    uOrigin = pd.unique(df['origin'])
    grafo = {}
    for origin in uOrigin:
        grafo[origin] = {}
    for index in df.index:
        if df['destination'][index] in grafo:
            if df['oneway'][index]:
                grafo[df['origin'][index]] = grafo[df['origin'][index]] | {df['destination'][index]:(df['length'][index],df['harassmentRisk'][index])}
                grafo[df['destination'][index]] = grafo[df['destination'][index]] | {df['origin'][index]:(df['length'][index],df['harassmentRisk'][index])}
            else: grafo[df['origin'][index]] = grafo[df['origin'][index]] | {df['destination'][index]:(df['length'][index],df['harassmentRisk'][index])}
        else:
            if df['oneway'][index]:
                grafo[df['destination'][index]] = {}
                grafo[df['origin'][index]] = grafo[df['origin'][index]] | {df['destination'][index]:(df['length'][index],df['harassmentRisk'][index])}
                grafo[df['destination'][index]] = grafo[df['destination'][index]] | {df['origin'][index]:(df['length'][index],df['harassmentRisk'][index])}

    return grafo

tupla1 = (23,4)
tupla2 = (23,4)
tupla3 = (4,23)
print(tupla1 == tupla2)
print(tupla1 == tupla3)
print(tupla2 == tupla3)
print(type(tupla1))
lista = [(23,4)]
print(tupla1 in lista)

    '''
            if df['oneway'][index]:
                graph[originIteration] = graph[originIteration] | {destinationIteration:(df['length'][index],df['harassmentRisk'][index])}
                graph[destinationIteration] = graph[destinationIteration] | {originIteration:(df['length'][index],df['harassmentRisk'][index])}
            else: graph[originIteration] = graph[originIteration] | {destinationIteration:(df['length'][index],df['harassmentRisk'][index])}
        else:
            if df['oneway'][index]:
                graph[destinationIteration] = {}
                graph[originIteration] = graph[originIteration] | {destinationIteration:(df['length'][index],df['harassmentRisk'][index])}
                graph[destinationIteration] = graph[destinationIteration] | {originIteration:(df['length'][index],df['harassmentRisk'][index])}
'''
    return graph