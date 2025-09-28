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
    global df, gamma_f, gamma_w, f_pk, g_laje, q_laje, g_pare, n_pavtos, comp_estrutura, larg_estrutura, tipo_argamassa, df

    if request.method == 'POST':

       acaoperm1 = formData.acaoperm;
       acaovar1 = formData.acaovar;
       bloco1 = formData.bloco;
       lajep1 = formData.lajep;
       lajev1 = formData.lajev;
       peso1 = formData.peso;
       pav1 = formData.pav;
       estr1 = formData.estr;
       larg1 = formData.larg;
       argamassa1=formData.argamassa;



        # Recebe os dados do formulário multipart/form-data
        viga1 = request.form.get('viga1')
        iviga1 = request.form.get('iviga1')
        distanciatopo1 = request.form.get('distanciatopo1')
        distancia1 = request.form.get('distancia1')

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
