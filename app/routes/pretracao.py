from flask import Blueprint, request, jsonify
from app.utils.calculos import perda_deformacao_imediata_concreto_pre_tracao
import pandas as pd

pretracao_bp = Blueprint('pretracao', __name__)

# Variáveis globais (como no seu código original)
deltaperc = p_it1 = sigma_pit1 = 0
response_data = {}

@pretracao_bp.route('/pretracao', methods=['POST', 'GET'])
def handle_pretracao():
    global deltaperc, p_it1, sigma_pit1, response_data

    if request.method == 'POST':
        data = request.get_json()

        # Coleta e conversão dos dados de entrada
        e_scp = float(data.get('elasticidadeaco1'))   # Módulo do aço (GPa)
        e_ccp = float(data.get('elasticidadeconc1'))  # Módulo do concreto (GPa)
        p_it0 = float(data.get('ci1'))                # Carga inicial (kN)
        sigma_pit0 = float(data.get('ti1'))           # Tensão inicial (MPa)
        a_c = float(data.get('secaobruta1'))          # Área da seção (cm²)
        i_c = float(data.get('inerciabruta1'))        # Inércia (cm⁴)
        m_gpp = float(data.get('fletor1'))            # Momento (kNm)
        e_p = float(data.get('excentricidade1'))      # Excentricidade (cm)
        a_slcp = float(data.get('armadura1'))         # Área da armadura (cm²)

        # Chamada da função de cálculo
        deltaperc, p_it1, sigma_pit1 = perda_deformacao_imediata_concreto_pre_tracao(
            e_scp * 1E3, e_ccp * 1E3,
            p_it0, sigma_pit0 * 1E3,
            a_slcp * 1E-4, a_c * 1E-4,
            i_c * 1E-8, e_p * 1E-2,
            m_gpp
        )

        print(f"[POST /pretracao] deltaperc: {deltaperc}, p_it1: {p_it1}, sigma_pit1: {sigma_pit1}")

        return jsonify({
            'deltaperc': f'{deltaperc:.2f} %',
            'p_it1': f'{p_it1:.3e} kN',
            'sigma_pit1':  f'{sigma_pit1/1000 :.3e} MPa'
        })

    elif request.method == 'GET':
        response_data = {
            'deltaperc': f'{deltaperc:.2f} %',
            'p_it1': f'{p_it1:.3e} kN',
            'sigma_pit1':  f'{sigma_pit1/1000 :.3e} MPa'
        }

        return jsonify(response_data)
