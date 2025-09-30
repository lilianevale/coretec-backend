from flask import Blueprint, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import os
import uuid
from app.utils.calculos import calculo_precipitacoes, indice_spi  # importe outras funções que você usar

idf_bp = Blueprint('idf', __name__)

# Variáveis globais
imagem_url = None
h_max1aux, preciptacao, intensidade, df_longo, media, desvio_padrao = (None,) * 6

@idf_bp.route('/idf', methods=['POST', 'GET'])
def idf_endpoint():
    global h_max1aux, preciptacao, intensidade, df_longo, media, desvio_padrao, imagem_url

    if request.method == 'POST':
        file = request.files.get('arq1')
        if not file:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400

        # Ler Excel
        df = pd.read_excel(file, skiprows=10)

        # Calcular precipitações e intensidades
        h_max1aux, preciptacao, intensidade, df_longo, media, desvio_padrao = calculo_precipitacoes(df)

        # Criar gráfico de exemplo (precipitação máxima por tempo de retorno)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(h_max1aux['tempo de retorno (anos)'], h_max1aux['Pmax diária (mm)'], color='blue')
        ax.set_xlabel('Tempo de Retorno (anos)')
        ax.set_ylabel('Precipitação Máxima Diária (mm)')
        ax.set_title('Precipitação Máxima Diária por Tempo de Retorno')
        plt.tight_layout()

        # Salvar imagem
        nome_arquivo = f"idf_{uuid.uuid4().hex[:8]}.png"
        pasta_destino = os.path.join("app", "static", "imagens")
        os.makedirs(pasta_destino, exist_ok=True)
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        fig.savefig(caminho_completo, dpi=300, bbox_inches='tight')
        plt.close(fig)

        imagem_url = f"/static/imagens/{nome_arquivo}"

        return jsonify({
            "h_max1aux": h_max1aux.to_dict(orient='records'),
            "preciptacao": preciptacao.to_dict(orient='records'),
            "intensidade": intensidade.to_dict(orient='records'),
            "df_longo": df_longo.to_dict(orient='records'),
            "media": media,
            "desvio_padrao": desvio_padrao,
            "imagem_url": imagem_url
        })

    elif request.method == 'GET':
        return jsonify({
            "h_max1aux": h_max1aux.to_dict(orient='records') if h_max1aux is not None else None,
            "preciptacao": preciptacao.to_dict(orient='records') if preciptacao is not None else None,
            "intensidade": intensidade.to_dict(orient='records') if intensidade is not None else None,
            "df_longo": df_longo.to_dict(orient='records') if df_longo is not None else None,
            "media": media,
            "desvio_padrao": desvio_padrao,
            "imagem_url": imagem_url
        })
