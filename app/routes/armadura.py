from flask import Blueprint, request, jsonify
from app.utils.calculos import perda_relax_armadura
import pandas as pd

armadura_bp = Blueprint('armadura', __name__)

# Variáveis globais como no seu código original
deltaperc = p_it1 = sigma_pit1 = psi = psi_1000 = 0
response_data = {}


@armadura_bp.route('/armadura', methods=['POST', 'GET'])
def handle_armadura():
    global deltaperc, p_it1, sigma_pit1, psi, psi_1000, response_data

    if request.method == 'POST':
        data = request.get_json()

        # Entrada dos dados e conversão de unidades
        p_it0 = float(data.get('protensao1'))
        sigma_pit0 = float(data.get('ti1'))
        t_0 = float(data.get('sdias1'))
        t_1 = float(data.get('tempof1'))
        temp = float(data.get('tempproj1'))
        f_pk = float(data.get('tensao1'))
        # nome está estranho, mas mantive como no seu código
        a_slcp = float(data.get('fletor1'))
        tipo_armadura = data.get('tipoarm1')
        tipo_aco = data.get('tipaco1')

        # Chamada da função de cálculo
        deltaperc, p_it1, sigma_pit1, psi, psi_1000 = perda_relax_armadura(
            p_it0, sigma_pit0 * 1E3, t_0, t_1, temp, f_pk * 1E3,
            a_slcp * 1E-4, tipo_armadura, tipo_aco
        )

        print(
            f"[POST /armadura] deltaperc: {deltaperc}, p_it1: {p_it1}, sigma_pit1: {sigma_pit1}, psi: {psi}, psi_1000: {psi_1000}")

        return jsonify({
            response_data = { 
            'deltaperc1' : f'{deltaperc:.2f} %',
            'sigma_pit11': f'{sigma_pit1/1000:.3e} MPa',
            'p_it11' : f'{p_it1:.3e} kN',
            'psi1':f'{psi:.3e} %',
            'psi_10001':f'{psi_1000:.3e} %'

        }
        })

    elif request.method == 'GET':
            response_data = { 
            'deltaperc1' : f'{deltaperc:.2f} %',
            'sigma_pit11': f'{sigma_pit1/1000:.3e} MPa',
            'p_it11' : f'{p_it1:.3e} kN',
            'psi1':f'{psi:.3e} %',
            'psi_10001':f'{psi_1000:.3e} %',

        }

        return jsonify(response_data)
