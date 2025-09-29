
from flask import Blueprint, request, jsonify
from app.utils.calculos import circulo_mohr_2d
import pandas as pd

mecSolidos_bp = Blueprint('mecSolidos', __name__)

# Variáveis globais
sig_x, sig_y, tau=0,0,0
fig, sigma_med, raio, sigma_maxx, sigma_minn, theta_p_graus, theta_c_graus=None,0,0,0,0,0,0
response_data = {}

@mecSolidos_bp.route('/mecSolidos', methods=['POST', 'GET'])
def handle_user_data():
    global response_data, sig_x, sig_y, tau, fig, sigma_med, raio, sigma_maxx, sigma_minn, theta_p_graus, theta_c_graus
    
        step=1e-8
    if request.method == 'POST':

        sig_x = float(data.get('sigmax1'))
        sig_y   = float(data.get('sigmay1'))
        tau  = float(data.get('tauxy1'))

        data = request.get_json() or {}
        print("Dados recebidos:", data)

   

        # chamada para cálculo
        fig, sigma_med, raio, sigma_maxx, sigma_minn, theta_p_graus, theta_c_graus = circulo_mohr_2d(sig_x, sig_y, tau, impressoes=True)
        st.pyplot(fig)
        response_data = { 
           'sigma_med':  f'{sigma_med:.3e}',
                 'raio':   f'{raio:.3e}',
                   'sigma_maxx': f'{sigma_maxx:.3e}',
                   'sigma_minn': f'{sigma_minn:.3e}',
                   'theta_p_graus': f'{theta_p_graus:.3f} º',
                   'theta_c_graus': f'{theta_c_graus:.3f} º',
                    'fig': fig,
        }

    elif request.method == 'GET':
        response_data = { 
           'sigma_med':  f'{sigma_med:.3e}',
                 'raio':   f'{raio:.3e}',
                   'sigma_maxx': f'{sigma_maxx:.3e}',
                   'sigma_minn': f'{sigma_minn:.3e}',
                   'theta_p_graus': f'{theta_p_graus:.3f} º',
                   'theta_c_graus': f'{theta_c_graus:.3f} º',
                   'fig': fig,

        }
        print("response_data", response_data)

    return jsonify(response_data)
