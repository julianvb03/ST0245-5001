from math import radians, sin, cos, asin, sqrt
from queue import PriorityQueue
import pandas as pd

#Metodo para corregir las coordenadas
def correctFormat(text: str) -> tuple:
    textProcess = text[1:-1]
    partB, partA = textProcess.split(",")
    listReturn = [float(partA),float(partB)]
    return tuple(listReturn)

#Metodo para aplicar la formula de Haversine
def haversine(latitude: float, longitude:float, latitude2: float, longitude2:float):
    RADIO = 6371
    lat1, lat2, lon1, lon2 = map(radians, [latitude, latitude2, longitude, longitude2])
    operation = 2 * RADIO * asin(sqrt(pow(sin((lat2 -lat1)/2),2) + cos(lat1)*cos(lat2) * pow(sin((lon2 - lon1)/2),2) ))
    return operation

#Metodo que crea el grafo
def createGrahp(df) -> dict:
    uniqueOrigins = pd.unique(df['origin'])
    graph = {}
    for origin in uniqueOrigins:
        correctOrigin = correctFormat(origin)
        graph[correctOrigin] = {}

    for index in df.index:
        originIteration = correctFormat(df['origin'][index])
        destinationIteration = correctFormat(df['destination'][index])
        if destinationIteration in graph:
            if df['oneway'][index]:
                graph[originIteration] |= {destinationIteration:(df['length'][index],df['harassmentRisk'][index],pow(df['length'][index], df['harassmentRisk'][index]))}
                graph[destinationIteration] |= {originIteration:(df['length'][index],df['harassmentRisk'][index],pow(df['length'][index], df['harassmentRisk'][index]))}
            else: graph[originIteration] |= {destinationIteration:(df['length'][index],df['harassmentRisk'][index],pow(df['length'][index], df['harassmentRisk'][index]))}
        else:
            if df['oneway'][index]:
                graph[destinationIteration] = {}
                graph[originIteration] |= {destinationIteration:(df['length'][index],df['harassmentRisk'][index],pow(df['length'][index], df['harassmentRisk'][index]))}
                graph[destinationIteration] |= {originIteration:(df['length'][index],df['harassmentRisk'][index],pow(df['length'][index], df['harassmentRisk'][index]))}
            else: graph[originIteration] |= {destinationIteration:(df['length'][index],df['harassmentRisk'][index],pow(df['length'][index], df['harassmentRisk'][index]))}

    return graph

#Metodo para encontrar la coordenada más cercana
def aproximate_coord(coordenadas: tuple, graph: dict):
    coords = list(graph.keys())[0]
    distance = haversine(coordenadas[0],coordenadas[1],coords[0],coords[1])
    for index in list(graph.keys()):
        actual = haversine(coordenadas[0],coordenadas[1],index[0],index[1])
        if distance > actual:
            distance = actual
            coords = index
        else: continue
    return coords

#Algortitmo de busqueda
def DjikstraTird(graph: dict, parameter: int, origin: tuple, destination: tuple) -> list:
    distances = {vertex : [float("inf"),0] for vertex in graph}
    previus = {vertex: 0 for vertex in graph}
    compares = PriorityQueue()
    global risk
    harasment = 0
    ruta = []

    distances[origin] = [0,0]
    compares.put((0,origin))

    while not compares.empty():
        vertexTuple = compares.get()
        vertex = vertexTuple[1]
        if vertex == destination: break
        for adyacent in graph[vertex]:
            weigth = graph[vertex][adyacent][parameter]
            harasment = graph[vertex][adyacent][1]
            if distances[adyacent][0] > distances[vertex][0] + weigth:
                distances[adyacent][0] = distances[vertex][0] + weigth
                distances[adyacent][1] = distances[vertex][1] + harasment
                previus[adyacent] = vertex
                compares.put((distances[adyacent],adyacent))

    actual = destination
    while actual != origin:
        harasment += distances[actual]
        ruta.insert(0,actual)
        actual = previus[actual]
    ruta.insert(0,origin)
    harasment = distances[ruta[-2]][1]
    risk = harasment / len(ruta)

    return ruta