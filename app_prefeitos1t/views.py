# app_prefeitos1t/views.py
from flask import render_template
from . import prefeitos1t  # Importando o Blueprint
import folium
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Usa o backend adequado para renderização sem interface gráfica
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Mapeamento de candidatos para cores
cores_candidatos = {
    'Branco': '#FFFFFF',
    'FERNANDO ESTIMA': '#9370db',
    'IRAJA RODRIGUES': '#b0c4de', 
    'JOÃO BOURSCEID': '#800000',
    'MARCIANO PERONDI': '#ffd700',
    'MARRONI': '#ff0000', 
    'Nulo': '#d2691e',
    'REGINALDO BACCI': '#228b22',
}

# Rota do Blueprint para o mapa
@prefeitos1t.route('/mapa_prefeitos1t')
def mapa_prefeitos1t():
    
    # Ler o CSV
    csv_path = '1tpelotas.csv'
    try:
        locais_votos = pd.read_csv(csv_path)
    except FileNotFoundError:
        return f"Erro: Arquivo '{csv_path}' não encontrado."

    # Filtrar apenas os prefeitos
    locais_votos = locais_votos[locais_votos['DS_CARGO_PERGUNTA'] == 'Prefeito']

    # Calcular o total de votos por local (independente do candidato)
    locais_votos_totais = locais_votos.groupby('LOCAL').agg({'QT_VOTOS': 'sum', 'LATITUDE': 'first', 'LONGITUDE': 'first'}).reset_index()

    # Calcular o vencedor de cada local (candidato com mais votos no local)
    locais_vencedores = locais_votos.groupby('LOCAL').apply(
        lambda x: x.loc[x['QT_VOTOS'].idxmax(), 'NM_VOTAVEL']
    ).reset_index(name='VENCEDOR')

    # Unir os dados para ter o vencedor e os votos totais
    locais_votos_totais = locais_votos_totais.merge(locais_vencedores, on='LOCAL')

    # Criar o mapa centralizado em Pelotas
    mapa_prefeito = folium.Map(location=[-31.7400, -52.3000], zoom_start=12, tiles="Esri WorldStreetMap")

    # Normalizar o tamanho das bolinhas proporcionalmente ao número total de votos no local
    max_votos = locais_votos_totais['QT_VOTOS'].max()
    min_votos = locais_votos_totais['QT_VOTOS'].min()

    for _, row in locais_votos_totais.iterrows():
        latitude = row['LATITUDE']
        longitude = row['LONGITUDE']
        local = row['LOCAL']
        votos = row['QT_VOTOS']
        vencedor = row['VENCEDOR']

        # Calcular o tamanho proporcional das bolinhas (escala de 5 a 20, por exemplo)
        radius = 5 + (15 * (votos - min_votos) / (max_votos - min_votos)) if max_votos > min_votos else 5

        # Definir a cor da bolinha com base no candidato vencedor
        color = cores_candidatos.get(vencedor, "#808080")  # Cor padrão cinza se o vencedor não for encontrado

        # Gerar o gráfico de pizza para o local
        votos_candidatos = locais_votos[locais_votos['LOCAL'] == local][['NM_VOTAVEL', 'QT_VOTOS']]
        labels = votos_candidatos['NM_VOTAVEL']
        sizes = votos_candidatos['QT_VOTOS']
        colors = [cores_candidatos.get(candidato, "#808080") for candidato in labels]

        plt.figure(figsize=(3, 3))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', textprops={'fontsize': 6}, labeldistance=1, startangle=10)

        # Salvar o gráfico como uma imagem base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=200)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        plt.close()

        # Criar o conteúdo do popup
        popup_content = f"""
            <html>
                <head>
                    <link href='https://fonts.googleapis.com/css2?family=Karla:ital,wght@0,200..800;1,200..800&display=swap' rel='stylesheet'>
                    <style>
                        .popup-text {{
                            font-family: 'Karla', serif;
                            font-size: 15px;
                        }}
                    </style>
                </head>
                <body>
                    <p class='popup-text'><b>Local:</b> {local}</p>
                    <p class='popup-text'><b>Total de votos:</b> {votos}</p>
                    <p class='popup-text'><b>Candidato vencedor:</b> {vencedor}</p>
                    <img src='data:image/png;base64,{image_base64}' width='400'>
                </body>
            </html>
        """

        folium.CircleMarker(
            location=[latitude, longitude],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=folium.Popup(popup_content, max_width=1000)
        ).add_to(mapa_prefeito)

    # Renderizar o mapa como HTML
    map_html_prefeitos = mapa_prefeito._repr_html_()

    # Renderizar o template com o mapa
    return render_template(
        'prefeitos1t.html',
        map_html_prefeitos=map_html_prefeitos
    )
