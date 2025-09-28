from flask import Blueprint, request, jsonify
from app.utils.calculos import perda_deslizamento_ancoragem
import pandas as pd

circulo_mohr_2d_bp = Blueprint('mecSolidos', __name__)

deltaperc = p_it1 = sigma_pit1 = 0
fig, sigma_med, raio, sigma_maxx, sigma_minn, theta_p_graus, theta_c_graus=0,0,0,0,0,0
response_data = {}


@circulo_mohr_2d_bp.route('/mecSolidos', methods=['POST', 'GET'])
def handle_circulo_mohr_2d_bp():
    global deltaperc, p_it1, sigma_pit1, response_data

    if request.method == 'POST':
        data = request.get_json()

        p_it0 = float(data.get('ci_prot1'))
        sigma_pit0 = float(data.get('ti_prot1'))
        a_slcp = float(data.get('arma_prot1'))
        l_0 = float(data.get('comp_armadura1'))
        Delta_anc = float(data.get('deslizamento1'))
        e_scp = float(data.get('melasticidade1'))

        deltaperc, p_it1, sigma_pit1 = perda_deslizamento_ancoragem(
            p_it0, sigma_pit0 * 1E3, a_slcp * 1E-4, l_0, Delta_anc * 1E-3, e_scp * 1E3
        )

        print(
            f"[POST /ancoragem] deltaperc: {deltaperc}, p_it1: {p_it1}, sigma_pit1: {sigma_pit1}")

        return jsonify({
            'deltaperc':  f'{deltaperc:.2f} %',
            'p_it1': f'{p_it1:.3e} kN',
            'sigma_pit1':  f'{sigma_pit1/1000:.3e} MPa'
        })

    elif request.method == 'GET':
        response_data = {
           'deltaperc':  f'{deltaperc:.2f} %',
            'p_it1': f'{p_it1:.3e} kN',
            'sigma_pit1':  f'{sigma_pit1/1000:.3e} MPa'
        }

        return jsonify(response_data)
