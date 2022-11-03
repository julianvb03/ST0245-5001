#Importación de los modulos necesarios y lectura del archivo CSV
import pandas as pd
import gmplot
from geopy.geocoders import Nominatim

df = pd.read_csv(r'calles_de_medellin_con_acoso.csv', sep=";")

#Metodo para corregir las coordenadas
def correctFormat(text: str) -> tuple:
    textProcess = text[1:-1]
    partB, partA = textProcess.split(",")
    listReturn = [float(partA),float(partB)]
    return tuple(listReturn)

#Metodo para obtener el nombre de una calle con sus coordenadas
def coordinateToStreet(coordinate: tuple) -> str:
    localizator = Nominatim(user_agent = "SecurityON")
    location = localizator.reverse("{},{}".format(coordinate[0],coordinate[1]))
    return location

#Metodo para sacar el promedio del acoso en toda la ciudad
def average() -> float:
    count = 0
    count2 = 0
    for iteration in df['harassmentRisk']:
        if pd.isnull(iteration):
            continue
        else:
            count2 += 1
            count += iteration
    return count / count2

#Reemplazar los valores NaN en la columna de 'harassmentRisk'
PROMEDIO = average()
df['harassmentRisk'].fillna(PROMEDIO, inplace=True)

#Metodo que crea el grafo
def createGrahp() -> dict:
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
                graph[originIteration] |= {destinationIteration:(df['length'][index],df['harassmentRisk'][index])}
                graph[destinationIteration] |= {originIteration:(df['length'][index],df['harassmentRisk'][index])}
            else: graph[originIteration] |= {destinationIteration:(df['length'][index],df['harassmentRisk'][index])}
        else:
            if df['oneway'][index]:
                graph[destinationIteration] = {}
                graph[originIteration] |= {destinationIteration:(df['length'][index],df['harassmentRisk'][index])}
                graph[destinationIteration] |= {originIteration:(df['length'][index],df['harassmentRisk'][index])}
            else: graph[originIteration] |= {destinationIteration:(df['length'][index],df['harassmentRisk'][index])}

    return graph

graphCM = createGrahp()

#Algoritmo que busca la ruta más corta, retorna una lista en orden con los nodos que representan dicha ruta
def DjikstraFirst(graph: dict, origin: tuple, destination: tuple) -> list:
    shortesdDistance = {}
    previusly = {}
    noVisiteds = graph
    CONTROLER = 999999
    shortestPath = []

    for node in noVisiteds:
        shortesdDistance[node] = CONTROLER
    shortesdDistance[origin] = 0

    while noVisiteds:
        minDistance = None
        for node in noVisiteds:
            if minDistance is None:
                minDistance = node
            elif shortesdDistance[node] < shortesdDistance[minDistance]:
                minDistance = node

        pahtOptions = graph[minDistance].items()

        for childNode, weight in pahtOptions:
            if weight[0] + shortesdDistance[minDistance] < shortesdDistance[childNode]:
                shortesdDistance[childNode] = weight[0] + shortesdDistance[minDistance]
                previusly[childNode] = minDistance

        noVisiteds.pop(minDistance)

    actualyNode = destination

    while actualyNode != origin:
        try:
            shortestPath.insert(0, actualyNode)
            actualyNode = previusly[actualyNode]
        except KeyError:
            return ["Error"]

    if shortesdDistance[destination] != CONTROLER:
        return shortestPath

route = DjikstraFirst(graphCM,(6.2099192, -75.5663399),(6.3003479,-75.5543665))

#Genera un archivo HTML con la ruta visualmente
def routhGenerator(lista: list) -> None:
    latitude = [x[0] for x in lista]
    lang = [x[1] for x in lista]
    gmapMedallo = gmplot.GoogleMapPlotter(lista[0][0], lista[0][1], 15)
    gmapMedallo.scatter(latitude, lang, '#F0F8FF', size = 50, marker = False)
    gmapMedallo.plot(latitude, lang, 'aliceblue', edge_width = 2)
    gmapMedallo.draw("Routh_Map.html")

routhGenerator(route)
