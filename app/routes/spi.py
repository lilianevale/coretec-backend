from flask import Blueprint, request, jsonify
import pandas as pd
from app.utils.calculos import calculo_precipitacoes, problema_inverso_idf, indice_spi, tutorial_idf, teoria_idf, pbl_idf, tutorial_spi, teoria_spi, pbl_spi

spi = Blueprint('spi', __name__)

# Variáveis globais
h_max1, preciptacao, intensidade, df_longo, media, desvio_padrao
df = None
response_data = {}


@idf_bp.route('/idf', methods=['POST', 'GET'])
def tensao_elastica_vao():
    global h_max1, preciptacao, intensidade, df_longo, media, desvio_padrao, df


    if request.method == 'POST':
        file = request.files.get('arq1')
        if file:
            df = pd.read_excel(file)
            print(f"[POST /idf] Arquivo recebido: {df.shape}")

            h_max1, preciptacao, intensidade, df_longo, media, desvio_padrao = calculo_precipitacoes(df)
            a, b, c, d = problema_inverso_idf(df_longo)
            return jsonify({
                'imagem_url': imagem_url,
                'sigma_t_vazio1': sigma_t_vazio,
                'sigma_b_vazio1': sigma_b_vazio,
                'sigma_t_serv1': sigma_t_serv,
                'sigma_b_serv1': sigma_b_serv
            })

    elif request.method == 'GET':
        response_data = {
            'imagem_url': imagem_url,
            'sigma_t_vazio1': sigma_t_vazio,
            'sigma_b_vazio1': sigma_b_vazio,
            'sigma_t_serv1': sigma_t_serv,
            'sigma_b_serv1': sigma_b_serv
        }
        return jsonify(response_data)
