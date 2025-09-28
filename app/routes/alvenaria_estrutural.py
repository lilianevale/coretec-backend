from flask import Blueprint, request, jsonify
import pandas as pd
from app.utils.calculos import tensao_topo_base, tensoes_vao_completo

alvenaria_bp = Blueprint('colapsoProgressivo', __name__)

# Variáveis globais
n_rd, n_sd, g_0, dados_parede =0,0,0,0
gamma_f, gamma_w, f_pk, g_laje, q_laje, g_pare, n_pavtos, comp_estrutura, larg_estrutura, tipo_argamassa=0,0,0,0,0,0,0,0,0,0
df = None
response_data = {}



@tensao_bp.route('/colapsoProgressivo', methods=['POST', 'GET'])
def tensao_elastica_vao():
    global df, gamma_f, gamma_w, f_pk, g_laje, q_laje, g_pare, n_pavtos, comp_estrutura, larg_estrutura, tipo_argamassa
    global n_rd, n_sd, g_0, dados_parede, response_data

    if request.method == 'POST':

        acaoperm1 = resquest.form.get(acaoperm1)
        acaovar1 = resquest.form.get(acaovar1)
        bloco1 = resquest.form.get(bloco1)
        lajep1 = resquest.form.get(lajep1)
        lajev1 = resquest.form.get(lajev1)
        peso1 = resquest.form.get(peso1)
        pav1 = resquest.form.get(pav1)
        estr1 = resquest.form.get(estr1)
        larg1 = resquest.form.get(larg1)
        argamassa1=resquest.form.get(argamassa1)

        gamma_f= float(acaoperm1)
        gamma_w= float(acaovar1)
        f_pk= float(bloco1)
        g_laje= float(lajep1)
        q_laje= float(lajev1)
        g_pare= float(peso1)
        n_pavtos= float(pav1)
        comp_estrutura= float(estr1)
        larg_estrutura= float(larg1)
        tipo_argamassa = float(
        
        a_c = float(viga1)
        i_c = float(iviga1)
        y_t = float(distanciatopo1)
        y_b = float(distancia1)

        file = request.files.get('arq1')
        if file:
            df = pd.read_excel(file)
            print(f"[POST /tensaoelasticavao] Arquivo recebido: {df.shape}")

            sigma_t_vazio, sigma_b_vazio, sigma_t_serv, sigma_b_serv, imagem_url = tensoes_vao_completo(
                df, a_c * 1E-4, i_c * 1E-8, y_t * 1E-2, y_b * 1E-2
            )

            return jsonify({
                'imagem_url': imagem_url,
                'sigma_t_vazio1': sigma_t_vazio,
                'sigma_b_vazio1': sigma_b_vazio,
                'sigma_t_serv1': sigma_t_serv,
                'sigma_b_serv1': sigma_b_serv
            })

    elif request.method == 'GET':
        response_data = {
            'imagem_url': imagem_url,
            'sigma_t_vazio1': sigma_t_vazio,
            'sigma_b_vazio1': sigma_b_vazio,
            'sigma_t_serv1': sigma_t_serv,
            'sigma_b_serv1': sigma_b_serv
        }
        return jsonify(response_data)
