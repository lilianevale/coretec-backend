from flask import Blueprint, request, jsonify
import pandas as pd
from app.utils.calculos import tensao_topo_base, tensoes_vao_completo

tensao_bp = Blueprint('tensao', __name__)

# Variáveis globais
sigma_t = sigma_b = 0
sigma_t_vazio = sigma_b_vazio = sigma_t_serv = sigma_b_serv = []
df = None
response_data = {}


@tensao_bp.route('/tensaoelastica', methods=['POST', 'GET'])
def tensao_elastica():
    global sigma_t, sigma_b, response_data

    if request.method == 'POST':
        data = request.get_json()

        # Coleta e conversão dos dados
        a_c = float(data.get('viga1'))              # Área da seção (cm²)
        i_c = float(data.get('iviga1'))             # Inércia (cm⁴)
        y_t = float(data.get('distanciatopo1'))     # Distância topo (cm)
        y_b = float(data.get('distancia1'))         # Distância base (cm)
        e_p = float(data.get('excentricidade1'))    # Excentricidade (cm)
        p_id = float(data.get('protensao1'))        # Protensão (kN)
        m_sd = float(data.get('fletor1'))           # Momento (kNm)

        # Cálculo
        sigma_t, sigma_b, imagem_url = tensao_topo_base(
            a_c * 1E-4, i_c * 1E-8,
            y_t * 1E-2, y_b * 1E-2,
            e_p * 1E-2, p_id, m_sd
        )

        return jsonify({
            'sigma_t1': sigma_t,
            'sigma_b1': sigma_b,
            'imagem_url': imagem_url
        })

    elif request.method == 'GET':
        response_data = {
            'imagem_url': imagem_url,
            'sigma_t1': sigma_t,
            'sigma_b1': sigma_b
        }
        return jsonify(response_data)


@tensao_bp.route('/tensaoelasticavao', methods=['POST', 'GET'])
def tensao_elastica_vao():
    global sigma_t_vazio, sigma_b_vazio, sigma_t_serv, sigma_b_serv, df, response_data

    if request.method == 'POST':
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
