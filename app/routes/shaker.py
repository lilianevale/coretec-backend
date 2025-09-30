from flask import Blueprint, request, jsonify
from app.utils.calculos import analise_inversa_shaker  # importe a função correta do shaker
import matplotlib.pyplot as plt
import os
import uuid

shaker_bp = Blueprint('shaker', __name__)

# Variáveis globais
fig, kk, y = None, 0, 0
m, b, h, l, omega, modulo_e, f_0, dano = 0, 0, 0, 0, 0, 0, 0, 0

@shaker_bp.route('/shaker', methods=['POST', 'GET'])
def handle_shaker():
    global fig, kk, y
    global m, b, h, l, omega, modulo_e, f_0, dano

    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Nenhum dado enviado"}), 400

        # Entrada dos dados e conversão de unidades
        m = float(data.get('valor1', 0))
        b = float(data.get('base1', 0))
        h = float(data.get('altura1', 0))
        l = float(data.get('compviga1', 0))
        omega = float(data.get('valor2', 0))
        f_0 = float(data.get('valor3', 0))
        modulo_e = float(data.get('valor4', 0))
        dano = float(data.get('dano1', 0))

        # Chamada da função de cálculo
        fig, kk, y = analise_inversa_shaker(m, b, h, l, omega, modulo_e, f_0, dano)

        # Salvar figura
        nome_arquivo = f"shaker_{uuid.uuid4().hex[:8]}.png"
        pasta_destino = os.path.join("app", "static", "imagens")
        os.makedirs(pasta_destino, exist_ok=True)
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        fig.savefig(caminho_completo, dpi=300, bbox_inches='tight')
        plt.close(fig)
        imagem_url = f"/static/imagens/{nome_arquivo}"

        return jsonify({
            'fig': imagem_url,
            'kk': f'{kk:.2f} N/m',
        })

    elif request.method == 'GET':
        return jsonify({
            'fig': None if fig is None else f"/static/imagens/{uuid.uuid4().hex[:8]}.png",
            'kk': f'{kk:.2f} N/m' if kk else None
        })
