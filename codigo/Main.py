import pandas as pd
import Algoritmo
import Grafica

df = pd.read_csv(r'calles_de_medellin_con_acoso.csv', sep=";")
HARASSMENT_APROX = df['harassmentRisk'].mean()
df['harassmentRisk'].fillna(HARASSMENT_APROX, inplace=True)
def run():
    graphCM = Algoritmo.createGrahp(df)
    inicio = Algoritmo.aproximate_coord((6.200200035354179, -75.57755148832867))
    destino = Algoritmo.aproximate_coord((6.26202374889627, -75.57729130409341))

    rapida = Algoritmo.DjikstraTird(graphCM, 0, inicio, destino)
    risk_rapida = Algoritmo.risk
    segura = Algoritmo.DjikstraTird(graphCM, 2, inicio, destino)
    risk_segura = Algoritmo.risk
    prom = Algoritmo.DjikstraTird(graphCM, 1, inicio, destino)
    risk_prom = Algoritmo.risk

    Grafica.create_map(rapida, segura, prom, risk_rapida, risk_segura, risk_prom)

if __name__ == "__main__":
    run()