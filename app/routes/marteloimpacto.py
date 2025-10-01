from flask import Blueprint, request, jsonify
from app.utils.calculos_martelo_impacto import analise_inversa_martelo_impacto, martelo_impacto_gif
import os
import uuid
import matplotlib
matplotlib.use("Agg")  # Backend para servidor
import matplotlib.pyplot as plt

marteloimpacto_bp = Blueprint('martelo', __name__)

# Variáveis globais
gif_buffer, fig, kk, y = None, None, 0, 0
response_data = {}


@marteloimpacto_bp.route('/martelo', methods=['POST', 'GET'])
def handle_martelo():
    global fig, kk, y, response_data, gif_buffer
    global m, c, f, k, dano

    if request.method == 'POST':
        data = request.get_json()

        # Entrada dos dados
        m = float(data.get('massa1', 1))
        c = float(data.get('amortecimento1', 0))
        f = float(data.get('forca1', 1))
        k = float(data.get('valor', 1000))
        dano = float(data.get('dano1', 0))

        # Cálculo principal
        fig, kk, y = analise_inversa_martelo_impacto(m, c, f, k, dano)

        # Pasta destino
        pasta_destino = os.path.join("app", "static", "imagens")
        os.makedirs(pasta_destino, exist_ok=True)

        # Salvar figura
        nome_arquivo_fig = f"vao_{uuid.uuid4().hex[:8]}.png"
        caminho_fig = os.path.join(pasta_destino, nome_arquivo_fig)
        fig.savefig(caminho_fig, dpi=300, bbox_inches='tight')
        plt.close(fig)
        imagem_url_fig = f"/static/imagens/{nome_arquivo_fig}"

        # Gerar GIF
        gif_frames = martelo_impacto_gif(y)
        nome_arquivo_gif = f"vao_{uuid.uuid4().hex[:8]}.gif"
        caminho_gif = os.path.join(pasta_destino, nome_arquivo_gif)
        gif_frames[0].save(
            caminho_gif,
            save_all=True,
            append_images=gif_frames[1:],
            loop=0,
            duration=100
        )
        imagem_url_gif = f"/static/imagens/{nome_arquivo_gif}"

        return jsonify({
            'fig': imagem_url_fig,
            'gif': imagem_url_gif,
            'kk': f'{kk:.2f} N/m',
        })

    elif request.method == 'GET':
        response_data = {
            'fig': None,
            'gif': None,
            'kk': f'{kk:.2f} N/m',
        }

    return jsonify(response_data)
