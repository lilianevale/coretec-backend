from flask import Blueprint, request, jsonify
from app.utils.calculos import circulo_mohr_2d
import io
import base64

mecSolidos_bp = Blueprint('mecSolidos', __name__)

# Variáveis globais
sig_x, sig_y, tau = 0, 0, 0
fig = None
sigma_med, raio, sigma_maxx, sigma_minn, theta_p_graus, theta_c_graus = 0, 0, 0, 0, 0, 0
response_data = {}


@mecSolidos_bp.route('/mecSolidos', methods=['POST', 'GET'])
def handle_user_data():
    global response_data, sig_x, sig_y, tau, fig
    global sigma_med, raio, sigma_maxx, sigma_minn, theta_p_graus, theta_c_graus

    if request.method == 'POST':
        # pega dados enviados no corpo JSON
        data = request.get_json() or {}
        print("Dados recebidos:", data)

        sig_x = float(data.get('sigmax1', 0))
        sig_y = float(data.get('sigmay1', 0))
        tau = float(data.get('tauxy1', 0))

        # chamada para cálculo
        fig, sigma_med, raio, sigma_maxx, sigma_minn, theta_p_graus, theta_c_graus = circulo_mohr_2d(
            sig_x, sig_y, tau, impressoes=True
        )

        # converter figura em base64
        img_bytes = io.BytesIO()
        fig.savefig(img_bytes, format='png')
        img_bytes.seek(0)
        fig_base64 = base64.b64encode(img_bytes.read()).decode("utf-8")

        response_data = {
            'sigma_med': f'{sigma_med:.3e}',
            'raio': f'{raio:.3e}',
            'sigma_maxx': f'{sigma_maxx:.3e}',
            'sigma_minn': f'{sigma_minn:.3e}',
            'theta_p_graus': f'{theta_p_graus:.3f} º',
            'theta_c_graus': f'{theta_c_graus:.3f} º',
            'fig': fig_base64  # figura como base64
        }

    elif request.method == 'GET':
        response_data = {
            'sigma_med': f'{sigma_med:.3e}',
            'raio': f'{raio:.3e}',
            'sigma_maxx': f'{sigma_maxx:.3e}',
            'sigma_minn': f'{sigma_minn:.3e}',
            'theta_p_graus': f'{theta_p_graus:.3f} º',
            'theta_c_graus': f'{theta_c_graus:.3f} º',
            # não retorna fig no GET, só os últimos cálculos
        }
        print("response_data", response_data)

    return jsonify(response_data)
