from flask import Blueprint, request, jsonify
from app.utils.calculos import perda_fluencia_concreto

fluencia_bp = Blueprint('fluencia', __name__)


@fluencia_bp.route('/fluencia', methods=['POST', 'GET'])
def handle_user_data7():
    global response_data
    if request.method == 'POST':
        # Get the data from the JSON body of the request
        data = request.get_json()
        # Access the username and email parameters sent from the frontend
        global p_it0, sigma_pit0, a_c, t_1, mu_ar, abatimento, a_slcp, umidade, tipo_endurecimento, t_0, e_scp, e_ccpt1, sigma_cabo, f_ck0, f_ck, temp
        global deltaperc, p_it1, sigma_pit1, psi, phi
        p_it0 = float(data.get('protensao1'))
        sigma_pit0 = float(data.get('ti1'))
        a_slcp = float(data.get('armprot1'))
        a_c = float(data.get('areabruta1'))
        mu_ar = float(data.get('ar1'))
        abatimento = float(data.get('slump1'))
        umidade = float(data.get('umidade1'))
        tipo_endurecimento = (data.get('endurecimento1'))
        t_0 = float(data.get('correcaotemp1'))
        t_1 = float(data.get('correcaotemp1'))
        temp = float(data.get('tempproj1'))
        e_scp = float(data.get('young1'))
        e_ccpt1 = float(data.get('young281'))
        sigma_cabo = float(data.get('tensaoarm1'))
        f_ck0 = float(data.get('resistencia1'))
        f_ck = float(data.get('resistencia281'))

        phi, deltaperc, p_it1, sigma_pit1 = perda_fluencia_concreto(p_it0, sigma_pit0*1E3, a_slcp*1E-4, a_c*1E-4, mu_ar*1E-2, abatimento*1E-2, umidade, tipo_endurecimento,
                                                                    temp, e_scp*1E3, e_ccpt1*1E3, sigma_cabo*1E3, t_0, t_1, f_ck0*1E3, f_ck*1E3)
    elif request.method == 'GET':

        response_data = {
            'deltaperc1': deltaperc,
            'sigma_pit11': sigma_pit1,
            'p_it11': p_it1,
            'phi1': phi

        }
        print("response_data fluencia", response_data)

    response_data = {
        'deltaperc1': deltaperc,
        'sigma_pit11': sigma_pit1,
        'p_it11': p_it1,
        'phi1': phi

    }
   
    return jsonify(response_data)
