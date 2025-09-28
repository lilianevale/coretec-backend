from flask import Blueprint, request, jsonify
import pandas as pd
from app.utils.calculos import calculo_precipitacoes, problema_inverso_idf, indice_spi, tutorial_idf, teoria_idf, pbl_idf, tutorial_spi, teoria_spi, pbl_spi

spi_bp = Blueprint('spi', __name__)

# Variáveis globais
spi_df, estatisticas_df=0,0
df = None
response_data = {}


@spi_bp.route('/spi', methods=['POST', 'GET'])
def idf():
    global  spi_df, estatisticas_df, df


    if request.method == 'POST':
        file = request.files.get('arq1')
        if file:
            df = pd.read_excel(file, sep=';', skiprows=10)
            print(f"[POST /spi] Arquivo recebido: {df.shape}")
            nome_arquivo = ile.name
            nome_arquivo = file.name.replace('.csv', '')
            spi_df, estatisticas_df = indice_spi(df) 

            
                # Agora vamos adicionar o gráfico
                import matplotlib.pyplot as plt
                plt.figure(figsize=(10, 6))
                plt.bar(spi_df['AnoMes'].astype(str), spi_df['SPI'], color='b')

                # Sombrear áreas de classificação
                plt.fill_between(spi_df['AnoMes'].astype(str), -3, -2, color='red', alpha=0.3, label='Extrema Seca (SPI < -2.0)')
                plt.fill_between(spi_df['AnoMes'].astype(str), -2, -1.5, color='orange', alpha=0.3, label='Muita Seca (-2.0 ≤ SPI < -1.5)')
                plt.fill_between(spi_df['AnoMes'].astype(str), -1.5, -1.0, color='yellow', alpha=0.3, label='Moderada Seca (-1.5 ≤ SPI ≤ -1.0)')
                plt.fill_between(spi_df['AnoMes'].astype(str), -1.0, 1.0, color='green', alpha=0.3, label='Condições Normais (-1.0 < SPI < 1.0)')
                plt.fill_between(spi_df['AnoMes'].astype(str), 1.0, 1.5, color='cyan', alpha=0.3, label='Moderada Umidade (1.0 ≤ SPI < 1.5)')
                plt.fill_between(spi_df['AnoMes'].astype(str), 1.5, 2.0, color='blue', alpha=0.3, label='Muita Umidade (1.5 ≤ SPI < 2.0)')
                plt.fill_between(spi_df['AnoMes'].astype(str), 2.0, 3, color='purple', alpha=0.3, label='Extrema Umidade (SPI ≥ 2.0)')

                # Configurações do gráfico
                plt.xlabel('Mês')
                plt.ylabel('SPI')
                plt.title('SPI Mensal (Índice de Precipitação Padronizado)')
                
                # Filtrar os meses de janeiro de cada ano para o eixo X
                ticks_to_show = spi_df[spi_df['AnoMes'].dt.month == 1]['AnoMes'].astype(str)
                plt.xticks(ticks=ticks_to_show.index, labels=ticks_to_show, rotation=90, fontsize=8)

                plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)  # Ajustar a posição da legenda
                plt.tight_layout()

                pyplot(plt)
            # Salvar imagem na pasta do projeto
        nome_arquivo = f"vao_{uuid.uuid4().hex[:8]}.png"
        pasta_destino = os.path.join("app", "static", "imagens")
        os.makedirs(pasta_destino, exist_ok=True)
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        fig.savefig(caminho_completo, dpi=300, bbox_inches='tight')
        plt.close(fig)

        imagem_url = f"/static/imagens/{nome_arquivo}"
            return jsonify({
                'spi_df': spi_df,
                'estatisticas_df': estatisticas_df,
                'plt': plt
            })

    elif request.method == 'GET':
        response_data = {
            'spi_df': spi_df,
                'estatisticas_df': estatisticas_df,
                'plt': plt
        }
        return jsonify(response_data)
