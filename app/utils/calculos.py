import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
import os
import uuid


def diagrama_magnel(a_c, y_t, y_b, i_c, sigma_max, sigma_min, m_sd_inicial):
    w_t = i_c / y_t
    w_b = i_c / y_b

    epsilon_b_max = sigma_max + m_sd_inicial / w_b
    epsilon_b_min = sigma_min + m_sd_inicial / w_b
    epsilon_t_max = sigma_max - m_sd_inicial / w_t
    epsilon_t_min = sigma_min - m_sd_inicial / w_t

    eq_0 = f'y >= ({1/a_c} + {1/w_b}·e_c) / {epsilon_b_max}'
    eq_1 = f'y <= ({1/a_c} + {1/w_b}·e_c) / {epsilon_b_min}'
    eq_2 = f'y >= ({1/a_c} - {1/w_t}·e_c) / {epsilon_t_max}'
    eq_3 = f'y <= ({1/a_c} - {1/w_t}·e_c) / {epsilon_t_min}'

    print("equação 0:", eq_0)
    print("equação 1:", eq_1)
    print("equação 2:", eq_2)
    print("equação 3:", eq_3)

    return eq_0, eq_1, eq_2, eq_3


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
    sigma_b_vazio = []
    sigma_t_vazio = []
    sigma_b_serv = []
    sigma_t_serv = []

    try:
        for i in range(len(df)):
            # Conversão das unidades da planilha (cm -> m)
            e_p = df['e_p (cm)'][i] * 1E-2
            p_sd_0 = df['p_Sd t=0 (kN)'][i]
            p_sd_inf = df['p_Sd t=∞ (kN)'][i]
            m_sd_0 = df['m_Sd,gpp (kNm)'][i]
            m_sd_total = (
                df['m_Sd,gpp (kNm)'][i]
                + df['m_Sd,gext (kNm)'][i]
                + df['m_Sd,q (kNm)'][i]
            )

            # Estado vazio
            topo_vazio, base_vazio, _ = tensao_topo_base(
                a_c, i_c, y_t, y_b, e_p, p_sd_0, m_sd_0
            )
            sigma_t_vazio.append(topo_vazio)
            sigma_b_vazio.append(base_vazio)

            # Estado serviço
            topo_serv, base_serv, _ = tensao_topo_base(
                a_c, i_c, y_t, y_b, e_p, p_sd_inf, m_sd_total
            )
            sigma_t_serv.append(topo_serv)
            sigma_b_serv.append(base_serv)

        # Geração do gráfico
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

        ax1.plot(df['x (cm)'], sigma_t_vazio, 'b-', label='Topo')
        ax1.plot(df['x (cm)'], sigma_b_vazio, 'r-', label='Base')
        ax1.set_title('Tensões - Estado Vazio')
        ax1.set_ylabel('Tensão (kPa)')
        ax1.grid(True)
        ax1.legend()

        ax2.plot(df['x (cm)'], sigma_t_serv, 'b-', label='Topo')
        ax2.plot(df['x (cm)'], sigma_b_serv, 'r-', label='Base')
        ax2.set_title('Tensões - Estado de Serviço')
        ax2.set_xlabel('Distância (cm)')
        ax2.set_ylabel('Tensão (kPa)')
        ax2.grid(True)
        ax2.legend()

        # Salvar imagem na pasta do projeto
        nome_arquivo = f"vao_{uuid.uuid4().hex[:8]}.png"
        pasta_destino = os.path.join("app", "static", "imagens")
        os.makedirs(pasta_destino, exist_ok=True)
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)
        fig.savefig(caminho_completo, dpi=300, bbox_inches='tight')
        plt.close(fig)

        imagem_url = f"/static/imagens/{nome_arquivo}"
        return sigma_t_vazio, sigma_b_vazio, sigma_t_serv, sigma_b_serv, imagem_url

    except Exception as e:
        print(f"[ERRO] Falha no cálculo das tensões no vão completo: {e}")
        return [], [], [], [], None


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

    nome_arquivo = f"tensao_{uuid.uuid4().hex[:8]}.png"
    pasta_destino = os.path.join("app", "static", "imagens")
    os.makedirs(pasta_destino, exist_ok=True)  # Garante que a pasta exista
    caminho_completo = os.path.join(pasta_destino, nome_arquivo)

    fig.savefig(caminho_completo, dpi=300, bbox_inches='tight')
    plt.close(fig)  # Libera memória

    # Retorna caminho relativo
    imagem_url = f"/static/imagens/{nome_arquivo}"
    return sigma_t, sigma_b, imagem_url


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
    print('Entrou aqui')
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
        else:
            alpha = 2

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
