from flask import Blueprint, request, jsonify
from app.utils.calculos import perda_relax_armadura
import pandas as pd
from calculos import  save_figure_temp, save_gif_temp, analise_inversa_martelo_impacto, martelo_impacto_gif


shaker_bp = Blueprint('shaker', __name__)

# Variáveis globais como no seu código original
 fig, kk, y= None,0,0 
m, b, h, l, omega, modulo_e, f_0, dano=0,0,0,0,0,0,0,0
response_data = {}


@marteloimpacto_bp.route('/shaker', methods=['POST', 'GET'])
def handle_shaker():
    global fig, kk, y, response_data, 
    global m, b, h, l, omega, modulo_e, f_0, dano=0,0,0,0,0,0,0,0


    if request.method == 'POST':
        data = request.get_json()

        # Entrada dos dados e conversão de unidades
        m = float(data.get('valor1'))
        b = float(data.get('base1'))
        h = float(data.get('altura1'))
        l = float(data.get('compviga1'))      
        omega = float(data.get('valor2'))
        f_0= float(data.get('valor3'))
        modulo_e= float(data.get('valor4'))
        dano = float(data.get('dano1'))
        
        # Chamada da função de cálculo
            fig, kk, y = analise_inversa_shaker(m, b, h, l, omega, modulo_e, f_0, dano) 
            pyplot(fig)

         # Salvar fig na pasta do projeto
        nome_arquivo = f"vao_{uuid.uuid4().hex[:8]}.png"
        pasta_destino = os.path.join("app", "static", "imagens")
        os.makedirs(pasta_destino, exist_ok=True)
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        fig.savefig(caminho_completo, dpi=300, bbox_inches='tight')
        plt.close(fig)
        imagem_url1 = f"/static/imagens/{nome_arquivo}"

        return jsonify({
            'fig': imagem_url1,
            'kk': f'{kk:.2f} N/m',
            
        })

    elif request.method == 'GET':
        response_data = {
           'fig': fig,
            'kk': f'{kk:.2f} N/m',
            

        }

    return jsonify(response_data)
