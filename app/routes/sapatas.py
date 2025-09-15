from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
import subprocess
import sys

from itertools import combinations
from app.utils.calculos import carregar_dados, estaca_info, capacidade_carga, download_excel, plot_data, save_dxf, vazio

sapatas = Blueprint('sapatas', __name__)

# Variáveis globais (como no original)
response_data = {}


@sapatas_bp.route('/sapatas', methods=['POST', 'GET'])
def handle_sapatas():
  if request.method == 'POST':
        data = request.get_json()
      # Carregamento do arquivo SPT
     s  pt_file = request.files.get('arq1')

        if spt_file is not None:
            df_spt = pd.read_excel(spt_file, engine='openpyxl')
            df_spt.columns = df_spt.columns.str.strip()



 # Carregamento do arquivo TQS
        tqs_file = request.files.get('arq2')

        if tqs_file is not None:
            df_tqs = pd.read_excel(tqs_file)
            # Definir a primeira linha como cabeçalho
            df_tqs.columns = df_tqs.iloc[0].dropna().values
            df_tqs = df_tqs[1:]

            # Renomear colunas duplicadas
            df_tqs.columns = pd.Index(
                [f"{col}_{i}" if (df_tqs.columns[:i].tolist().count(col) > 0) else col 
                for i, col in enumerate(df_tqs.columns)]
            )
                    
             elem_names = df_tqs[' '].iloc[0:].values
            fx_max = []
            fx_min = []
            fy_max = []
            fy_min = []
            fz_max = []
            fz_min = []
            mx_max = []
            mx_min = []
            my_max = []
            my_min = []

            for index, row in df_tqs.iterrows():
                if index > 0:
                    fx_max.append(row.filter(like='Fx').max())
                    fx_min.append(row.filter(like='Fx').min())
                    fy_max.append(row.filter(like='Fy').max())
                    fy_min.append(row.filter(like='Fy').min())
                    fz_max.append(row.filter(like='Fz').max())
                    fz_min.append(row.filter(like='Fz').min())
                    mx_max.append(row.filter(like='Mx').max())
                    mx_min.append(row.filter(like='Mx').min())
                    my_max.append(row.filter(like='My').max())
                    my_min.append(row.filter(like='My').min())

            new_tqs = pd.DataFrame({
                "Elem": elem_names,
                "Fx_max": fx_max,
                "Fx_min": fx_min,
                "Fy_max": fy_max,
                "Fy_min": fy_min,
                "Fz_max": fz_max,
                "Fz_min": fz_min,
                "Mx_max": mx_max,
                "Mx_min": mx_min,
                "My_max": my_max,
                "My_min": my_min
            })

            if 'Elem' in df_spt.columns and 'Elem' in new_tqs.columns:
                df_final = pd.merge(df_spt, new_tqs, on='Elem', how='inner')
                df_final.insert(3, 'Hx (m)', np.random.uniform(0, 1, size=len(df_final)))
                df_final.insert(4, 'Hy (m)', np.random.uniform(0, 1, size=len(df_final)) )
                st.title("Dataframe com os dados das tabelas inseridas")
                st.table(df_final)

                columns = ['Fz_max', 'Fz_min', 'Mx_max', 'Mx_min', 'My_max', 'My_min']
                combinations_3 = list(combinations(columns, 3))
                
                valid_combinations = [
                    comb for comb in combinations_3 
                    if len(set(col.split('_')[0] for col in comb)) == 3
                ]
                data_valid_combinations = pd.DataFrame({'Combinações válidas:': valid_combinations})
                st.title("Combinações válidas")
                st.table(data_valid_combinations)

                #Plotar gráfico
                data_plot = {
                    'label': df_final['Elem'],
                    'x': df_final['x (m)'],
                    'y': df_final['y (m)'],
                    'L x': df_final['Hx (m)'],
                    'L y': df_final['Hy (m)']
                }
                fig = plot_data(data_plot)

                st.title("Gráfico das Posições das Sapatas")
                st.pyplot(fig)

               
            else:
                st.error("Não foi possível encontrar a coluna 'Elem' em ambos os arquivos.")


   
       
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
