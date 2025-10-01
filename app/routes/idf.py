from flask import Blueprint, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import os
import uuid
from app.utils.calculos_idf import calculo_precipitacoes

idf_bp = Blueprint('idf', __name__)

@idf_bp.route('/idf', methods=['POST', 'GET'])
def idf_endpoint():
    if request.method == 'POST':
        file = request.files.get('arq1')
        if not file:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400

        try:
            # Ler Excel
            df = pd.read_excel(file)

            # Calcular precipitações e intensidades
            h_max1aux, preciptacao, intensidade, df_longo, media, desvio_padrao = calculo_precipitacoes(df)

            # Criar gráfico IDF
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

            # (Opcional) Salvar df_longo em Excel
            nome_excel = f"idf_{uuid.uuid4().hex[:8]}.xlsx"
            caminho_excel = os.path.join(pasta_destino, nome_excel)
            df_longo.to_excel(caminho_excel, index=False)

            excel_url = f"/static/imagens/{nome_excel}"

            return jsonify({
                "h_max1aux": h_max1aux.to_dict(orient='records'),
                "preciptacao": preciptacao.to_dict(orient='records'),
                "intensidade": intensidade.to_dict(orient='records'),
                "df_longo": df_longo.to_dict(orient='records'),
                "media": round(float(media), 2),
                "desvio_padrao": round(float(desvio_padrao), 2),
                "imagem_url": imagem_url,
                "excel_url": excel_url
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:
        return jsonify({"message": "Envie um arquivo via POST para calcular o IDF."})
