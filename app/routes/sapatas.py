from flask import Blueprint, request, jsonify
from app.utils.calculos import perda_retracao_concreto
import pandas as pd
import numpy as np
import subprocess
import sys

from itertools import combinations
from app.utils.calculos import carregar_dados, estaca_info, capacidade_carga, download_excel, plot_data, save_dxf
from utilitarios import vazio

sapatas = Blueprint('sapatas', __name__)

# Variáveis globais (como no original)
deltaperc = p_it1 = sigma_pit1 = eps_cs = 0
response_data = {}


@sapatas_bp.route('/sapatas', methods=['POST', 'GET'])
def handle_sapatas():
    global deltaperc, p_it1, sigma_pit1, eps_cs, response_data

      # Carregamento do arquivo SPT
        spt_file = st.file_uploader("Selecione o arquivo com a lista de SPT e suas coordenadas", type=["csv", "xlsx"])
        if spt_file is not None:
            df_spt = pd.read_excel(spt_file, engine='openpyxl')
            df_spt.columns = df_spt.columns.str.strip()


    if request.method == 'POST':
        data = request.get_json()

        p_it0 = float(data.get('cargain1'))
        sigma_pit0 = float(data.get('tensinit1'))
        umidade = float(data.get('umidade1'))
        a_slcp = float(data.get('totalarmadura1'))
        abatimento = float(data.get('umidade1'))
        a_c = float(data.get('slump1'))
        mu_ar = float(data.get('areabruta1'))
        t_0 = float(data.get('perimex1'))
        t_1 = float(data.get('tempin1'))
        temp = float(data.get('temp1'))
        e_scp = float(data.get('young1'))

        eps_cs, deltaperc, p_it1, sigma_pit1 = perda_retracao_concreto(
            p_it0,
            sigma_pit0 * 1E3,
            a_slcp * 1E-4,
            umidade,
            abatimento * 1E-2,
            a_c * 1E-4,
            mu_ar * 1E-2,
            t_0,
            t_1,
            temp,
            e_scp * 1E3
        )

        print(
            f"[POST /sapatas] deltaperc: {deltaperc}, p_it1: {p_it1}, sigma_pit1: {sigma_pit1}, eps_cs: {eps_cs}")

        return jsonify({
            'deltaperc':  f'{deltaperc:.2f} %',
            'p_it1':  f'{p_it1:.3e} kN',
            'sigma_pit1': f'{sigma_pit1/1000:.3e} MPa',
            'eps_cs': f'{eps_cs:.3e}'
        })

    elif request.method == 'GET':
        response_data = {
            'deltaperc':  f'{deltaperc:.2f} %',
            'p_it1':  f'{p_it1:.3e} kN',
            'sigma_pit1': f'{sigma_pit1/1000:.3e} MPa',
            'eps_cs': f'{eps_cs:.3e}'
        }

        return jsonify(response_data)
