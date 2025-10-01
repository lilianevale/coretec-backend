from flask import Blueprint, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import os
import uuid
import numpy as np
from app.utils.calculos_spi import indice_spi

spi_bp = Blueprint('spi', __name__)

# Variáveis globais
imagem_url = None
spi_df, estatisticas_df = None, None

def df_para_json(df):
    """Converte DataFrame em dict serializável para JSON."""
    df_serializavel = df.copy()
    for col in df_serializavel.columns:
        if np.issubdtype(df_serializavel[col].dtype, np.number):
            df_serializavel[col] = df_serializavel[col].apply(lambda x: None if pd.isna(x) else float(x))
        elif np.issubdtype(df_serializavel[col].dtype, np.datetime64):
            df_serializavel[col] = df_serializavel[col].dt.strftime('%Y-%m-%d')
        elif isinstance(df_serializavel[col].dtype, pd.PeriodDtype):
            df_serializavel[col] = df_serializavel[col].astype(str)
        else:
            df_serializavel[col] = df_serializavel[col].astype(str)
    return df_serializavel.to_dict(orient='records')


@spi_bp.route('/spi', methods=['POST', 'GET'])
def spi_endpoint():
    global spi_df, estatisticas_df, imagem_url

    if request.method == 'POST':
        file = request.files.get('arq1')
        if not file:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400

        try:
            # Detectar tipo do arquivo
            filename = file.filename.lower()
            if filename.endswith('.csv'):
                df = pd.read_csv(file, sep=';')
            elif filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                return jsonify({"error": "Formato de arquivo não suportado"}), 400

            # Padronizar nomes de colunas
            df.columns = df.columns.str.replace(',', '').str.replace('  ', ' ').str.strip()
            df.rename(columns={
                'PRECIPITACAO TOTAL DIARIO (AUT)(mm)': 'PRECIPITACAO TOTAL DIARIA (mm)',
                'Data Medicao': 'Data Medicao'
            }, inplace=True)

            # Calcular SPI
            spi_df, estatisticas_df = indice_spi(df)

            # Criar gráfico
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(spi_df['AnoMes'].astype(str), spi_df['SPI'].fillna(0), color='b')

            # Áreas de classificação
            ax.fill_between(spi_df['AnoMes'].astype(str), -3, -2, color='red', alpha=0.3, label='Extrema Seca')
            ax.fill_between(spi_df['AnoMes'].astype(str), -2, -1.5, color='orange', alpha=0.3, label='Muita Seca')
            ax.fill_between(spi_df['AnoMes'].astype(str), -1.5, -1.0, color='yellow', alpha=0.3, label='Moderada Seca')
            ax.fill_between(spi_df['AnoMes'].astype(str), -1.0, 1.0, color='green', alpha=0.3, label='Normal')
            ax.fill_between(spi_df['AnoMes'].astype(str), 1.0, 1.5, color='cyan', alpha=0.3, label='Moderada Umidade')
            ax.fill_between(spi_df['AnoMes'].astype(str), 1.5, 2.0, color='blue', alpha=0.3, label='Muita Umidade')
            ax.fill_between(spi_df['AnoMes'].astype(str), 2.0, 3, color='purple', alpha=0.3, label='Extrema Umidade')

            ax.set_xlabel('Mês')
            ax.set_ylabel('SPI')
            ax.set_title('SPI Mensal')
            ax.set_xticks(range(len(spi_df)))
            ax.set_xticklabels(spi_df['AnoMes'].astype(str), rotation=90, fontsize=8)
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
            plt.tight_layout()

            # Salvar imagem
            nome_arquivo = f"spi_{uuid.uuid4().hex[:8]}.png"
            pasta_destino = os.path.join("app", "static", "imagens")
            os.makedirs(pasta_destino, exist_ok=True)
            caminho_completo = os.path.join(pasta_destino, nome_arquivo)
            fig.savefig(caminho_completo, dpi=300, bbox_inches='tight')
            plt.close(fig)

            imagem_url = f"/static/imagens/{nome_arquivo}"

            return jsonify({
                'spi_df': df_para_json(spi_df),
                'estatisticas_df': df_para_json(estatisticas_df),
                'imagem_url': imagem_url
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # GET: retorna último resultado se existir
    return jsonify({
        'spi_df': df_para_json(spi_df) if spi_df is not None else [],
        'estatisticas_df': df_para_json(estatisticas_df) if estatisticas_df is not None else [],
        'imagem_url': imagem_url
    })
