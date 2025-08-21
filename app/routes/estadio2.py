from flask import Blueprint, request, jsonify
from app.utils.calculos import perda_relax_armadura
import pandas as pd

estadio2_bp = Blueprint('estadio2', __name__)

# Variáveis globais como no seu código original
x_ii, i_ii, a_1, a_2, a_3, passa_onde, x_ii_teste =0,0,0,0,0,0,0
response_data = {}



@estadio2_bp.route('/estadio2', methods=['POST', 'GET'])
def handle_user_data():
    global response_data
    if request.method == 'POST':
        # Get the data from the JSON body of the request
        data = request.get_json()
        global h, h_f, b_f, b_w, a_st, a_sc, alpha_mod, d, dl
        # Access the username and email parameters sent from the frontend
        global x_ii, i_ii, a_1, a_2, a_3, passa_onde, x_ii_teste 
        step= 1e-8
        h_f= float(data.get('hmesa1'))
        b_f= float(data.get('lmesa1'))
        b_w= float(data.get('alma1'))
        a_st= float(data.get('tracao1'))
        a_sc=float(data.get('comprimida1'))
        alpha_mod=float(data.get('modulos1'))
        d=float(data.get('fletor1'))
        dl=float(data.get('hcompr1'))
       
        x_ii, i_ii, a_1, a_2, a_3, passa_onde, x_ii_teste = prop_geometrica_estadio_ii(h_f, b_f, b_w, a_st/1e4, a_sc/1e4, alpha_mod, d, d_l)
        # Perform any necessary backend processing with the received data
    elif request.method == 'GET':

        response_data = { 
                    'x_ii': f'{x_ii_teste*1e2:.3e} cm',
                    'i_ii':f'{i_ii:.3e} m\u2074',
                    'a_1': f'{a_1*1e2:.3e} cm',
                    'a_2':f'{a_2*1e4:.3e} cm²',
                    'a_3':f'{a_3*1e6:.3e} cm³',
                    'passa_onde':passa_onde,
                    'x_ii_teste':f'{x_ii_teste*1e2:.3e} cm',
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
    
