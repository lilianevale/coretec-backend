from flask import Blueprint, request, jsonify
from app.utils.calculos import area_aco_flexao_simples

# Criação do Blueprint
fsarmado_bp = Blueprint('fsarmado', __name__)

# Variáveis globais
step, b_w, h, d, f_ck, f_ywkaux, f_ywk, gamma_c, gamma_s = 0, 0, 0, 0, 0, "", 0, 0, 0
m_sd, v_sd, cob, phi_est, d_max = 0, 0, 0, 0, 0
x_iii, z_iii, a_slmin, a_sl, v_rd2, v_c0 = 0, 0, 0, 0, 0, 0
a_swmin, a_sw90, a_h, a_v, n_bar_cam, fig = 0, 0, 0, 0, 0, None

@fsarmado_bp.route('/fsarmado', methods=['POST', 'GET'])
def handle_fsarmado():
    global step, b_w, h, d, f_ck, f_ywkaux, f_ywk, gamma_c, gamma_s
    global m_sd, v_sd, cob, phi_est, d_max
    global x_iii, z_iii, a_slmin, a_sl, v_rd2, v_c0
    global a_swmin, a_sw90, a_h, a_v, n_bar_cam, fig

    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Nenhum dado enviado"}), 400

        # Conversão de dados recebidos
        step = 1e-8
        b_w = float(data.get('lviga1', 0))
        h = float(data.get('hviga1', 0))
        d = float(data.get('hutilsecao1', 0))
        f_ck = float(data.get('resistconc1', 0))
        f_ywkaux = data.get('resistaco1', '')  # string
        gamma_c = float(data.get('cofconc1', 0))
        gamma_s = float(data.get('cofaco1', 0))
        m_sd = float(data.get('fletor1', 0))
        v_sd = float(data.get('corte1', 0))
        cob = float(data.get('tamanho1', 0))
        phi_est = float(data.get('estribo1', 0)) / 1000
        d_max = float(data.get('fletor1', 0)) / 1000

        # Determinar f_ywk em kPa
        if f_ywkaux == 'CA-25':
            f_ywk = 250e3
        elif f_ywkaux == 'CA-50':
            f_ywk = 500e3
        else:
            f_ywk = 600e3

        # Cálculo da área de aço e demais parâmetros
        x_iii, z_iii, a_slmin, a_sl, v_rd2, v_c0, \
        a_swmin, a_sw90, a_h, a_v, n_bar_cam, fig = area_aco_flexao_simples(
            b_w/100, h/100, d/100, f_ck*1000, f_ywk, gamma_c, gamma_s,
            m_sd, v_sd, cob/100, phi_est, d_max
        )

        return jsonify({"message": "Cálculo realizado com sucesso"})

    elif request.method == 'GET':
        return jsonify({
            'x_iii': f"{x_iii*1e2:.3e}",
            'z_iii': f"{z_iii*1e2:.3e}",
            'a_slmin': f"{a_slmin*1e4:.3e}",
            'a_sl': f"{a_sl*1e4:.3e}",
            'v_rd2': f"{v_rd2:.3e}",
            'v_c0': f"{v_c0:.3e}",
            'a_swmin': f"{a_swmin*1e4:.3e}",
            'a_sw90': f"{a_sw90*1e4:.3e}",
            'n_bar_cam': n_bar_cam,
            'fig': fig
        })
