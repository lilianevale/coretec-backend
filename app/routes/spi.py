from flask import Blueprint, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import os
import uuid
from app.utils.calculos import indice_spi

spi_bp = Blueprint('spi', __name__)

# Variáveis globais
imagem_url = None
spi_df, estatisticas_df = None, None
df = None


@spi_bp.route('/spi', methods=['POST', 'GET'])
def idf():
    global spi_df, estatisticas_df, df, imagem_url

    if request.method == 'POST':
        file = request.files.get('arq1')
        if file:
            df = pd.read_excel(file, skiprows=10)
            print(f"[POST /spi] Arquivo recebido: {df.shape}")

            nome_arquivo_base = file.filename.replace('.csv', '')

            spi_df, estatisticas_df = indice_spi(df)

            # Criar gráfico
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(spi_df['AnoMes'].astype(str), spi_df['SPI'], color='b')

            # Sombrear áreas de classificação
            ax.fill_between(spi_df['AnoMes'].astype(
                str), -3, -2, color='red', alpha=0.3, label='Extrema Seca (SPI < -2.0)')
            ax.fill_between(spi_df['AnoMes'].astype(
                str), -2, -1.5, color='orange', alpha=0.3, label='Muita Seca (-2.0 ≤ SPI < -1.5)')
            ax.fill_between(spi_df['AnoMes'].astype(
                str), -1.5, -1.0, color='yellow', alpha=0.3, label='Moderada Seca (-1.5 ≤ SPI ≤ -1.0)')
            ax.fill_between(spi_df['AnoMes'].astype(
                str), -1.0, 1.0, color='green', alpha=0.3, label='Condições Normais (-1.0 < SPI < 1.0)')
            ax.fill_between(spi_df['AnoMes'].astype(
                str), 1.0, 1.5, color='cyan', alpha=0.3, label='Moderada Umidade (1.0 ≤ SPI < 1.5)')
            ax.fill_between(spi_df['AnoMes'].astype(
                str), 1.5, 2.0, color='blue', alpha=0.3, label='Muita Umidade (1.5 ≤ SPI < 2.0)')
            ax.fill_between(spi_df['AnoMes'].astype(
                str), 2.0, 3, color='purple', alpha=0.3, label='Extrema Umidade (SPI ≥ 2.0)')

            # Configurações do gráfico
            ax.set_xlabel('Mês')
            ax.set_ylabel('SPI')
            ax.set_title('SPI Mensal (Índice de Precipitação Padronizado)')

            # Filtrar os meses de janeiro para o eixo X
            ticks_to_show = spi_df[spi_df['AnoMes'].dt.month == 1]['AnoMes'].astype(
                str)
            ax.set_xticks(ticks_to_show.index)
            ax.set_xticklabels(ticks_to_show, rotation=90, fontsize=8)

            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
            plt.tight_layout()

            # Salvar imagem
            nome_arquivo = f"vao_{uuid.uuid4().hex[:8]}.png"
            pasta_destino = os.path.join("app", "static", "imagens")
            os.makedirs(pasta_destino, exist_ok=True)
            caminho_completo = os.path.join(pasta_destino, nome_arquivo)
            fig.savefig(caminho_completo, dpi=300, bbox_inches='tight')
            plt.close(fig)

            imagem_url = f"/static/imagens/{nome_arquivo}"

            return jsonify({
                'spi_df': spi_df.to_dict(orient='records'),
                'estatisticas_df': estatisticas_df.to_dict(orient='records'),
                'imagem_url': imagem_url
            })

    elif request.method == 'GET':
        return jsonify({
            'spi_df': spi_df.to_dict(orient='records') if spi_df is not None else None,
            'estatisticas_df': estatisticas_df.to_dict(orient='records') if estatisticas_df is not None else None,
            'imagem_url': imagem_url
        })
