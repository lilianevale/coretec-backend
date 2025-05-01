from flask import Blueprint, request, jsonify
from app.utils.calculos import perda_deslizamento_ancoragem

ancoragem_bp = Blueprint('ancoragem', __name__)

deltaperc = p_it1 = sigma_pit1 = 0
response_data = {}


@ancoragem_bp.route('/ancoragem', methods=['POST', 'GET'])
def handle_ancoragem():
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
            'deltaperc': deltaperc,
            'p_it1': p_it1,
            'sigma_pit1': sigma_pit1,
        })

    elif request.method == 'GET':
        response_data = {
            'deltaperc': deltaperc,
            'p_it1': p_it1,
            'sigma_pit1': sigma_pit1
        }

        return jsonify(response_data)
