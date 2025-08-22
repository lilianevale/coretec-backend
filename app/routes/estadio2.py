from flask import Blueprint, request, jsonify
from app.utils.calculos import prop_geometrica_estadio_ii
import pandas as pd

estadio2_bp = Blueprint('estadio2', __name__)

# Variáveis globais
h_f, b_f, b_w, a_st, a_sc, alpha_mod, d, dl = 0,0,0,0,0,0,0,0
x_ii, i_ii, a_1, a_2, a_3, passa_onde, x_ii_teste = 0,0,0,0,0,0,0
response_data = {}

@estadio2_bp.route('/estadio2', methods=['POST', 'GET'])
def handle_user_data():
    global response_data
    global h_f, b_f, b_w, a_st, a_sc, alpha_mod, d, dl
    global x_ii, i_ii, a_1, a_2, a_3, passa_onde, x_ii_teste 

    if request.method == 'POST':
        data = request.get_json() or {}
        print("Dados recebidos:", data)

        required_fields = ['lmesa1','alma1','tracao1','comprimida1','modulos1','hcompr1']
        missing = [f for f in required_fields if f not in data]

        # aceita fletor1 ou htracao1
        if not (data.get('fletor1') or data.get('htracao1')):
            missing.append('fletor1/htracao1')

        # hmesa1 pode ser opcional dependendo da sua fórmula
        if missing:
            return jsonify({"error": f"Campos obrigatórios faltando: {missing}"}), 400

        try:
            h_f       = float(data.get('hmesa1') or 0)   # se não vier, assume 0
            b_f       = float(data.get('lmesa1'))
            b_w       = float(data.get('alma1'))
            a_st      = float(data.get('tracao1'))
            a_sc      = float(data.get('comprimida1'))
            alpha_mod = float(data.get('modulos1'))
            d         = float(data.get('fletor1') or data.get('htracao1'))
            dl        = float(data.get('hcompr1'))
        except ValueError as e:
            return jsonify({"error": f"Valor inválido: {str(e)}"}), 400

        # chamada para cálculo
        x_ii, i_ii, a_1, a_2, a_3, passa_onde, x_ii_teste = prop_geometrica_estadio_ii(
            h_f, b_f, b_w, a_st/1e4, a_sc/1e4, alpha_mod, d, dl
        )

        response_data = { 
            'x_ii'      : f'{x_ii*1e2:.3e} cm',
            'i_ii'      : f'{i_ii:.3e} m\u2074',
            'a_1'       : f'{a_1*1e2:.3e} cm',
            'a_2'       : f'{a_2*1e4:.3e} cm²',
            'a_3'       : f'{a_3*1e6:.3e} cm³',
            'passa_onde': passa_onde,
            'x_ii_teste': f'{x_ii_teste*1e2:.3e} cm',
        }

    elif request.method == 'GET':
        response_data = { 
            'x_ii'      : f'{x_ii*1e2:.3e} cm',
            'i_ii'      : f'{i_ii:.3e} m\u2074',
            'a_1'       : f'{a_1*1e2:.3e} cm',
            'a_2'       : f'{a_2*1e4:.3e} cm²',
            'a_3'       : f'{a_3*1e6:.3e} cm³',
            'passa_onde': passa_onde,
            'x_ii_teste': f'{x_ii_teste*1e2:.3e} cm',
        }
        print("response_data", response_data)

    return jsonify(response_data)
