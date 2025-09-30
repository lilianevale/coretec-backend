from flask import Blueprint, request, jsonify
from app.utils.calculos import perda_relax_armadura
import pandas as pd
from app.utils.calculos import analise_inversa_martelo_impacto, martelo_impacto_gif


marteloimpacto_bp = Blueprint('martelo', __name__)

# Variáveis globais como no seu código original
gif_buffer, fig, kk, y = None, None, 0, 0
response_data = {}


@marteloimpacto_bp.route('/martelo', methods=['POST', 'GET'])
def handle_martelo():
    global fig, kk, y, response_data, gif_buffer
    global m, c, f, k, dano

    if request.method == 'POST':
        data = request.get_json()

        # Entrada dos dados e conversão de unidades
        m = float(data.get('massa1'))
        c = float(data.get('amortecimento1'))
        f = float(data.get('forca1'))
        k = float(data.get('valor'))
        dano = float(data.get('dano1'))

        # Chamada da função de cálculo
        fig, kk, y = analise_inversa_martelo_impacto(m, c, f, k, dano)
        pyplot(fig)

        # Salvar fig na pasta do projeto
        nome_arquivo = f"vao_{uuid.uuid4().hex[:8]}.png"
        pasta_destino = os.path.join("app", "static", "imagens")
        os.makedirs(pasta_destino, exist_ok=True)
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        fig.savefig(caminho_completo, dpi=300, bbox_inches='tight')
        plt.close(fig)
        imagem_url2 = f"/static/imagens/{nome_arquivo}"

        gif_buffer = martelo_impacto_gif(y)

        # Salvar gif_buffer na pasta do projeto
        nome_arquivo = f"vao_{uuid.uuid4().hex[:8]}.png"
        pasta_destino = os.path.join("app", "static", "imagens")
        os.makedirs(pasta_destino, exist_ok=True)
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        gif_buffer.savefig(caminho_completo, dpi=300, bbox_inches='tight')
        plt.close(gif_buffer)
        imagem_url1 = f"/static/imagens/{nome_arquivo}"

        return jsonify({
            'fig': imagem_url1,
            'gif_buffer': imagem_url2,
            'kk': f'{kk:.2f} N/m',

        })

    elif request.method == 'GET':
        response_data = {
            'fig': fig,
            'gif_buffer': gif_buffer,
            'kk': f'{kk:.2f} N/m',


        }

    return jsonify(response_data)
