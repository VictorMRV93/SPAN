
import pandas as pd

from geopy.distance import geodesic

from itertools import combinations

import os
 

# --- ETAPA 1: Ler o arquivo Excel ---

caminho_arquivo = 'Análise IA - Cluster.xlsx'  # Substitua pelo nome correto

df = pd.read_excel(caminho_arquivo, engine='openpyxl')

 

# --- ETAPA 2: Correção de coordenadas (vírgula -> ponto) ---

df['LATITUDE'] = df['LATITUDE'].astype(str).str.replace(',', '.', regex=False)

df['LONGITUDE'] = df['LONGITUDE'].astype(str).str.replace(',', '.', regex=False)

 

# Converter para float (ignorando valores inválidos)

df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce')

df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')

 

# --- ETAPA 3: Função de validação de coordenadas ---

def coordenadas_validas(lat, lon):

    return (-90 <= lat <= 90) and (-180 <= lon <= 180)

 

# --- ETAPA 4: Cálculo de distâncias com validação ---

resultados = []

 

# Agrupar por REGIONAL e CLUSTER

for (regional, cluster), grupo in df.groupby(['REGIONAL', 'CLUSTER']):

    cidades = grupo['CIDADE'].unique()

    if len(cidades) >= 2:

        for cidade1, cidade2 in combinations(cidades, 2):

            coord1 = grupo[grupo['CIDADE'] == cidade1].iloc[0][['LATITUDE', 'LONGITUDE']]

            coord2 = grupo[grupo['CIDADE'] == cidade2].iloc[0][['LATITUDE', 'LONGITUDE']]

            lat1, lon1 = coord1['LATITUDE'], coord1['LONGITUDE']

            lat2, lon2 = coord2['LATITUDE'], coord2['LONGITUDE']

            if all(coordenadas_validas(lat, lon) for lat, lon in [(lat1, lon1), (lat2, lon2)]):

                distancia = geodesic((lat1, lon1), (lat2, lon2)).km

            else:

                distancia = None  # Coordenadas inválidas

            resultados.append({

                'REGIONAL': regional,

                'CLUSTER': cluster,

                'CIDADE_1': cidade1,

                'CIDADE_2': cidade2,

                'DISTÂNCIA_KM': distancia

            })

 

# Criar DataFrame com os resultados

df_resultado = pd.DataFrame(resultados)

 

# --- ETAPA 5: Salvar em Excel ---

caminho_excel = os.path.join(os.getcwd(), 'distancias_entre_cidades_Cluster.xlsx')

df_resultado.to_excel(caminho_excel, index=False, engine='openpyxl')

 

print(f"\nArquivo Excel salvo em: {caminho_excel}")

print("\nResultado (5 primeiras linhas):")

print(df_resultado.head().to_string(index=False))

 
 
 