from flask import Blueprint, request, jsonify
import pandas as pd
from app.utils.calculos import projeto_paredes_compressao

alvenaria_bp = Blueprint('colapsoProgressivo', __name__)

# Variáveis globais
n_rd, n_sd, g_0, dados_parede =0,0,0,0
gamma_f, gamma_w, f_pk, g_laje, q_laje, g_pare, n_pavtos, comp_estrutura, larg_estrutura, tipo_argamassa=0,0,0,0,0,0,0,0,0,0
df = None
response_data = {}



@alvenaria_bp.route('/colapsoProgressivo', methods=['POST', 'GET'])
def alvenaria():
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
        tipo_argamassa = float(argamassa1)
        
        
        file = request.files.get('arq1')
        if file:
            df = pd.read_excel(file)
            print(f"[POST /colapsoProgressivo] Arquivo recebido: {df.shape}")

            n_rd, n_sd, g_0, dados_parede = projeto_paredes_compressao(df, gamma_f, gamma_w, f_pk, g_laje, q_laje, g_pare, n_pavtos, comp_estrutura, larg_estrutura, tipo_argamassa)
            return jsonify({
                'n_rd': n_rd,
                'n_sd': n_sd,
                'g_0': g_0,
                'dados_parede': dados_parede            })

    elif request.method == 'GET':
        response_data = {
             'n_rd': n_rd,
             'n_sd': n_sd,
              'g_0': g_0,
             'dados_parede': dados_parede            
        }
        return jsonify(response_data)
