#Importación de los modulos necesarios, lectura del archivo CSV y Reemplazar los valores NaN en la columna de 'harassmentRisk'
from geopy.geocoders import Nominatim
from queue import PriorityQueue
import pandas as pd
from math import radians, sin, cos, asin, sqrt
import folium

df = pd.read_csv(r'calles_de_medellin_con_acoso.csv', sep=";")
HARASSMENT_APROX = df['harassmentRisk'].mean()
df['harassmentRisk'].fillna(HARASSMENT_APROX, inplace=True)

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

#Aproximacion de coordenadas
def aproximation(coordinate: tuple):
    data = {}
    for index in df.index:
        coordinateF = 0
        coordinateS = 0

#Metodo para obtener el nombre de una calle con sus coordenadas
def coordinateToStreet(coordinate: tuple) -> str:
    localizator = Nominatim(user_agent = "SecurityON")
    location = localizator.reverse("{},{}".format(coordinate[0],coordinate[1]))
    return location

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

graphCM = createGrahp()

#Metodo para generar el mapa con la ruta
def create_map(path, path2, path3):
    mapa = folium.Map(location=[path[0][0], path[0][1]], zoom_start = 100)

    folium.TileLayer('Stamen Terrain').add_to(mapa)
    folium.TileLayer('Stamen Toner').add_to(mapa)
    folium.TileLayer('Stamen Water Color').add_to(mapa)
    folium.TileLayer('cartodbpositron').add_to(mapa)
    folium.TileLayer('cartodbdark_matter').add_to(mapa)

    f1=folium.FeatureGroup("Ruta Rápida") #Rapida
    f2=folium.FeatureGroup("Ruta Segura") #Segura
    f3=folium.FeatureGroup("Ruta Promedio") #Promedio
    pp1 = folium.Html('<h3>Ruta más rápida</h3>' + f'<p>Origen: {[path[0][0], path[0][1]]}</p>', script=True)
    popup1 = folium.Popup(pp1, max_width=2650)
    pp2 = folium.Html('<h3>Ruta más segura</h3>' + f'<p>Origen: {[path2[0][0], path2[0][1]]}</p>', script=True)
    popup2 = folium.Popup(pp2, max_width=2650)
    pp3 = folium.Html('<h3>Ruta promedio</h3>' + f'<p>Origen: {[path3[0][0], path3[0][1]]}</p>', script=True)
    popup3 = folium.Popup(pp3, max_width=2650)
    pp11 = folium.Html('<h3>Ruta más rápida</h3>' + f'<p>Destino: {[path[-1][0], path[-1][1]]}</p>', script=True)
    popup11 = folium.Popup(pp11, max_width=2650)
    pp22 = folium.Html('<h3>Ruta más segura</h3>' + f'<p>Destino: {[path2[-1][0], path2[-1][1]]}</p>', script=True)
    popup22 = folium.Popup(pp22, max_width=2650)
    pp33 = folium.Html('<h3>Ruta promedio</h3>' + f'<p>Destino: {[path3[-1][0], path3[-1][1]]}</p>', script=True)
    popup33 = folium.Popup(pp33, max_width=2650)
    folium.Marker(location=[path[0][0], path[0][1]], popup=popup1, tooltip='<strong>Click para ver origen</strong>', angle=30, icon=folium.Icon(color='blue', prefix='glyphicon', icon='off')).add_to(f1)
    folium.Marker(location=[path2[0][0], path2[0][1]], popup=popup2, tooltip='<strong>Click para ver origen</strong>', icon=folium.Icon(color='green', prefix='fa',icon='heart')).add_to(f2)
    folium.Marker(location=[path3[0][0], path3[0][1]], popup=popup3, tooltip='<strong>Click para ver origen</strong>', icon=folium.Icon(color='purple', prefix='fa',icon='anchor')).add_to(f3)
    folium.Marker(location=[path[-1][0], path[-1][1]], popup=popup11, tooltip='<strong>Click para ver destino</strong>', icon=folium.Icon(color='blue', prefix='glyphicon', icon='off')).add_to(f1)
    folium.Marker(location=[path2[-1][0], path2[-1][1]], popup=popup22, tooltip='<strong>Click para ver destino</strong>', icon=folium.Icon(color='green', prefix='fa',icon='heart')).add_to(f2)
    folium.Marker(location=[path3[-1][0], path3[-1][1]], popup=popup33, tooltip='<strong>Click para ver destino</strong>', icon=folium.Icon(color='purple', prefix='fa',icon='anchor')).add_to(f3)
    folium.PolyLine(path, color='blue', weigth=15, tooltip='Ruta Rápida').add_to(f1) #Rapida
    folium.PolyLine(path2, color='green', weigth=15, tooltip='Ruta Segura').add_to(f2) #Segura
    folium.PolyLine(path3, color='purple', weigth=15, tooltip='Ruta Promedio').add_to(f3) #Prom
    f1.add_to(mapa)
    f2.add_to(mapa)
    f3.add_to(mapa)
    folium.LayerControl().add_to(mapa)
    mapa.save('index.html')

#Metodo para encontrar la coordenada más cercana
def aproximate_coord(coordenadas: tuple):
    coords = list(graphCM.keys())[0]
    distance = haversine(coordenadas[0],coordenadas[1],coords[0],coords[1])
    for index in list(graphCM.keys()):
        actual = haversine(coordenadas[0],coordenadas[1],index[0],index[1])
        if distance > actual:
            distance = actual
            coords = index
        else: continue
    return coords

#Algoritmo de busqueda del camino
def DjikstraSecond(graph: dict, parameter: int, origin: tuple, destination: tuple) -> list:
    distances = {vertex : float("inf") for vertex in graph}
    previus = {vertex: 0 for vertex in graph}
    compares = PriorityQueue()
    ruta = []

    distances[origin] = 0
    compares.put((0,origin))

    while not compares.empty():
        vertexTuple = compares.get()
        vertex = vertexTuple[1]
        if vertex == destination: break
        for adyacent in graph[vertex]:
            weigth = graph[vertex][adyacent][parameter]
            if distances[adyacent] > distances[vertex] + weigth:
                distances[adyacent] = distances[vertex] + weigth
                previus[adyacent] = vertex
                compares.put((distances[adyacent],adyacent))

    actual = destination
    while actual != origin:
        ruta.insert(0,actual)
        actual = previus[actual]
    ruta.insert(0,origin)

    return ruta
#rapida = DjikstraSecond(graphCM,0,(6.2099192, -75.5663399),(6.3003479,-75.5543665))
#segura = DjikstraSecond(graphCM,1,(6.2099192, -75.5663399),(6.3003479,-75.5543665))
#prom = DjikstraSecond(graphCM,2,(6.2099192, -75.5663399),(6.3003479,-75.5543665))

#create_map(rapida, segura, prom)
print(graphCM[(6.2988698, -75.5494875)])
print(aproximate_coord((6.292474, -75.550242)))