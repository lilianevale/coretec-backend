from flask import Blueprint, request, jsonify
from app.utils.calculos import prop_geometrica_estadio_i
import pandas as pd

estadio1_bp = Blueprint('estadio1', __name__)

# Variáveis globais
h_f, b_f, b_w, a_st, a_sc, alpha_mod, d, dl = 0, 0, 0, 0, 0, 0, 0, 0
a_ci, x_i, i_i, w_inf, w_sup = 0, 0, 0, 0, 0
response_data = {}

@estadio1_bp.route('/estadio1', methods=['POST', 'GET'])
def handle_user_data():
    global response_data
    global h, h_f, b_f, b_w, a_st, alpha_mod, d
    global a_ci, x_i, i_i, w_inf, w_sup

    if request.method == 'POST':
        data = request.get_json() or {}
        print("Dados recebidos:", data)  # debug

        # campos obrigatórios
        required_fields = ['htotal1','hmesa1','lmesa1','alma1','tracao1','modulos1']
        missing = [f for f in required_fields if f not in data]

        # pelo menos um desses deve existir
        if not (data.get('fletor1') or data.get('htracao1')):
            missing.append('fletor1/htracao1')

        if missing:
            return jsonify({"error": f"Campos obrigatórios faltando: {missing}"}), 400

        try:
            h         = float(data.get('htotal1'))
            h_f       = float(data.get('hmesa1'))
            b_f       = float(data.get('lmesa1'))
            b_w       = float(data.get('alma1'))
            a_st      = float(data.get('tracao1'))
            alpha_mod = float(data.get('modulos1'))
            # aceita tanto fletor1 quanto htracao1
            d         = float(data.get('fletor1') or data.get('htracao1'))
        except ValueError as e:
            return jsonify({"error": f"Valor inválido: {str(e)}"}), 400

        # chama a função de cálculo
        a_ci, x_i, i_i, w_inf, w_sup = prop_geometrica_estadio_i(
            h, h_f, b_f, b_w, a_st/1e4, alpha_mod, d
        )

        response_data = { 
            'a_ci' : f"{a_ci*1e4:.3e}",
            'x_i'  : f"{x_i*1e2:.3e}",
            'i_i'  : f"{i_i:.3e}",
            'w_inf': f"{w_inf*1e6:.3e}",
            'w_sup': f"{w_sup*1e6:.3e}",
        }

    elif request.method == 'GET':
        response_data = { 
            'a_ci' : f"{a_ci*1e4:.3e}",
            'x_i'  : f"{x_i*1e2:.3e}",
            'i_i'  : f"{i_i:.3e}",
            'w_inf': f"{w_inf*1e6:.3e}",
            'w_sup': f"{w_sup*1e6:.3e}",
        }
        print("response_data", response_data)

    return jsonify(response_data)
