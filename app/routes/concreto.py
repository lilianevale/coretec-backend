from flask import Blueprint, request, jsonify
from app.utils.calculos import perda_retracao_concreto
import pandas as pd

concreto_bp = Blueprint('concreto', __name__)

# Variáveis globais (como no original)
deltaperc = p_it1 = sigma_pit1 = eps_cs = 0
response_data = {}


@concreto_bp.route('/concreto', methods=['POST', 'GET'])
def handle_concreto():
    global deltaperc, p_it1, sigma_pit1, eps_cs, response_data

    if request.method == 'POST':
        data = request.get_json()

        p_it0 = float(data.get('cargain1'))
        sigma_pit0 = float(data.get('tensinit1'))
        umidade = float(data.get('umidade1'))
        a_slcp = float(data.get('totalarmadura1'))
        abatimento = float(data.get('umidade1'))
        a_c = float(data.get('slump1'))
        mu_ar = float(data.get('areabruta1'))
        t_0 = float(data.get('perimex1'))
        t_1 = float(data.get('tempin1'))
        temp = float(data.get('temp1'))
        e_scp = float(data.get('young1'))

        eps_cs, deltaperc, p_it1, sigma_pit1 = perda_retracao_concreto(
            p_it0,
            sigma_pit0 * 1E3,
            a_slcp * 1E-4,
            umidade,
            abatimento * 1E-2,
            a_c * 1E-4,
            mu_ar * 1E-2,
            t_0,
            t_1,
            temp,
            e_scp * 1E3
        )

        print(
            f"[POST /concreto] deltaperc: {deltaperc}, p_it1: {p_it1}, sigma_pit1: {sigma_pit1}, eps_cs: {eps_cs}")

        return jsonify({
            'deltaperc': deltaperc,
            'p_it1': p_it1,
            'sigma_pit1': sigma_pit1,
            'eps_cs': eps_cs
        })

    elif request.method == 'GET':
        response_data = {
            'deltaperc': deltaperc,
            'p_it1': p_it1,
            'sigma_pit1': sigma_pit1,
            'eps_cs': eps_cs
        }

        return jsonify(response_data)
