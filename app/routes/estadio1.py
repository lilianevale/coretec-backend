from flask import Blueprint, request, jsonify
from app.utils.calculos import perda_deformacao_imediata_concreto_pre_tracao
import pandas as pd

estadio1_bp = Blueprint('estadio1', __name__)

# Variáveis globais (como no seu código original)
a_ci, x_i, i_i, w_inf, w_sup=0,0,0,0,0
response_data = {}

@estadio1_bp.route('/estadio1', methods=['POST', 'GET'])
def handle_user_data():
    global response_data
    if request.method == 'POST':
        # Get the data from the JSON body of the request
        data = request.get_json()
        global h, h_f, b_f, b_w, a_st, alpha_mod, d
        # Access the username and email parameters sent from the frontend
        global a_ci, x_i, i_i, w_inf, w_sup
        step= 1e-8
        h= float(data.get('htotal1'))
        h_f= float(data.get('hmesa1'))
        b_f= float(data.get('lmesa1'))
        b_w= float(data.get('alma1'))
        a_st= float(data.get('tracao1'))
        alpha_mod=float(data.get('modulos1'))
        d=float(data.get('fletor1'))
       
        a_ci, x_i, i_i, w_inf, w_sup = prop_geometrica_estadio_i(h, h_f, b_f, b_w, a_st/1e4, alpha_mod, d)

        # Perform any necessary backend processing with the received data
    elif request.method == 'GET':

        response_data = { 
                    'a_ci':f"{a_ci*1e4:.3e}",
                    'x_i':f"{x_i * 1e2:.3e}",
                    'i_i': f"{i_i:.3e}",
                    'w_inf':f"{w_inf*1e6:.3e}",
                    'w_sup':f"{w_sup*1e6:.3e}",
        }
        print("response_data ", response_data )

   # return {
    #       'message': 'result',
     #       'resultado0' : resultado0,
      #      'resultado1' : resultado1,
       #     'resultado2' : resultado2,
        #    'resultado3' : resultado3

   # } 
    return jsonify(response_data)
