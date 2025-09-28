from flask import Blueprint, request, jsonify
import pandas as pd
from app.utils.calculos import calculo_precipitacoes, problema_inverso_idf, indice_spi, tutorial_idf, teoria_idf, pbl_idf, tutorial_spi, teoria_spi, pbl_spi

spi = Blueprint('spi', __name__)

# Variáveis globais
h_max1, preciptacao, intensidade, df_longo, media, desvio_padrao
df = None
response_data = {}


@idf_bp.route('/spi', methods=['POST', 'GET'])
def spi():
    global h_max1, preciptacao, intensidade, df_longo, media, desvio_padrao, df


    if request.method == 'POST':
        file = request.files.get('arq1')
        if file:
            df = pd.read_csv(file, sep=';', skiprows=10)
            print(f"[POST /spi] Arquivo recebido: {df.shape}")

            h_max1, preciptacao, intensidade, df_longo, media, desvio_padrao = calculo_precipitacoes(df)
            a, b, c, d = problema_inverso_idf(df_longo)
            return jsonify({
                'h_max1': h_max1,
                'preciptacao': preciptacao,
                'intensidade': intensidade,
                'df_longo': df_longo,
                'media': media,
                'desvio_padrao':desvio_padrao
            })

    elif request.method == 'GET':
        response_data = {
            'h_max1': h_max1,
                'preciptacao': preciptacao,
                'intensidade': intensidade,
                'df_longo': df_longo,
                'media': media,
                'desvio_padrao':desvio_padrao
        }
        return jsonify(response_data)
