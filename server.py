# Filename - server.py

# Import flask and datetime module for showing date and time
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import openpyxl
import openai
from flask import Flask, jsonify, render_template, request, session
import datetime
import numpy as np
import matplotlib.pyplot as plt
import tempfile
import pandas as pd
import matplotlib
matplotlib.pyplot.switch_backend('Agg')


# Define the folder where uploads will be stored
UPLOAD_FOLDER = 'uploads'
# Define allowed file extensions
ALLOWED_EXTENSIONS = {'ppt', 'pptx'}

# Initializing flask app
app = Flask(__name__)

response_data = {}
# Route for seeing a data

step, b_w, h, d, f_ck, f_ywkaux, f_ywk,  gamma_c,  gamma_s, m_sd, v_sd, cob,phi_est, d_max=0,0,0,0,0,"",0,0,0,0,0,0,0,0
x_iii, z_iii, a_slmin, a_sl, v_rd2, v_c0, a_swmin, a_sw90, a_h, a_v, n_bar_cam, fig =0,0,0,0,0,0,0,0,0,0,0,"teste.png"
h_f, b_f, b_w, a_st, a_sc, alpha_mod, d, dl=0,0,0,0,0,0,0,0
a_ci, x_i, i_i, w_inf, w_sup=0,0,0,0,0
x_ii, i_ii, a_1, a_2, a_3, passa_onde, x_ii_teste =0,0,0,0,0,0,0
resultado0, resultado1, resultado2, resultado3 = 0, 0, 0, 0
deltaperc, p_it1, sigma_pit1 = 0, 0, 0
sigma_t, sigma_b, fig = 0, 0, "teste.png"
a_c, i_c, y_t, y_b, e_p, p_id, m_sd = 0, 0, 0, 0, 0, 0, 0
areabruta, distopo, disbase, inercia, tensmin, tensmin, tensmax, fletor = 0, 0, 0, 0, 0, 0, 0, 0
a_slcp, p_it0, sigma_pit0, l_0, Delta_anc, e_scp = 0, 0, 0, 0, 0, 0
u, abat, a_c, mu_ar, t_0, t_1, eps_cs, temp = 0, 0, 0, 0, 0, 0, 0, 0
sigma_t_vazio, sigma_b_vazio, sigma_t_serv, df, sigma_b_serv = 0, 0, 0, "", ""
p_it0, sigma_pit0, t_0, t_1, temp, f_pk, a_slcp, tipo_aco, tipo_armadura = 0, 0, 0, 0, 0, 0, 0, "", ""
deltaperc, p_it1, sigma_pit1, psi, psi_1000 = 0, 0, 0, 0, 0
elasticidadeaco, belasticidadeconc, ci, ti, armadura, secaobruta, inerciabruta, excentricidade = 0, 0, 0, 0, 0, 0, 0, 0,
p_it0, sigma_pit0, a_c, t_1, mu_ar, abatimento, a_slcp, umidade, tipo_endurecimento, t_0, e_scp, e_ccpt1, sigma_cabo, f_ck0, temp, f_ck = 0, 0, 0, 0, 0, 0, 0, 0, "", 0, 0, 0, 0, 0, 0, 0
deltaperc, p_it1, sigma_pit1, psi, phi = 0, 0, 0, 0, 0

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Enable Cross-Origin Resource Sharing (CORS) to allow requests from the React app
CORS(app)

# Function to check for allowed file extensions


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
  if request.method == 'POST':

     # Check if the post request has the file part
     if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

     file = request.files['file']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
     if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

     if file and allowed_file(file.filename):
        # Use secure_filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)

        # Create the upload folder if it doesn't exist
     if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Save the file
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
       texto="Elabore questões sobre este conteúdo: "
     for eachfile in glob.glob(filename):
     prs = Presentation(eachfile)
     print(eachfile)
     print("----------------------")
     for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
              #  print(shape.text)
          
                texto=texto+'\n'+shape.text
                Ask_chatgpt = chat_with_gpt(texto)

 elif request.method == 'GET':

        response_data = { 
            ' \\n questões' : Ask_chatgpt,

        }
    return jsonify(response_data)




def chat_with_gpt(user_input):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",  # Use the appropriate engine
        prompt=user_input,
    )
# Extracting and returning the assistant's response
    assistant_response = response['choices'][0]['text']
    print("resposta:",  assistant_response)

    return assistant_response

