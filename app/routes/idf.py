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

<<<<<<< HEAD
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
                "media": float(media),
                "desvio_padrao": float(desvio_padrao),
                "imagem_url": imagem_url
            })
=======
        # Salvar imagem
        nome_arquivo = f"idf_{uuid.uuid4().hex[:8]}.png"
        pasta_destino = os.path.join("app", "static", "imagens")
        os.makedirs(pasta_destino, exist_ok=True)
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        fig.savefig(caminho_completo, dpi=300, bbox_inches='tight')
        plt.close(fig)
        imagem_url = f"/static/imagens/{nome_arquivo}"

        data=download_excel(df_longo),
                    file_name=f"PLANILHA_IDF_{nome_arquivo}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return jsonify({
            "h_max1aux": h_max1aux.to_dict(orient='records'),
            "preciptacao": preciptacao.to_dict(orient='records'),
            "intensidade": intensidade.to_dict(orient='records'),
            "df_longo": df_longo.to_dict(orient='records'),
            "media": f': {media:.2f} mm',
            "desvio_padrao": f': {desvio_padrao:.2f} mm',
            "imagem_url": imagem_url,
            "data": data
        })
>>>>>>> 061a6ddbd21500f2f520bdcdec03d9a7fd8183eb

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:
        return jsonify({"message": "Envie um arquivo via POST para calcular o IDF."})
