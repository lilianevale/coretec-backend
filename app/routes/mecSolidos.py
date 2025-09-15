
from flask import Blueprint, request, jsonify
from app.utils.calculos import prop_geometrica_estadio_ii
import pandas as pd

mecSolidos_bp = Blueprint('mecSolidos', __name__)

# Variáveis globais
sig_x, sig_y, tau=0,0,0

response_data = {}

@mecSolidos_bp.route('/mecSolidos', methods=['POST', 'GET'])
def handle_user_data():
    global response_data, sig_x, sig_y, tau
    
        step=1e-8
    if request.method == 'POST':

        sig_x = float(data.get('sigmax1'))
        sig_y   = float(data.get('sigmay1'))
        tau  = float(data.get('tauxy1'))

        data = request.get_json() or {}
        print("Dados recebidos:", data)

   

        # chamada para cálculo
        fig, sigma_med, raio, sigma_maxx, sigma_minn, theta_p_graus, theta_c_graus = circulo_mohr_2d(sig_x, sig_y, tau, impressoes=True)
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
