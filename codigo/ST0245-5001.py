#Importación de los modulos necesarios, lectura del archivo CSV y Reemplazar los valores NaN en la columna de 'harassmentRisk'
from math import radians, sin, cos, asin, sqrt
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from queue import PriorityQueue
import folium
import pandas as pd
import random

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

#Metodo para obtener el nombre de una calle con sus coordenadas
def coordinateToStreet(coordinate: tuple) -> str:
    localizator = Nominatim(user_agent = "SecurityON")
    location = localizator.reverse("{},{}".format(coordinate[0],coordinate[1]))
    return str(location)

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

#Metodo para corregir el formato del tiempo
def correct_time(n):
  x = n
  nint = int(x)
  sobrante = int((x % 1) * 60)
  if nint == 0 and sobrante != 1:
    return(f'{sobrante} minutos')
  elif nint == 0 and sobrante == 1:
    return(f'{sobrante} minuto')
  elif nint != 1 and sobrante == 0:
    return(f'{nint} horas')
  elif nint == 1 and sobrante == 0:
    return(f'{nint} hora')
  elif nint == 1 and sobrante == 1:
    return(f'{nint} hora y {sobrante} minuto')
  elif nint == 1 and sobrante != 1:
    return(f'{nint} hora y {sobrante} minutos')
  elif nint != 1 and sobrante == 1:
    return(f'{nint} horas y {sobrante} minuto')
  elif nint != 1 and sobrante != 1:
    return(f'{nint} horas y {sobrante} minutos')

