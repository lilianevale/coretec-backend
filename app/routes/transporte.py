from flask import Blueprint, request, jsonify
from app.utils.calculos import analise_inversa_shaker  # importe a função correta do shaker
import matplotlib.pyplot as plt
import os
import uuid

transporte_bp = Blueprint('transporte', __name__)

# Variáveis globais

@transporte_bp.route('/transporte', methods=['POST', 'GET'])
def handle_transporte():
   

    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Nenhum dado enviado"}), 400

        # Entrada dos dados e conversão de unidades
        rota = float(data.get('rota1', 0))
       
       gtfs_zip_path = "./arc_upload/GTFSBHTRANSCON.zip"
        main(gtfs_zip_path, rota)

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
