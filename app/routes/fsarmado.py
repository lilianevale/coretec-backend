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