#Metodo para generar el mapa con la ruta
def create_map(path, path2, path3):
    mapa = folium.Map(location=[path[0][0], path[0][1]], zoom_start = 100) #, tiles='cartodbdark_matter'

    kilo1 = 0
    kilo2 = 0
    kilo3 = 0

    for i in range(1, len(path)):
      kilo1 += geodesic([path[i-1][0], path[i-1][1]], [path[i][0], path[i][1]]).kilometers
    for i in range(1, len(path2)):
      kilo2 += geodesic([path2[i-1][0], path2[i-1][1]], [path2[i][0], path2[i][1]]).kilometers
    for i in range(1, len(path3)):
      kilo3 += geodesic([path3[i-1][0], path3[i-1][1]], [path3[i][0], path3[i][1]]).kilometers
    prom_vel = random.randrange(4,6)
    prom_vel1 = kilo1 / prom_vel
    prom_vel2 = kilo2 / prom_vel
    prom_vel3 = kilo3 / prom_vel

    if kilo1 < 1.0:
      kilo1 *= 1000
      kilo1 = f'{kilo1:.2f} metros'
    else:
      kilo1 = f'{kilo1:.2f} kilómetros'
    if kilo2 < 1.0:
      kilo2 *= 1000
      kilo2 = f'{kilo2:.2f} metros'
    else:
      kilo2 = f'{kilo2:.2f} kilómetros'
    if kilo3 < 1.0:
      kilo3 *= 1000
      kilo3 = f'{kilo3:.2f} metros'
    else:
      kilo3 = f'{kilo3:.2f} kilómetros'

    folium.TileLayer('OpenStreetMap').add_to(mapa)
    folium.TileLayer('Stamen Terrain').add_to(mapa)
    folium.TileLayer('Stamen Toner').add_to(mapa)
    folium.TileLayer('Stamen Water Color').add_to(mapa)
    folium.TileLayer('cartodbpositron').add_to(mapa)
    folium.TileLayer('cartodbdark_matter').add_to(mapa)

    f1 = folium.FeatureGroup("Ruta Rápida")
    f2 = folium.FeatureGroup("Ruta Segura")
    f3 = folium.FeatureGroup("Ruta Promedio")

    ubi1 = coordinateToStreet((path[0][0], path[0][1])).split(',')
    ubi2 = coordinateToStreet((path2[0][0], path2[0][1])).split(',')
    ubi3 = coordinateToStreet((path3[0][0], path3[0][1])).split(',')

    dest1 = coordinateToStreet((path[-1][0], path[-1][1])).split(',')
    dest2 = coordinateToStreet((path2[-1][0], path2[-1][1])).split(',')
    dest3 = coordinateToStreet((path3[-1][0], path3[-1][1])).split(',')

    riesgos1 = ""
    if risk_rapida > 0.1 and risk_rapida < 0.5:
      riesgos1 = f'{risk_rapida:.5f} - el camino es seguro'
    elif risk_rapida > 0.5 and risk_rapida < 0.6:
      riesgos1 = f'{risk_rapida:.5f} - el camino un poco inseguro'
    else:
      riesgos1 = f'{risk_rapida:.5f} - el camino es muy inseguro'

    riesgos2 = ""
    if risk_segura > 0.1 and risk_segura < 0.5:
      riesgos2 = f'{risk_segura:.5f} - el camino es seguro'
    elif risk_segura > 0.5 and risk_segura < 0.6:
      riesgos2 = f'{risk_segura:.5f} - el camino un poco inseguro'
    else:
      riesgos2 = f'{risk_segura:.5f} - el camino es muy inseguro'

    riesgos3 = ""
    if risk_prom > 0.1 and risk_prom < 0.5:
      riesgos3 = f'{risk_prom:.5f} - el camino es seguro'
    elif risk_prom > 0.5 and risk_prom < 0.6:
      riesgos3 = f'{risk_prom:.5f} - el camino un poco inseguro'
    else:
      riesgos3 = f'{risk_prom:.5f} - el camino es muy inseguro'


    pp1 = folium.Html('<h3>Ruta más rápida</h3>' + f'<strong>Ubicación: {ubi1[0]}, {ubi1[1]}, {ubi1[2]}</strong>' + f'<p>Origen: {path[0][0], path[0][1]}</p>', script=True)
    popup1 = folium.Popup(pp1, max_width=2650)
    pp2 = folium.Html('<h3>Ruta más segura</h3>' + f'<strong>Ubicación: {ubi2[0]}, {ubi2[1]}, {ubi2[2]}</strong>' + f'<p>Origen: {path2[0][0], path2[0][1]}</p>', script=True)
    popup2 = folium.Popup(pp2, max_width=2650)
    pp3 = folium.Html('<h3>Ruta promedio</h3>' + f'<strong>Ubicación: {ubi3[0]}, {ubi3[1]}, {ubi3[2]}</strong>' + f'<p>Origen: {path3[0][0], path3[0][1]}</p>', script=True)
    popup3 = folium.Popup(pp3, max_width=2650)

    pp11 = folium.Html('<h3>Ruta más rápida</h3>' + f'<strong>Ubicación: {dest1[0]}, {dest1[1]}, {dest1[2]}</strong>' + f'<p>Destino: {path[-1][0], path[-1][1]}</p>' + f'<p>Riesgo: {riesgos1}</p>' + f'<p>Distancia: {kilo1}</p>' + f'<p>A una velocidad promedio de {prom_vel} km/h</p>' + f'<p>su tiempo estimado de llegada es de {correct_time(prom_vel1)}</p>', script=True)
    popup11 = folium.Popup(pp11, max_width=2650)
    pp22 = folium.Html('<h3>Ruta más segura</h3>' + f'<strong>Ubicación: {dest2[0]}, {dest2[1]}, {dest2[2]}</strong>' + f'<p>Destino: {path2[-1][0], path2[-1][1]}</p>' + f'<p>Riesgo: {riesgos2}</p>' + f'<p>Distancia: {kilo2}</p>' + f'<p>A una velocidad promedio de {prom_vel} km/h</p>' + f'<p>su tiempo estimado de llegada es de {correct_time(prom_vel2)}</p>', script=True)
    popup22 = folium.Popup(pp22, max_width=2650)
    pp33 = folium.Html('<h3>Ruta promedio</h3>' + f'<strong>Ubicación: {dest3[0]}, {dest3[1]}, {dest3[2]}</strong>' + f'<p>Destino: {path3[-1][0], path3[-1][1]}</p>' + f'<p>Riesgo: {riesgos3}</p>' + f'<p>Distancia: {kilo3}</p>' + f'<p>A una velocidad promedio de {prom_vel} km/h</p>' + f'<p>su tiempo estimado de llegada es de {correct_time(prom_vel3)}</p>', script=True)
    popup33 = folium.Popup(pp33, max_width=2650)

    folium.Marker(location=[path[0][0], path[0][1]], popup=popup1, tooltip= '<strong>Ruta Rápida - Origen</strong>', icon=folium.Icon(color='red', prefix='glyphicon', icon='off')).add_to(f1)
    folium.Marker(location=[path2[0][0], path2[0][1]], popup=popup2, tooltip='<strong>Ruta Segura - Origen</strong>', icon=folium.Icon(color='red', prefix='fa',icon='heart')).add_to(f2)
    folium.Marker(location=[path3[0][0], path3[0][1]], popup=popup3, tooltip='<strong>Ruta Promedio - Origen</strong>', icon=folium.Icon(color='red', prefix='fa',icon='anchor')).add_to(f3)

    folium.Marker(location=[path[-1][0], path[-1][1]], popup=popup11, tooltip='<strong>Ruta Rápida - Destino</strong>', icon=folium.Icon(color='blue', prefix='glyphicon', icon='off')).add_to(f1)
    folium.Marker(location=[path2[-1][0], path2[-1][1]], popup=popup22, tooltip='<strong>Ruta Segura - Destino</strong>', icon=folium.Icon(color='green', prefix='fa',icon='heart')).add_to(f2)
    folium.Marker(location=[path3[-1][0], path3[-1][1]], popup=popup33, tooltip='<strong>Ruta Promedio - Destino</strong>', icon=folium.Icon(color='purple', prefix='fa',icon='anchor')).add_to(f3)

    folium.PolyLine(path, color='blue', weigth=15, tooltip='Ruta Rápida').add_to(f1) #Rapida
    folium.PolyLine(path2, color='green', weigth=15, tooltip='Ruta Segura').add_to(f2) #Segura
    folium.PolyLine(path3, color='purple', weigth=15, tooltip='Ruta Promedio').add_to(f3) #Prom

    f1.add_to(mapa)
    f2.add_to(mapa)
    f3.add_to(mapa)
    folium.LayerControl().add_to(mapa)
    mapa.save('routes.html')

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


starts = aproximate_coord((6.200200035354179, -75.57755148832867))
target = aproximate_coord((6.26202374889627, -75.57729130409341))

rapida = DjikstraTird(graphCM,0,starts, target)
risk_rapida = risk
segura = DjikstraTird(graphCM,2,starts, target)
risk_segura = risk
prom = DjikstraTird(graphCM,1,starts, target)
risk_prom = risk

create_map(rapida, segura, prom)