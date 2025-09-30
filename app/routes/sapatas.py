from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
from itertools import combinations
from app.utils.calculos import plot_data

sapatas_bp = Blueprint('sapatas', __name__)

# Variáveis globais
fig = None
response_data = {}


@sapatas_bp.route('/sapatas', methods=['POST', 'GET'])
def handle_sapatas():
    global response_data, fig

    if request.method == 'POST':
        # Arquivo SPT
        spt_file = request.files.get('arq1')
        if not spt_file:
            return jsonify({'error': "Arquivo 'arq1' (SPT) não enviado"}), 400

        df_spt = pd.read_excel(spt_file, engine='openpyxl')
        df_spt.columns = df_spt.columns.str.strip()

        # Arquivo TQS
        tqs_file = request.files.get('arq2')
        if not tqs_file:
            return jsonify({'error': "Arquivo 'arq2' (TQS) não enviado"}), 400

        df_tqs = pd.read_excel(tqs_file)
        df_tqs.columns = df_tqs.iloc[0].dropna().values
        df_tqs = df_tqs[1:]

        # Renomear colunas duplicadas
        df_tqs.columns = pd.Index(
            [
                f"{col}_{i}" if (df_tqs.columns[:i].tolist().count(col) > 0) else col
                for i, col in enumerate(df_tqs.columns)
            ]
        )

        # Nomes dos elementos (ajuste conforme seu Excel: aqui uso a coluna vazia ' ')
        elem_names = df_tqs[df_tqs.columns[0]].astype(str).values

        fx_max, fx_min, fy_max, fy_min, fz_max, fz_min, mx_max, mx_min, my_max, my_min = ([] for _ in range(10))

        for _, row in df_tqs.iterrows():
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
            "Fx_max": fx_max, "Fx_min": fx_min,
            "Fy_max": fy_max, "Fy_min": fy_min,
            "Fz_max": fz_max, "Fz_min": fz_min,
            "Mx_max": mx_max, "Mx_min": mx_min,
            "My_max": my_max, "My_min": my_min
        })

        if 'Elem' in df_spt.columns and 'Elem' in new_tqs.columns:
            df_final = pd.merge(df_spt, new_tqs, on='Elem', how='inner')
            df_final.insert(3, 'Hx (m)', np.random.uniform(0, 1, size=len(df_final)))
            df_final.insert(4, 'Hy (m)', np.random.uniform(0, 1, size=len(df_final)))

            # Combinações válidas
            cols = ['Fz_max', 'Fz_min', 'Mx_max', 'Mx_min', 'My_max', 'My_min']
            combinations_3 = list(combinations(cols, 3))
            data_valid_combinations = [
                comb for comb in combinations_3
                if len(set(c.split('_')[0] for c in comb)) == 3
            ]

            # Gráfico
            data_plot = {
                'label': df_final['Elem'],
                'x': df_final.get('x (m)', pd.Series(np.zeros(len(df_final)))),
                'y': df_final.get('y (m)', pd.Series(np.zeros(len(df_final)))),
                'L x': df_final['Hx (m)'],
                'L y': df_final['Hy (m)']
            }
            fig = plot_data(data_plot)

            return jsonify({
                'table1': df_final.to_dict(orient="records"),
                'table2': data_valid_combinations,
                'fig': str(fig)  # ou salvar imagem em base64 se precisar
            })
        else:
            return jsonify({'error': "Não foi possível encontrar a coluna 'Elem' em ambos os arquivos."}), 400

    elif request.method == 'GET':
        return jsonify(response_data)
