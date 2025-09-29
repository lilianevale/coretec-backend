from flask import Blueprint, request, jsonify
from app.utils.calculos import perda_relax_armadura
import pandas as pd

marteloimpacto_bp = Blueprint('martelo', __name__)

# Variáveis globais como no seu código original
fig, kk, y=None,0,0 
response_data = {}


@marteloimpacto_bp.route('/martelo', methods=['POST', 'GET'])
def handle_martelo():
    global fig, kk, y, response_data
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

        return jsonify({
            'fig': fig,
            'kk': f'{kk:.2f} N/m',
            'p_it11': f'{p_it1:.3e} kN',
            'psi1': f'{psi:.3e} %',
            'psi_10001': f'{psi_1000:.3e} %'


        })

    elif request.method == 'GET':
        response_data = {
            'deltaperc1': f'{deltaperc:.2f} %',
            'sigma_pit11': f'{sigma_pit1/1000:.3e} MPa',
            'p_it11': f'{p_it1:.3e} kN',
            'psi1': f'{psi:.3e} %',
            'psi_10001': f'{psi_1000:.3e} %',

        }

    return jsonify(response_data)
