import folium
import pandas as pd
from flask import render_template, request
from . import vereadores_bp  # Importa o Blueprint

@vereadores_bp.route("/mapa_vereadores")
def mapa_vereadores():
    pass

    csv_path = '1tpelotas.csv'
    try:
        locais_votos = pd.read_csv(csv_path)
    except FileNotFoundError:
        return f"Erro: Arquivo '{csv_path}' não encontrado."

    locais_votos = locais_votos[locais_votos['DS_CARGO_PERGUNTA'] == 'Vereador']
    candidatos = sorted(locais_votos['NM_VOTAVEL'].unique())
    candidato_selecionado = request.args.get('candidato', candidatos[0])
    locais_filtrados = locais_votos[locais_votos['NM_VOTAVEL'] == candidato_selecionado]
    total_votos_candidato = locais_filtrados['QT_VOTOS'].sum()

    mapa = folium.Map(location=[-31.7400, -52.3000], zoom_start=12, tiles="Esri WorldStreetMap")
    max_votos = locais_filtrados['QT_VOTOS'].max()
    min_votos = locais_filtrados['QT_VOTOS'].min()

    for _, row in locais_filtrados.iterrows():
        latitude = row['LATITUDE']
        longitude = row['LONGITUDE']
        local = row['LOCAL']
        votos = row['QT_VOTOS']
        radius = 5 + (15 * (votos - min_votos) / (max_votos - min_votos)) if max_votos > min_votos else 5

        popup_content = f"""
            <html>
                <body>
                    <p><b>{local}</b></p>
                    <p>{votos} votos</p>
                </body>
            </html>
        """
        folium.CircleMarker(
            location=[latitude, longitude],
            radius=radius,
            color='#690000',
            fill=True,
            fill_color='#690000',
            fill_opacity=0.6,
            popup=folium.Popup(popup_content, max_width=300)
        ).add_to(mapa)

    locais_votos_totais = locais_votos.groupby('LOCAL').agg({'QT_VOTOS': 'sum'}).reset_index()
    locais_votos_totais = locais_votos_totais.sort_values(by='QT_VOTOS', ascending=False)

    lista_locais = []
    for _, row in locais_votos_totais.iterrows():
        local = row['LOCAL']
        total_votos_local = row['QT_VOTOS']
        votos_candidato_local = locais_filtrados[locais_filtrados['LOCAL'] == local]['QT_VOTOS'].sum()
        lista_locais.append({
            'LOCAL': local,
            'VOTOS_CANDIDATO': votos_candidato_local,
            'TOTAL_VOTOS_LOCAL': total_votos_local
        })

    lista_locais.sort(key=lambda x: x['VOTOS_CANDIDATO'], reverse=True)
    map_html = mapa._repr_html_()

    return render_template(
        'vereadores.html',
        candidatos=candidatos,
        candidato_selecionado=candidato_selecionado,
        map_html=map_html,
        lista_locais=lista_locais,
        total_votos_candidato=total_votos_candidato
    )