@app.route('/fsarmado', methods=['POST', 'GET'])
def handle_user_data():
    global response_data
    if request.method == 'POST':
        # Get the data from the JSON body of the request
        data = request.get_json()
        global step, b_w, h, d, f_ck, f_ywkaux, f_ywk,  gamma_c,  gamma_s, m_sd, v_sd, cob, phi_est, d_max

        # Access the username and email parameters sent from the frontend
        global x_iii, z_iii, a_slmin, a_sl, v_rd2, v_c0, a_swmin, a_sw90, a_h, a_v, n_bar_cam, fig

        step= 1e-8
        b_w= float(data.get('lviga1'))
        h= float(data.get('hviga1'))
        d= float(data.get('hutilsecao1'))
        f_ck= float(data.get('resistconc1'))
        f_ywkaux= float(data.get('resistaco1'))
        gamma_c= float(data.get('cofconc1'))
        gamma_s=float(data.get('cofaco1'))
        m_sd=float(data.get('fletor1'))
        v_sd=float(data.get('corte'))
        cob=float(data.get('tamanho1'))
        phi_est=float(data.get('estribo1'))
        d_max=float(data.get('fletor1'))
        phi_est=phi_est/1000
        if f_ywkaux == 'CA-25':
            f_ywk = 250e3
        elif f_ywkaux == 'CA-50':
            f_ywk = 500e3
        else:
            f_ywk = 600e3

        x_iii, z_iii, a_slmin, a_sl, v_rd2, v_c0, a_swmin, a_sw90, a_h, a_v, n_bar_cam, fig = area_aco_flexao_simples(
                b_w/100, h/100, d/100, f_ck*1000, f_ywk, gamma_c, gamma_s, m_sd, v_sd, cob/100, phi_est, d_max/1000
            )   
        

        # Perform any necessary backend processing with the received data
    elif request.method == 'GET':

        response_data = { 
            'x_iii':f"{x_iii*1e2:.3e}",
            'z_iii' : f"{z_iii*1e2:.3e}",
            'a_slmin' : f"{a_slmin*1e4:.3e}",
            'a_sl' : f"{a_sl*1e4:.3e}",
            'v_rd2': f"{v_rd2:.3e}",
            'v_c0': f"{v_c0:.3e}",
            'a_swmin': f"{a_swmin*1e4:.3e}",
            'a_sw90': f"{a_sw90*1e4:.3e}",
            'n_bar_cam': n_bar_cam,
            'fig': fig,
            

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



app.route('/estadio1', methods=['POST', 'GET'])
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


@app.route('/estadio2', methods=['POST', 'GET'])
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
    

 
@app.route('/magnel', methods=['POST', 'GET'])
def handle_user_data():
    global response_data
    if request.method == 'POST':
        # Get the data from the JSON body of the request
        data = request.get_json()
        global areabruta, distopo, disbase, inercia, tensmin, tensmin, tensmax, fletor
        # Access the username and email parameters sent from the frontend
        global resultado0, resultado1, resultado2, resultado3
        areabruta = float(data.get('areabruta1'))
        distopo = float(data.get('distopo1'))
        disbase = float(data.get('disbase1'))
        inercia = float(data.get('inercia1'))
        tensmin = float(data.get('tensmin1'))
        tensmax = float(data.get('tensmax1'))
        fletor = float(data.get('fletor1'))
        print(areabruta)
        print(distopo)
        print(disbase)
        print(inercia)
        print(tensmin)
        print(tensmax)
        print(disbase)
        print(fletor)
        resultado0, resultado1, resultado2, resultado3 = diagrama_magnel(
            areabruta, distopo, disbase, inercia, tensmax, tensmin, fletor)
    # resultMagnel()
        print(f"Equação da reta 0: {resultado0}")
        print(f"Equação da reta 1: {resultado1}")
        print(f"Equação da reta 2: {resultado2}")
        print(f"Equação da reta 3: {resultado3}")

        # Perform any necessary backend processing with the received data
    elif request.method == 'GET':

        response_data = {
            ' \\nEquacao da reta 0': resultado0,
            '\\n Equacao da reta 1': resultado1,
            ' \\nEquacao da reta 2': resultado2,
            '\\n Equacao da reta 3': resultado3,


        }
        print("response_data ", response_data)

   # return {
    #       'message': 'result',
     #       'resultado0' : resultado0,
      #      'resultado1' : resultado1,
       #     'resultado2' : resultado2,
        #    'resultado3' : resultado3

   # }
    return jsonify(response_data)


def diagrama_magnel(a_c, y_t, y_b, i_c, sigma_max, sigma_min, m_sd_inicial):
    w_t = i_c / y_t
    w_b = i_c / y_b
    epsilon_b_max = sigma_max + m_sd_inicial / w_b
    epsilon_b_min = sigma_min + m_sd_inicial / w_b
    epsilon_t_max = sigma_max - m_sd_inicial / w_t
    epsilon_t_min = sigma_min - m_sd_inicial / w_t
    # eq_0 = r'$P_{sd} \leq \dfrac{' + f'{epsilon_b_max}' + r'}{\dfrac{1}{' + f'{a_c}' + r'} + \dfrac{' + f'{e_c}' + r'}{' + f'{w_b}' + r'}}$'
    # eq_1 = r'$P_{sd} \geq \dfrac{' + f'{epsilon_b_min}' + r'}{\dfrac{1}{' + f'{a_c}' + r'} + \dfrac{' + f'{e_c}' + r'}{' + f'{w_b}' + r'}}$'
    # eq_2 = r'$P_{sd} \geq \dfrac{' + f'{epsilon_t_max}' + r'}{\dfrac{1}{' + f'{a_c}' + r'} + \dfrac{' + f'{e_c}' + r'}{' + f'{w_t}' + r'}}$'
    # eq_3 = r'$P_{sd} \leq \dfrac{' + f'{epsilon_t_min}' + r'}{\dfrac{1}{' + f'{a_c}' + r'} + \dfrac{' + f'{e_c}' + r'}{' + f'{w_t}' + r'}}$'
    eq_0 = f'y >= ({1/a_c} + {1/w_b}. e_c) / {epsilon_b_max}'
    eq_1 = f'y <= ({1/a_c} + {1/w_b}. e_c) / {epsilon_b_min}'
    eq_2 = f'y >= ({1/a_c} - {1/w_t}. e_c) / {epsilon_t_max}'
    eq_3 = f'y <= ({1/a_c} - {1/w_t}. e_c) / {epsilon_t_min}'

    print("equacao 0", eq_0)
    print("equacao 1", eq_1)
    print("equacao 2", eq_2)
    print("equacao 3", eq_3)
    f = open(
        "C:/Users/Zeyah/Downloads/projeto-liliane/react-ezequiel/client/public/calc.txt", "w")
    f.write(eq_0+"\n")
    f.write(eq_1+"\n")
    f.write(eq_2+"\n")
    f.write(eq_3+"\n")

    f.close()

    return eq_0, eq_1, eq_2, eq_3


@app.route('/pretracao', methods=['POST', 'GET'])
def handle_user_data1():
    global response_data
    if request.method == 'POST':
        # Get the data from the JSON body of the request
        data = request.get_json()
        global elasticidadeaco, belasticidadeconc, ci, ti, armadura, secaobruta, inerciabruta, excentricidade, fletor
        # Access the username and email parameters sent from the frontend
        global deltaperc, p_it1, sigma_pit1
        e_scp = float(data.get('elasticidadeaco1'))
        e_ccp = float(data.get('elasticidadeconc1'))
        p_it0 = float(data.get('ci1'))
        sigma_pit0 = float(data.get('ti1'))
        a_c = float(data.get('secaobruta1'))
        i_c = float(data.get('inerciabruta1'))
        m_gpp = float(data.get('fletor1'))
        e_p = float(data.get('excentricidade1'))
        a_slcp = float(data.get('armadura1'))

        deltaperc, p_it1, sigma_pit1 = perda_deformacao_imediata_concreto_pre_tracao(
            e_scp*1E3, e_ccp*1E3, p_it0, sigma_pit0*1E3, a_slcp*1E-4, a_c*1E-4, i_c*1E-8, e_p*1E-2, m_gpp)
    # resultMagnel()
        print(f"resultado: {deltaperc}")
        print(f"resultado: {p_it1}")
        print(f"resultado: {sigma_pit1}")

        # Perform any necessary backend processing with the received data
    elif request.method == 'GET':

        response_data = {
            'deltaperc': deltaperc,
            'p_it1': p_it1,
            'sigma_pit1': sigma_pit1,


        }
        print("response_data ", response_data)

   # return {
    #       'message': 'result',
     #       'resultado0' : resultado0,
      #      'resultado1' : resultado1,
       #     'resultado2' : resultado2,
        #    'resultado3' : resultado3

   # }
    return jsonify(response_data)


@app.route('/ancoragem', methods=['POST', 'GET'])
def handle_user_data2():
    global response_data
    if request.method == 'POST':
        # Get the data from the JSON body of the request
        data = request.get_json()
        # Access the username and email parameters sent from the frontend
        global a_slcp, p_it0, sigma_pit0, l_0, Delta_anc, e_scp
        global deltaperc, p_it1, sigma_pit1
        p_it0 = float(data.get('ci_prot1'))
        sigma_pit0 = float(data.get('ti_prot1'))
        a_slcp = float(data.get('arma_prot1'))
        l_0 = float(data.get('comp_armadura1'))
        Delta_anc = float(data.get('deslizamento1'))
        e_scp = float(data.get('melasticidade1'))

        deltaperc, p_it1, sigma_pit1 = perda_deslizamento_ancoragem(
            # resultMagnel()
            p_it0, sigma_pit0*1E3, a_slcp*1E-4, l_0, Delta_anc*1E-3, e_scp*1E3)
        print(f"resultado: {deltaperc}")
        print(f"resultado: {p_it1}")
        print(f"resultado: {sigma_pit1}")

        # Perform any necessary backend processing with the received data
    elif request.method == 'GET':

        response_data = {
            'deltaperc': deltaperc,
            'p_it1': p_it1,
            'sigma_pit1': sigma_pit1,


        }
        print("response_data ", response_data)

   # return {
    #       'message': 'result',
     #       'resultado0' : resultado0,
      #      'resultado1' : resultado1,
       #     'resultado2' : resultado2,
        #    'resultado3' : resultado3

   # }
    return jsonify(response_data)


@app.route('/concreto', methods=['POST', 'GET'])
def handle_user_data3():
    global response_data
    if request.method == 'POST':
        # Get the data from the JSON body of the request
        data = request.get_json()
        # Access the username and email parameters sent from the frontend
        global a_slcp, p_it0, sigma_pit0, l_0, Delta_anc, e_scp, u, abat, a_c, mu_ar, t_0, t_1, temp
        global deltaperc, p_it1, sigma_pit1, eps_cs
        p_it0 = float(data.get('cargain1'))
        sigma_pit0 = float(data.get('tensinit1'))
        u = float(data.get('totalarmadura1'))
        abat = float(data.get('umidade1'))
        a_c = float(data.get('slump1'))
        mu_ar = float(data.get('areabruta1'))
        t_0 = float(data.get('perimex1'))
        t_1 = float(data.get('tempin1'))
        temp = float(data.get('temp1'))
        e_scp = float(data.get('young1'))

        eps_cs, deltaperc, p_it1, sigma_pit1 = perda_retracao_concreto(
            p_it0, sigma_pit0*1E3, a_slcp*1E-4, u, abat*1E-2, a_c*1E-4, mu_ar*1E-2, t_0, t_1, temp, e_scp*1E3)
        print(f"resultado: {deltaperc}")
        print(f"resultado: {p_it1}")
        print(f"resultado: {sigma_pit1}")

        # Perform any necessary backend processing with the received data
    elif request.method == 'GET':

        response_data = {
            'deltaperc': deltaperc,
            'p_it1': p_it1,
            'sigma_pit1': sigma_pit1,
            'eps_cs': eps_cs


        }
        print("response_data ", response_data)

   # return {
    #       'message': 'result',
     #       'resultado0' : resultado0,
      #      'resultado1' : resultado1,
       #     'resultado2' : resultado2,
        #    'resultado3' : resultado3

   # }
    return jsonify(response_data)


def save_figure_temp(fig):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    fig.savefig(temp_file.name)
    temp_file.close()
    return temp_file.name


@app.route('/tensaoelastica', methods=['POST', 'GET'])
def handle_user_data4():
    global response_data
    if request.method == 'POST':
        # Get the data from the JSON body of the request
        data = request.get_json()
        # Access the username and email parameters sent from the frontend
        global a_c, i_c, y_t, y_b, e_p, p_id, m_sd
        global sigma_t, sigma_b
        a_c = float(data.get('viga1'))
        i_c = float(data.get('iviga1'))
        y_t = float(data.get('distanciatopo1'))
        y_b = float(data.get('distancia1'))
        e_p = float(data.get('excentricidade1'))
        p_id = float(data.get('protensao1'))
        m_sd = float(data.get('fletor1'))

        print(f" teste a_c: {a_c}")

        sigma_t, sigma_b = tensao_topo_base(
            a_c*1E-4, i_c*1E-8, y_t*1E-2, y_b*1E-2, e_p*1E-2, p_id, m_sd)
        print(f"resultado: {sigma_t}")
        print(f"resultado: {sigma_b}")

        # Perform any necessary backend processing with the received data
    elif request.method == 'GET':

        response_data = {
            'sigma_t1': sigma_t,
            'sigma_b1': sigma_b,

        }
        print("response_data ", response_data)

   # return {
    #       'message': 'result',
     #       'resultado0' : resultado0,
      #      'resultado1' : resultado1,
       #     'resultado2' : resultado2,
        #    'resultado3' : resultado3

   # }
    return jsonify(response_data)


@app.route('/tensaoelasticavao', methods=['POST', 'GET'])
def handle_user_data5():

    global response_data
    if request.method == 'POST':
        global a_c, i_c, y_t, y_b, p_id, m_sd, df,  e_p
        global sigma_t_vazio, sigma_b_vazio, sigma_t_serv, sigma_b_serv

        # Recebe os dados do formulário
        viga1 = request.form.get('viga1')
        iviga1 = request.form.get('iviga1')
        distanciatopo1 = request.form.get('distanciatopo1')
        distancia1 = request.form.get('distancia1')
        a_c = float(viga1)
        i_c = float(iviga1)
        y_t = float(distanciatopo1)
        y_b = float(distancia1)
        print(viga1)
        print(iviga1)
        print(distanciatopo1)
        print(distancia1)

        # Recebe o arquivo
        file = request.files.get('arq1')
        if file:
            df = pd.read_excel(file)  # Lê o arquivo Excel
            print(df)  # Exibe o DataFrame no console para depuração
        sigma_t_vazio, sigma_b_vazio, sigma_t_serv, sigma_b_serv = tensoes_vao_completo(
            df, a_c*1E-4, i_c*1E-8, y_t*1E-2, y_b*1E-2)

        # Processa os dados e retorna a resposta

        # Perform any necessary backend processing with the received data
    elif request.method == 'GET':

        response_data = {
            'sigma_t_vazio1': sigma_t_vazio,
            'sigma_b_vazio1': sigma_b_vazio,
            'sigma_t_serv1': sigma_t_serv,
            'sigma_b_serv1': sigma_b_serv,

        }

    return jsonify(response_data)


@app.route('/armadura', methods=['POST', 'GET'])
def handle_user_data6():
    global response_data
    if request.method == 'POST':
        # Get the data from the JSON body of the request
        data = request.get_json()
        # Access the username and email parameters sent from the frontend
        global p_it0, sigma_pit0, t_0, t_1, temp, f_pk, a_slcp, tipo_aco, tipo_armadura, e_p
        global deltaperc, p_it1, sigma_pit1, psi, psi_1000
        p_it0 = float(data.get('protensao1'))
        sigma_pit0 = float(data.get('ti1'))
        t_0 = float(data.get('sdias1'))
        t_1 = float(data.get('tempof1'))
        temp = float(data.get('tempproj1'))
        f_pk = float(data.get('tensao1'))
        a_slcp = float(data.get('fletor1'))
        tipo_armadura = (data.get('tipoarm1'))
        tipo_aco = (data.get('tipaco1'))

        deltaperc, p_it1, sigma_pit1, psi, psi_1000 = perda_relax_armadura(
            p_it0, sigma_pit0*1E3, t_0, t_1, temp, f_pk*1E3, a_slcp*1E-4, tipo_armadura, tipo_aco)
        # Perform any necessary backend processing with the received data
    elif request.method == 'GET':

        response_data = {
            'deltaperc1': deltaperc,
            'sigma_pit11': sigma_pit1,
            'p_it11': p_it1,
            'psi1': psi,
            'psi_10001': psi_1000,

        }
        print("response_data ", response_data)

   # return {
    #       'message': 'result',
     #       'resultado0' : resultado0,
      #      'resultado1' : resultado1,
       #     'resultado2' : resultado2,
        #    'resultado3' : resultado3

   # }
    return jsonify(response_data)


@app.route('/fluencia', methods=['POST', 'GET'])
def handle_user_data7():
    global response_data
    if request.method == 'POST':
        # Get the data from the JSON body of the request
        data = request.get_json()
        # Access the username and email parameters sent from the frontend
        global p_it0, sigma_pit0, a_c, t_1, mu_ar, abatimento, a_slcp, umidade, tipo_endurecimento, t_0, e_scp, e_ccpt1, sigma_cabo, f_ck0, f_ck, temp
        global deltaperc, p_it1, sigma_pit1, psi, phi
        p_it0 = float(data.get('protensao1'))
        sigma_pit0 = float(data.get('ti1'))
        a_slcp = float(data.get('armprot1'))
        a_c = float(data.get('areabruta1'))
        mu_ar = float(data.get('ar1'))
        abatimento = float(data.get('slump1'))
        umidade = float(data.get('umidade1'))
        tipo_endurecimento = (data.get('endurecimento1'))
        t_0 = float(data.get('correcaotemp1'))
        t_1 = float(data.get('correcaotemp1'))
        temp = float(data.get('tempproj1'))
        e_scp = float(data.get('young1'))
        e_ccpt1 = float(data.get('young281'))
        sigma_cabo = float(data.get('tensaoarm1'))
        f_ck0 = float(data.get('resistencia1'))
        f_ck = float(data.get('resistencia281'))

        phi, deltaperc, p_it1, sigma_pit1 = perda_fluencia_concreto(p_it0, sigma_pit0*1E3, a_slcp*1E-4, a_c*1E-4, mu_ar*1E-2, abatimento*1E-2, umidade, tipo_endurecimento,
                                                                    # Perform any necessary backend processing with the received data
                                                                    temp, e_scp*1E3, e_ccpt1*1E3, sigma_cabo*1E3, t_0, t_1, f_ck0*1E3, f_ck*1E3)
    elif request.method == 'GET':

        response_data = {
            'deltaperc1': deltaperc,
            'sigma_pit11': sigma_pit1,
            'p_it11': p_it1,
            'phi1': phi,

        }
        print("response_data fluencia", response_data)

   # return {
    #       'message': 'result',
     #       'resultado0' : resultado0,
      #      'resultado1' : resultado1,
       #     'resultado2' : resultado2,
        #    'resultado3' : resultado3

   # }
    return jsonify(response_data)


def perda_fluencia_concreto(p_it0, sigma_pit0, a_slcp, a_c, mu_ar, abatimento, umidade, tipo_endurecimento, temp, e_scp, e_ccpt1, sigma_cabo, t_0, t_1, f_ck0, f_ck):
    """Esta função determina a perda de protensão devido ao efeito de fluência.

    Args:
        p_it0 (Float): Carga inicial de protensão (kN)
        sigma_pit0 (Float): Tensão inicial de protensão (kPa)
        a_slcp (Float): Área total de armadura protendida (m2)
        a_c (Float): Área bruta da seção (m2)
        mu_ar (Float): Parte do perímetro externo da seção em contato com ar (m)
        abatimento (Float): Abatimento ou slump test do concreto (m)
        umidade (Float): Umidade do ambiente no intervalo de tempo de análise (%)
        tipo_endurecimento (String):  Tipo da perda que deseja-se calcular a correção do tempo: 'LENTO' = Endurecimento lento AF250, AF320, POZ250, 'NORMAL' = Endurecimento normal CP250, CP320, CP400, 'RÁPIDO' = Endurecimento rápido aderência
        temp (Float): temperatura de projeto (°C)
        e_scp (Float): Módulo de elasticidade do aço protendido (kPa)
        e_ccpt1 (Float): Módulo de deformação tangente do concreto na idade t1 (kPa)
        sigma_cabo (Float): Tensões no nível dos cabos (kPa)
        t_0 (Float): tempo inicial de análise sem correção da temperatura (dias)
        t_1 (Float): tempo final de análise sem correção da temperatura (dias)
        f_ck0 (Float): Resistência característica à compressão na idade t0 (kPa)
        f_ck (Float): Resistência característica à compressão aos 28 dias (kPa)

    Returns:
        phi (Float): Fator de fluência total
        deltaperc (Float): Perda percentual de protensão (%)
        p_it1 (Float): Carga final de protensão (kN)
        sigma_pit1 (Float): Tensão final de protensão após a perda (kPa)
    """

    # Coeficiente de fluência rápida irreversível
    relacao_fck = f_ck0 / f_ck
    f_ck /= 1E3
    if f_ck <= 45:
        phi_a = 0.80 * (1 - relacao_fck)
    elif f_ck > 45:
        phi_a = 1.40 * (1 - relacao_fck)
    f_ck *= 1E3

    # Coeficiente de fluência lenta irreversível
    phi_1c = 1.00 * (4.45 - 0.035 * umidade)
    # intervalo 0.05 <= abatimento <= 0.09
    if umidade <= 90 and ((abatimento >= 0.05 and abatimento <= 0.09)):
        phi_1c *= 1.00
    # intervalo 0.00 <= abatimento <= 0.04
    elif umidade <= 90 and ((abatimento >= 0.00 and abatimento <= 0.04)):
        phi_1c *= 0.75
    # intervalo 10.0 <= abatimento <= 15.0
    elif umidade <= 90 and ((abatimento >= 0.10 and abatimento <= 0.15)):
        phi_1c *= 1.25
    h_fic = calculo_h_ficticio(umidade, a_c, mu_ar)
    phi_2c = (0.42 + h_fic) / (0.20 + h_fic)
    f_ck /= 1E3
    if f_ck <= 45:
        phi_finf = phi_1c * phi_2c
    elif f_ck > 45:
        phi_finf = 0.45 * phi_1c * phi_2c
    f_ck *= 1E3

    # Coeficiente de fluência lenta reversível
    phi_dinf = 0.40

    # Coeficiente de fluência lenta reversível
    beta_d = (t_1 - t_0 + 20) / (t_1 - t_0 + 70)

    # Coeficiente de fluência lenta irreversível
    t_0fic = calculo_tempo_ficticio(t_0, temp, 'FLUÊNCIA', tipo_endurecimento)
    beta_f0, _, _, _, _ = betaf_fluencia(t_0fic, h_fic)

    t_1fic = calculo_tempo_ficticio(t_1, temp, 'FLUÊNCIA', tipo_endurecimento)
    beta_f1, _, _, _, _ = betaf_fluencia(t_1fic, h_fic)

    # Coeficiente de fluência total
    phi = phi_a + phi_finf * (beta_f1 - beta_f0) + phi_dinf * beta_d

    # Perdas de protensão
    epsilon_cs = sigma_cabo / e_ccpt1 * phi
    deltasigma = e_scp * epsilon_cs
    sigma_pit1 = sigma_pit0 - deltasigma
    deltap = deltasigma * a_slcp
    p_it1 = p_it0 - deltap
    deltaperc = (deltap / p_it0) * 100

    return phi, deltaperc, p_it1, sigma_pit1


def betaf_fluencia(t_fic, h_fic):
    """Esta função determina o coeficiente de retração β_F.

    Args:
        t_fic (Float): tempo de projeto corrigido em função da temperatura (dias)
        h_fic (Float): altura fictícia da peça para cálculo de fluência e retração (m)

    Returns:
        beta_f (Float): Coeficiente de fluência
        a (Float): Coeficiente A
        b (Float): Coeficiente B
        c (Float): Coeficiente C
        d (Float): Coeficiente D
    """

    # Coeficientes A até E
    a = 42 * pow(h_fic, 3) - 350 * pow(h_fic, 2) + 588 * h_fic + 113
    b = 768 * pow(h_fic, 3) - 3060 * pow(h_fic, 2) + 3234 * h_fic - 23
    c = -200 * pow(h_fic, 3) + 13 * pow(h_fic, 2) + 1090 * h_fic + 183
    d = 7579 * pow(h_fic, 3) - 31916 * pow(h_fic, 2) + 35343 * h_fic + 1931

    # Determinação do BETA_F
    aux_0 = pow(t_fic, 2) + a * t_fic + b
    aux_1 = pow(t_fic, 2) + c * t_fic + d
    beta_f = aux_0 / aux_1

    return beta_f, a, b, c, d


def perda_relax_armadura(p_it0, sigma_pit0, t_0, t_1, temp, f_pk, a_slcp, tipo_arm, tipo_aco):
    """Esta função determina a perda de protensão por relaxação da armadura de protensão em peças de concreto protendido.

    Args:
        p_it0 (Float): Carga inicial de protensão (kN)
        sigma_pit0 (Float): Tensão inicial de protensão (kPa)
        t_0 (Float): tempo inicial de análise sem correção da temperatura (dias)
        t_1 (Float): tempo final de análise sem correção da temperatura (dias)
        temp (Float): temperatura de projeto (°C)
        f_pk (Float): Tensão última do aço (kPa)
        a_slcp (Float): Área total de armadura protendida (m2)
        tipo_arm (String): Tipo de armadura: 'FIO' = Fio, 'COR' = Cordoalha, 'BAR' = Barra
        tipo_aco (String): Tipo de aço: 'RN' = Relaxação normal, 'RB' = Relaxação baixa

    Returns:
        deltaperc (Float): Perda percentual de protensão (%)
        p_it1 (Float): Carga final de protensão (kN)
        sigma_pit1 (Float): Tensão final de protensão (kPa)
        psi (Float): Coeficiente de relaxação do aço (%)
        psi_1000 (Float): Valor médio da relaxação, medidos após 1.000 h, à temperatura constante de 20 °C (%)
    """

    # Determinação Ψ_1000
    rho_sigma = sigma_pit0 / f_pk
    psi_1000 = tabela_psi1000(tipo_arm, tipo_aco, rho_sigma)
    print("valor de psi1000", psi_1000)
    # Determinação do psi no intervalo de tempo t_1 - t_0
    temp_corrigida = (t_1 - t_0) * temp / 20
    if t_1 > (49 * 365):
        psi = 2.50 * psi_1000
    else:
        psi = psi_1000 * (temp_corrigida / 41.67) ** 0.15

    # Perdas de protensão
    deltasigma = (psi / 100) * sigma_pit0
    sigma_pit1 = sigma_pit0 - deltasigma
    deltap = deltasigma * a_slcp
    p_it1 = p_it0 - deltap
    deltaperc = (deltap / p_it0) * 100

    return deltaperc, p_it1, sigma_pit1, psi, psi_1000


def tabela_psi1000(tipo_arm, tipo_aco, rho_sigma):
    """Esta função encontra o fator Ψ_1000 para cálculo da relaxação.

    Args:
        tipo_arm (String): Tipo de armadura: 'FIO' = Fio, 'COR' = Cordoalha, 'BAR' = Barra
        tipo_aco (String): Tipo de aço: 'RN' = Relaxação normal, 'RB' = Relaxação baixa
        rho_sigma (Float): Razão entre f_pk e sigma_pi na data escolhida

    Returns:
        psi_1000 (Float): Valor médio da relaxação, medidos após 1.000 h, à temperatura constante de 20 °C (%)   
    """

    # Cordoalhas
    if tipo_arm == 'COR':
        if tipo_aco == 'RN':
            if rho_sigma <= 0.5:
                psi_1000 = 0
            elif 0.5 < rho_sigma and rho_sigma <= 0.6:
                y_0 = 0.00
                y_1 = 3.50
                x_0 = 0.50
                x_1 = 0.60
                x_k = rho_sigma
                psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
            elif 0.6 < rho_sigma and rho_sigma <= 0.7:
                y_0 = 3.50
                y_1 = 7.00
                x_0 = 0.60
                x_1 = 0.70
                x_k = rho_sigma
                psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
            elif 0.7 < rho_sigma and rho_sigma <= 0.8:
                y_0 = 7.00
                y_1 = 12.00
                x_0 = 0.70
                x_1 = 0.80
                x_k = rho_sigma
                psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
            elif rho_sigma > 0.80:
                psi_1000 = 12.00
        elif tipo_aco == 'RB':
            if rho_sigma <= 0.5:
                psi_1000 = 0
            elif 0.5 < rho_sigma and rho_sigma <= 0.6:
                y_0 = 0.00
                y_1 = 1.30
                x_0 = 0.50
                x_1 = 0.60
                x_k = rho_sigma
                psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
            elif 0.6 < rho_sigma and rho_sigma <= 0.7:
                y_0 = 1.30
                y_1 = 2.50
                x_0 = 0.60
                x_1 = 0.70
                x_k = rho_sigma
                psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
            elif 0.7 < rho_sigma and rho_sigma <= 0.8:
                y_0 = 2.50
                y_1 = 3.50
                x_0 = 0.70
                x_1 = 0.80
                x_k = rho_sigma
                psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
            elif rho_sigma > 0.8:
                psi_1000 = 3.50
    # Fio
    elif tipo_arm == 'FIO':
        if tipo_aco == 'RN':
            if rho_sigma <= 0.5:
                psi_1000 = 0
            elif 0.5 < rho_sigma and rho_sigma <= 0.6:
                y_0 = 0.00
                y_1 = 2.50
                x_0 = 0.50
                x_1 = 0.60
                x_k = rho_sigma
                psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
            elif 0.6 < rho_sigma and rho_sigma <= 0.7:
                y_0 = 2.50
                y_1 = 5.00
                x_0 = 0.60
                x_1 = 0.70
                x_k = rho_sigma
                psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
            elif 0.7 < rho_sigma and rho_sigma <= 0.8:
                y_0 = 5.00
                y_1 = 8.50
                x_0 = 0.70
                x_1 = 0.80
                x_k = rho_sigma
                psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
            elif rho_sigma > 0.8:
                psi_1000 = 8.50
        elif tipo_aco == 'RB':
            if rho_sigma <= 0.5:
                psi_1000 = 0
            elif 0.5 < rho_sigma and rho_sigma <= 0.6:
                y_0 = 0.00
                y_1 = 1.00
                x_0 = 0.50
                x_1 = 0.60
                x_k = rho_sigma
                psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
            elif 0.6 < rho_sigma and rho_sigma <= 0.7:
                y_0 = 1.00
                y_1 = 2.00
                x_0 = 0.60
                x_1 = 0.70
                x_k = rho_sigma
                psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
            elif 0.7 < rho_sigma and rho_sigma <= 0.8:
                y_0 = 2.00
                y_1 = 3.00
                x_0 = 0.70
                x_1 = 0.80
                x_k = rho_sigma
                psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
            elif rho_sigma > 0.8:
                psi_1000 = 3.00
    # Barra
    elif tipo_arm == 'BAR':
        if rho_sigma <= 0.5:
            psi_1000 = 0
        elif 0.5 < rho_sigma and rho_sigma <= 0.6:
            y_0 = 0.00
            y_1 = 1.50
            x_0 = 0.50
            x_1 = 0.60
            x_k = rho_sigma
            psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
        elif 0.6 < rho_sigma and rho_sigma <= 0.7:
            y_0 = 1.50
            y_1 = 4.00
            x_0 = 0.60
            x_1 = 0.70
            x_k = rho_sigma
            psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
        elif 0.7 < rho_sigma and rho_sigma <= 0.8:
            y_0 = 4.00
            y_1 = 7.00
            x_0 = 0.70
            x_1 = 0.80
            x_k = rho_sigma
            psi_1000 = interpolador(x_0, x_1, x_k, y_0, y_1)
        elif rho_sigma > 0.8:
            psi_1000 = 7.00

    return psi_1000


def interpolador(x_1, x_2, x_k, y_1, y_2):
    """Esta função interpola linearmente valores.

    Args:
        x_1 (Float): Valor inferior x_k
        x_2 (Float): Valor superior x_k
        x_k (Float): Valor x de referência
        y_1 (Float): Valor inferior y_k
        y_2 (Float): Valor superior y_k

    Returns:
        y_k (Float): Valor interpolado y_k a partir de x_k
    """

    return y_1 + (x_k - x_1) * ((y_2 - y_1) / (x_2 - x_1))


def tensoes_vao_completo(df, a_c, i_c, y_t, y_b):
    """Determina as tensões de flexão no topo e na base da seção considerando a carga p_sd e protensão e uma combinação de momentos m_sd em um vão completo de viga.

    Args:
        df (DataFrame): DataFrame com os dados da peça de concreto protendido:'
        a_c (Float): Área da seção transversal (m2)
        i_c (Float): Inércia da seção transversal (m4)
        y_t (Float): Distância do topo da seção até o centro de gravidade (m)
        y_b (Float): Distância da base da seção até o centro de gravidade (m)

    Returns:
        sigma_t_vazio (List): Tensão de flexão no topo da seção estado vazio (kPa)
        sigma_b_vazio (List): Tensão de flexão na base da seção estado vazio (kPa)
        sigma_t_serv (List): Tensão de flexão no topo da seção estado serviço (kPa)
        sigma_b_serv (List): Tensão de flexão na base da seção estado serviço (kPa)
        fig (Figure): Figura com o diagrama de tensões
    """

    sigma_b_vazio = []
    sigma_t_vazio = []
    sigma_b_serv = []
    sigma_t_serv = []
    for i in range(len(df)):
        topo_vazio, base_vazio, _ = tensao_topo_base(
            a_c, i_c, y_t, y_b, df['e_p (cm)'][i]*1E-2, df['p_Sd t=0 (kN)'][i], df['m_Sd,gpp (kNm)'][i])
        sigma_t_vazio.append(topo_vazio)
        sigma_b_vazio.append(base_vazio)
        topo_serv, base_serv, _ = tensao_topo_base(
            a_c, i_c, y_t, y_b, df['e_p (cm)'][i]*1E-2, df['p_Sd t=∞ (kN)'][i], df['m_Sd,gpp (kNm)'][i]+df['m_Sd,gext (kNm)'][i]+df['m_Sd,q (kNm)'][i])
        sigma_t_serv.append(topo_serv)
        sigma_b_serv.append(base_serv)

    # Grafico 1 - ATO
    fig, (ax1, ax2) = plt.subplots(
        2, 1, sharex=True, sharey=True, figsize=(8, 10))
    ax1.plot(df['x (cm)'], sigma_t_vazio,
             color='blue', linestyle='-', linewidth=2)
    ax1.plot(df['x (cm)'], sigma_b_vazio,
             color='red', linestyle='-', linewidth=2)
    ax1.set_title('Tensões na seção transversal - Estado Vazio', size=14)
    ax1.set_ylabel('Tensão (kPa)')
    ax1.legend(['Topo', 'Base', 'Limite tração', 'Limite compressão'])
    ax1.grid(True)

    # Grafico 2 - SERV
    ax2.plot(df['x (cm)'], sigma_t_serv,
             color='blue', linestyle='-', linewidth=2)
    ax2.plot(df['x (cm)'], sigma_b_serv,
             color='red', linestyle='-', linewidth=2)
    ax2.set_title('Tensões na seção transversal - Estado Serviço', size=14)
    ax2.set_xlabel('Distância (cm)')
    ax2.set_ylabel('Tensão (kPa)')
    ax2.legend(['Topo', 'Base'])
    ax2.grid(True)
    fig.savefig("./cliente/src/pages/teste1.png", dpi=300, bbox_inches='tight')
    fig.show
    return sigma_t_vazio, sigma_b_vazio, sigma_t_serv, sigma_b_serv


def tensao_topo_base(a_c, i_c, y_t, y_b, e_p, p_sd, m_sd):
    """Determina a tensão de flexão no topo e na base da seção considerando a carga p_sd e protensão e uma combinação de momentos m_sd.

    Args:
        a_c (Float): Área da seção transversal (m2)
        i_c (Float): Inércia da seção transversal (m4)
        y_t (Float): Distância do topo da seção até o centro de gravidade (m)
        y_b (Float): Distância da base da seção até o centro de gravidade (m)
        e_p (Float): Excentricidade de protensão (m)
        p_sd (Float): Valor da protensão de cálculo na seção (kN)
        m_sd (Float): Momento fletor de cálculo (kNm)

    Returns:
        sigma_t (Float): Tensão de flexão no topo da seção (kPa)
        sigma_b (Float): Tensão de flexão na base da seção (kPa)
        fig (Figure): Figura com o diagrama de tensões
    """

    # Calculando os módulos plásticos
    w_t = i_c / y_t
    w_b = i_c / y_b

    # Determinação das tensões na base e no topo
    sigma_ms_b, sigma_ms_t = tensao_momento(w_t, w_b, m_sd)
    sigma_pi_b, sigma_pi_t = tensao_protensao(a_c, w_t, w_b, e_p, p_sd)
    sigma_b = sigma_ms_b + sigma_pi_b
    sigma_t = sigma_ms_t + sigma_pi_t

    # Desenho do diagrama de tensões
    def regra1(sigma_b, sigma_t):
        escala = (100 * abs(sigma_t)) / max(abs(sigma_t), abs(sigma_b))
        if sigma_t >= 0:
            x = 250 + escala
            y = (y_b + y_t) * 100
        elif sigma_t < 0:
            x = 250 - escala
            y = (y_b + y_t) * 100

        return x, y

    def regra2(sigma_b, sigma_t):
        escala = (100 * abs(sigma_b)) / max(abs(sigma_t), abs(sigma_b))
        if sigma_b >= 0:
            x = 250 + escala
            y = 0
        elif sigma_b < 0:
            x = 250 - escala
            y = 0

        return x, y

    x1, y1 = regra1(sigma_b, sigma_t)
    x2, y2 = regra2(sigma_b, sigma_t)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([x1, x2], [y1, y2], color='#03AED2', linestyle='-', linewidth=2)
    ax.plot([x2, 250], [y2, y2], color='#03AED2', linestyle='-', linewidth=2)
    ax.plot([x1, 250], [y1, y1], color='#03AED2', linestyle='-', linewidth=2)
    ax.fill([250, 250, x1, x2, 250], [0, ((y_t + y_b)*100), y1, y2, 0],
            color='#C7C7C7', linestyle='-', linewidth=2)
    ax.tick_params(axis='both', which='both', bottom=False, top=False,
                   left=False, right=False, labelbottom=False, labelleft=False)
    ax.set_xlim(-10, 420)
    ax.set_title('Tensões na seção transversal', size=16)
    ax.text(-5, (y_t + y_b) * 100,
            f'$\sigma_t=${sigma_t:.2f} kPa', ha='left', va='center', size=14)
    ax.text(-5, 0, f'$\sigma_b=${sigma_b:.2f} kPa',
            ha='left', va='center', size=14)

    fig.savefig("/Users/lilianevale/Documents/UFG/react/Tutorial-Project/client/src/pages/teste.png",
                dpi=300, bbox_inches='tight')
    fig.show

    return sigma_t, sigma_b


def tensao_momento(w_t, w_b, m_s):
    """Determina a tensão de flexão devido a momento fletor informado.

    Args:
        w_t (Float): Módulo plástico do topo da seção (m3)
        w_b (Float): Módulo plástico da base da seção (m3)
        delta (Booleaneano): Condição de existência da tensão na idade analisada
        m_s (Float): Momento fletor na seção (kN.m)     

    Returns:
        sigma_b_ms (Float): Tensão de flexão na base devido ao momento fletor (kPa)
        sigma_t_ms (Float): Tensão de flexão no topo devido ao momento fletor (kPa)
    """

    # Calculando as tensões
    sigma_b_ms = -m_s / w_b
    sigma_t_ms = m_s / w_t

    return sigma_b_ms, sigma_t_ms


def tensao_protensao(a_c, w_t, w_b, e_p, p_id):
    """Determina a tensão devido a protensão informada.

    Args:
        a_c (Float): Área da seção transversal (m2)
        w_t (Float): Módulo plástico do topo da seção (m3)
        w_b (Float): Módulo plástico da base da seção (m3)
        e_p (Float): Excentricidade de protensão (m)
        p_id (Float): Valor da protensão na seção (kN)

    Returns:
        sigma_b_mp (Float): Tensão de flexão na base devido a protensão (kPa)
        sigma_t_mp (Float): Tensão de flexão no topo devido a protensão (kPa)
    """

    # Calculando as tensões
    p_0 = p_id / a_c
    m_pi = p_id * e_p
    sigma_b_mp = p_0 + m_pi / w_b
    sigma_t_mp = p_0 - m_pi / w_t

    return sigma_b_mp, sigma_t_mp


def perda_retracao_concreto(p_it0, sigma_pit0, a_slcp, umidade, abatimento, a_c, mu_ar, t_0, t_1, temp, e_scp):
    """Esta função determina a perda de protensão devido a retração do concreto. 

    Args:
        p_it0 (Float): Carga inicial de protensão (kN)
        sigma_pit0 (Float): Tensão inicial de protensão (kPa)
        a_slcp (Float): Área total de armadura protendida (m2)
        umidade (Float): Umidade do ambiente no intervalo de tempo de análise (%)
        abatimento (Float): Abatimento ou slump test do concreto (m)
        a_c (Float): Área bruta da seção (m2)
        mu_ar (Float): Parte do perímetro externo da seção em contato com ar (m)
        t_0 (Float): tempo inicial de análise sem correção da temperatura (dias)
        t_1 (Float): tempo final de análise sem correção da temperatura (dias)
        temp (Float): temperatura de projeto (°C)
        e_scp (Float): Módulo de elasticidade do aço protendido (kPa)

    Returns:
        epsilon_cs (Float): Valor final da deformação por retração
        deltaperc (Float): Perda percentual de protensão (%)
        p_it1 (Float): Carga final de protensão (kN)
        sigma_pit1 (Float): Tensão final de protensão após a perda (kPa)
    """

    # Cálculo da deformação específica epsilon_1s
    epsilon_1s = -8.09 + (umidade / 15) - (umidade ** 2 / 2284) - \
        (umidade ** 3 / 133765) + (umidade ** 4 / 7608150)
    epsilon_1s /= -1E4
    # intervalo 0.05 <= abatimento <= 0.09
    if umidade <= 90 and ((abatimento >= 0.05 and abatimento <= 0.09)):
        epsilon_1s *= 1.00
    # intervalo 0.00 <= abatimento <= 0.04
    elif umidade <= 90 and ((abatimento >= 0.00 and abatimento <= 0.04)):
        epsilon_1s *= 0.75
    # intervalo 10.0 <= abatimento <= 15.0
    elif umidade <= 90 and ((abatimento >= 0.10 and abatimento <= 0.15)):
        epsilon_1s *= 1.25

    # Cálculo da defomração específica epsilon_2s
    h_fic = calculo_h_ficticio(umidade, a_c, mu_ar)
    epsilon_2s = (0.33 + 2 * h_fic) / (0.208 + 3 * h_fic)

    # Coeficiente beta_s T0
    t_0fic = calculo_tempo_ficticio(t_0, temp, 'RETRAÇÃO', None)
    beta_st0, _, _, _, _, _ = betas_retracao(t_0fic, h_fic)

    # Coeficiente beta_s T1
    t_1fic = calculo_tempo_ficticio(t_1, temp, 'RETRAÇÃO', None)
    beta_st1, _, _, _, _, _ = betas_retracao(t_1fic, h_fic)

    # Valor final da deformação por retração epsilon_cs
    epsilon_cs = epsilon_1s * epsilon_2s * (beta_st1 - beta_st0)

    # Perdas de protensão
    deltasigma = e_scp * epsilon_cs
    sigma_pit1 = sigma_pit0 - deltasigma
    deltap = deltasigma * a_slcp
    p_it1 = p_it0 - deltap
    deltaperc = (deltap / p_it0) * 100

    return epsilon_cs, deltaperc, p_it1, sigma_pit1


def betas_retracao(t_fic, h_fic):
    """Esta função determina o coeficiente de retração β_S.

    Args:
        t_fic (Float): tempo de projeto corrigido em função da temperatura (dias)
        h_fic (Float): altura fictícia da peça para cálculo de fluência e retração (m)

    Returns:
        beta_s (Float): Coeficiente de retração
        a (Float): Coeficiente A
        b (Float): Coeficiente B
        c (Float): Coeficiente C
        d (Float): Coeficiente D
        e (Float): Coeficiente E
    """

    # Coeficientes A até E
    a = 40
    b = 116 * pow(h_fic, 3) - 282 * pow(h_fic, 2) + 220 * h_fic - 4.8
    c = 2.5 * pow(h_fic, 3) - 8.8 * h_fic + 40.7
    d = -75 * pow(h_fic, 3) + 585 * pow(h_fic, 2) + 496 * h_fic - 6.8
    e = -169 * pow(h_fic, 4) + 88 * pow(h_fic, 3) + \
        584 * pow(h_fic, 2) - 39 * h_fic + 0.8
    t_fic100 = t_fic / 100

    # Determinação do beta_s
    aux_0 = pow(t_fic100, 3) + a * pow(t_fic100, 2) + b * t_fic100
    aux_1 = pow(t_fic100, 3) + c * pow(t_fic100, 2) + d * t_fic100 + e
    beta_s = aux_0 / aux_1

    return beta_s, a, b, c, d, e


def calculo_tempo_ficticio(delta_tempo, temperatura, tipo_perda, tipo_endurecimento):
    """Esta função calcula o tempo corrigido para cálculo das perdas de fluência e retração. 

    Args:
        tempo (Float): tempo para análise da correção em função da temperatura (dias)
        temperatura (Float): temperatura de projeto (°C)
        tipo_perda (String): 'RETRAÇÃO' = Retração, 'FLUÊNCIA' = Fluência
        tipo_endurecimento (String):  Tipo da perda que deseja-se calcular a correção do tempo: 'LENTO' = Endurecimento lento AF250, AF320, POZ250, 'NORMAL' = Endurecimento normal CP250, CP320, CP400, 'RÁPIDO' = Endurecimento rápido aderência

    Returns:
        t_fic (Float): tempo de projeto corrigido em função da temperatura (°C)
    """

    # Parâmetros de reologia e tipo de pega
    if tipo_perda == 'RETRAÇÃO':
        alpha = 1
    elif tipo_perda == 'FLUÊNCIA':
        if tipo_endurecimento == 'LENTO':
            alpha = 1
        elif tipo_endurecimento == 'NORMAL':
            alpha = 2
        elif tipo_endurecimento == 'RÁPIDO':
            alpha = 3

    # Determinação da idade fictícia do concreto
    t_fic = alpha * ((temperatura + 10) / 30) * delta_tempo

    # Correção dos tempos menores que 3 dias e maiores que 10.000 dias
    if t_fic < 3 and t_fic > 0:
        t_fic = 3
    elif t_fic > 10000:
        t_fic = 10000

    return t_fic


def calculo_h_ficticio(umidade, a_c, mu_ar):
    """Esta função calcula a altura fictícia de uma peça de concreto.

    Args:
        umidade (Float): Umidade do ambiente no intervalo de tempo de análise (%)
        a_c (Float): Área bruta da seção (m2)
        mu_ar (Float): Parte do perímetro externo da seção em contato com ar (m)

    Returns:
        h_fic (Float): Altura fictícia da peça para cálculo de fluência e retração (m)
    """

    gamma = 1 + np.exp(-7.8 + 0.1 * umidade)
    h_fic = gamma * 2 * a_c / mu_ar
    if h_fic > 1.60:
        h_fic = 1.60
    if h_fic < 0.050:
        h_fic = 0.050

    return h_fic


def perda_deslizamento_ancoragem(p_it0, sigma_pit0, a_slcp, l_0, delta_anc, e_scp):
    """Esta função determina a perda de protensão por deslizamento da armadura na ancoragem.

    Args:
      p_it0 (Float): Carga inicial de protensão [kN]
      sigma_pit0 (Float): Tensão inicial de protensão [kPa]
      a_slcp (Float): Área total de armadura protendida [m2]
      l_0 (Float): Comprimento da pista de protensão [m]
      delta_anc (Float): Previsão do deslizamento do sistema de ancoragem [m]
      e_scp (Float): Módulo de elasticidade do aço protendido [kPa]

    Returns:
      deltaperc (Float): Perda percentual de protensão [%]
      p_it1 (Float): Carga final de protensão após a perda [kN]
      sigma_pit1 (Float): Tensão final de protensão após a perda [kPa]
    """

    # Pré-alongamento do cabo
    deltal_p = l_0 * (sigma_pit0 / e_scp)

    # Redução da deformação na armadura de protensão
    deltaepsilon_p = delta_anc / (l_0 + deltal_p)

    # Perdas de protensão
    deltasigma = e_scp * deltaepsilon_p
    sigma_pit1 = sigma_pit0 - deltasigma
    deltap = deltasigma * a_slcp
    p_it1 = p_it0 - deltap
    deltaperc = (deltap / p_it0) * 100

    return deltaperc, p_it1, sigma_pit1


def perda_deformacao_imediata_concreto_pre_tracao(e_scp, e_ccp, p_it0, sigma_pit0, a_slcp, a_c, i_c, e_p, m_gpp):
    """Esta função determina a perda de protensão devido a deformação inicial do concreto. 

    Args:
      e_scp (Float): Módulo de elasticidade do aço protendido [kPa]
      e_ccp (Float): Módulo de elasticidade do concreto [kPa]
      p_it0 (Float): Carga inicial de protensão [kN]
      sigma_pit0 (Float): Tensão inicial de protensão [kPa]
      a_slcp (Float): Área total de armadura protendida [m2]
      a_c (Float): Área bruta da seção [m2]
      i_c (Float): Inércia da seção bruta [m4]
      e_p (Float): Excentricidade do cabo de protensão [m]
      m_gpp (Float): Momento fletor devido ao peso próprio [kNm]

    Returns:
      deltaperc (Float): Perda percentual de protensão [%]
      p_it1 (Float): Carga final de protensão após a perda [kN]
      sigma_pit1 (Float): Tensão final de protensão após a perda [kPa]
    """

    # Tensões individuais das peças
    alpha_p = e_scp / e_ccp
    aux_0 = p_it0 / a_c
    aux_1 = (p_it0 * e_p ** 2) / i_c
    aux_2 = (m_gpp * e_p) / i_c

    # Perdas de protensão
    deltasigma = alpha_p * (aux_0 + aux_1 - aux_2)
    sigma_pit1 = sigma_pit0 - deltasigma
    deltap = deltasigma * a_slcp
    p_it1 = p_it0 - deltap
    deltaperc = (deltap / p_it0) * 100

    return deltaperc, p_it1, sigma_pit1


# Running app
if __name__ == '__main__':
    app.run(debug=True, port=5000)

   # a_c = 1500
   # y_t = 37.5
   # y_b = 37.5
   # i_c = 703125
   # sigma_max = 0.7*28.90
   # sigma_min = 0.0
    # m_sd_inicial = 22.97
   # eq0, eq1, eq2, eq3 = diagrama_magnel(a_c*1E-4, y_t*1E-2, y_b*1E-2, i_c*1E-8, sigma_max*1E3, sigma_min*1E3, m_sd_inicial)
