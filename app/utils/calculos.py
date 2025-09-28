import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
import os
import uuid

def indice_spi(df_inmet):
    """Determina o Índice de Preciptação Padronizado (SPI) para um determinado DataFrame.
    
    Args:
        df (DataFrame): DataFrame com os dados de preciptação
    
    Returns:
        spi_df (DataFrame): DataFrame com os valores do SPI
    """

    # Limpeza dos dados
    df = df_inmet
    df_precip = df.drop(columns=['Unnamed: 2'])
    df_precip.columns = ['Data Medição', 'Precipitação Total Diária (mm)']
    df_precip['Precipitação Total Diária (mm)'] = df_precip['Precipitação Total Diária (mm)'].str.replace(',', '.').astype(float)
    df_precip['Data Medição'] = pd.to_datetime(df_precip['Data Medição'], format='%Y-%m-%d')
    df_precip['Precipitação Total Diária (mm)'] = pd.to_numeric(df_precip['Precipitação Total Diária (mm)'], errors='coerce')

    # Agrupar por mês e somar a precipitação diária para obter precipitação mensal
    df_precip['AnoMes'] = df_precip['Data Medição'].dt.to_period('M')  # Criar uma coluna com o ano e mês
    precip_mensal = df_precip.groupby('AnoMes')['Precipitação Total Diária (mm)'].sum()  # Soma a precipitação diária para obter mensal

    # Função para calcular o SPI considerando precipitação zero
   
    def calcular_spi(precipitacao_mensal):
        
        spi_mensal = []
        estatisticas = [] 

        # Iterar sobre os 12 meses do ano
        for mes in range(1, 13):
            # Filtrar os dados referentes a cada mês
            dados_mes = precipitacao_mensal[precipitacao_mensal.index.month == mes]
          
            # Calcular a média mensal
            media = np.mean(dados_mes)

            # Separar os valores de precipitação zero e positivos
            zeros = (dados_mes == 0).sum()
            positivos = dados_mes[dados_mes > 0]
            
            # Probabilidade de zeros
            prob_zeros = zeros / len(dados_mes)
            
            # Ajustar a distribuição gama aos valores positivos
            shape, loc, scale = gamma.fit(positivos, floc=0)
            cdf = gamma.cdf(dados_mes, shape, loc=loc, scale=scale)
            
            # Ajustar a CDF para lidar com zeros
            cdf_adjusted = prob_zeros + (1 - prob_zeros) * cdf
            
            # Convertendo a CDF ajustada para a distribuição normal padrão (SPI)
            spi_mes = norm.ppf(cdf_adjusted)
            
            # Armazenar os valores de SPI para o mês atual
            spi_mensal.extend(spi_mes)
        
            # Armazenar as estatísticas do mês
            estatisticas.append({
                        'Mês': mes,
                        'Média Mensal': media,
                        'q (zeros)': prob_zeros,
                        'Alpha (shape)': shape,
                        'Beta (scale)': scale
            })


        return spi_mensal, estatisticas
    
    # Calcular o SPI mensal e estatísticas por mês do ano
    spi_mensal, estatisticas = calcular_spi(precip_mensal)

    # Criar um DataFrame com os resultados
    spi_df = pd.DataFrame({'AnoMes': precip_mensal.index, 'PrecipitaçãoMensal': precip_mensal.values, 'SPI': spi_mensal})
    estatisticas_df = pd.DataFrame(estatisticas)

    # Exibir a tabela com o SPI calculado
    print(spi_df)
    print(estatisticas_df)

    return spi_df, estatisticas_df
def calculo_precipitacoes(df_inmet):
    """Determina as preciptações e intensidades máximas em função de diversos tempos de retorno e tempos de duraçao.
    
    Args:
        df_inmet (DataFrame): DataFrame com os dados de preciptação retirados do INMET
        
    Returns:
        h_max1aux (DataFrame): Valores de preciptação diária (mm) para os tempos de retorno selecionados (ano)
        preciptacao (DataFrame): Preciptação máxima para os tempos de retorno e tempos de duração selecionados
        intensidade (DataFrame): Intensidade de preciptação máxima para os tempos de retorno e duraçoes selecionadas
        df_longo (DataFrame): DataFrame com os valores de intensidade, preciptação máxima em funçao dos tempos de duraçao (min) e tempos de retorno (ano)
    """

    # Limpeza dos dados
    # Detectar o nome correto da coluna e renomear
    df = df_inmet
    if 'PRECIPITACAO TOTAL, DIARIO (AUT)(mm)' in df.columns:
        df.rename(columns={'PRECIPITACAO TOTAL, DIARIO (AUT)(mm)': 'PRECIPITACAO TOTAL DIARIA (mm)'}, inplace=True)
    elif 'PRECIPITACAO TOTAL, DIARIO(mm)' in df.columns:
        df.rename(columns={'PRECIPITACAO TOTAL, DIARIO(mm)': 'PRECIPITACAO TOTAL DIARIA (mm)'}, inplace=True)
    else:
        nomes_esperados = ['PRECIPITACAO TOTAL DIARIA (mm)']
        colunas_atuais = df.columns.tolist()
        # Verifica possíveis correspondências incorretas
        colunas_erradas = [col for col in colunas_atuais if 'PRECIPITACAO' in col]
        st.error("A coluna de precipitação não foi encontrada.")
        st.write("Colunas com possíveis erros:")
        st.table(colunas_erradas)
        st.write(f"O nome correto esperado é: <span style='color:green'>{nomes_esperados[0]}</span>", unsafe_allow_html=True)
        st.write("Colunas disponíveis no DataFrame:")
        st.table(colunas_atuais)
        st.stop()
    
    df['Data Medicao'] = pd.to_datetime(df['Data Medicao'])
    df['ano hidrológico'] = df['Data Medicao'].dt.year
    df['PRECIPITACAO TOTAL DIARIA (mm)'] = pd.to_numeric(df['PRECIPITACAO TOTAL DIARIA (mm)'], errors='coerce')
    df.dropna(subset=['PRECIPITACAO TOTAL DIARIA (mm)'], inplace=True)

    # Preciptação máxima por ano e estatística descritiva dos dados
    maiores_precipitacoes_por_ano = df.groupby('ano hidrológico')['PRECIPITACAO TOTAL DIARIA (mm)'].max()
    media = maiores_precipitacoes_por_ano.mean()
    desvio_padrao = maiores_precipitacoes_por_ano.std() 
    tempo_retorno = [2, 5, 10, 15, 20, 25, 50, 100, 250, 500, 1000]
    h_max1 = [calcular_hmax(media, desvio_padrao, tr) for tr in tempo_retorno]
    h_max1aux = pd.DataFrame({'tempo de retorno (anos)': tempo_retorno, 'Pmax diária (mm)': h_max1})

    # Desagregação da preciptação e intensidade
    preciptacao = desagragacao_preciptacao(h_max1)
    intensidade = conversao_intensidade(preciptacao)

    # Geração tabela IDF
    df_longo = intensidade.melt(id_vars='td (min)', var_name='tr', value_name='y_obs (mm/h)')
    df_longo['tr'] = df_longo['tr'].astype(float)

    return h_max1aux, preciptacao, intensidade, df_longo, media, desvio_padrao


def problema_inverso_idf(df_long):
    """Está função determina os parâmetros da equação IDF a partir dos dados de intensidade de preciptação máxima diária.
    
    Args:
        df_long (DataFrame): DataFrame com os valores de intensidade de preciptação máxima diária para os tempos de retorno selecionados (mm/h)
        
    Returns:
        a_opt (Float): Parâmetro a da equação IDF
        b_opt (Float): Parâmetro b da equação IDF
        c_opt (Float): Parâmetro c da equação IDF
        d_opt (Float): Parâmetro d da equação IDF
    """

    # Dados para confecção do IDF
    t_r = df_long['tr'].values 
    t_c = df_long['td (min)'].values  
    y_obs = df_long['y_obs (mm/h)'].values 

    # Equação de predição do IDF
 # Equação de predição do IDF
    def model_function(params, t_r, t_c):
        a, b, c, d = params
        return (a * t_r ** b) / (t_c + c)**d

    # Equação de erro
    def error_function(params, t_r, t_c, y_obs):
        y_pred = model_function(params, t_r, t_c)
        error = np.mean((y_pred - y_obs) ** 2)
        return error

    # Problema inverso
    initial_guess = [0, 0, 0, 0]
    bounds = [(1e-5, None), (1e-5, None), (1e-5, None), (1e-5, None)]
    result = minimize(error_function, initial_guess, args=(t_r, t_c, y_obs), bounds=bounds)
    a_opt, b_opt, c_opt, d_opt = result.x

    return a_opt, b_opt, c_opt, d_opt

def projeto_paredes_compressao(dados_parede_aux, gamma_f, gamma_w, f_pk, g, q, g_wall, n_pavtos, x_total, y_total, tipo_argamassa):
    """
    Verificação de projeto de paredes à compressão.
    
    Args:
        dados_parede_aux (pd.DataFrame): dataframe contendo os dados das paredes
        gamma_f (float): coeficiente de ponderação das ações permanentes
        gamma_w (float): coeficiente de ponderação das ações variáveis
        f_pk (float): resistência característica à compressão do bloco
        g (float): carga permanente da laje
        q (float): carga variável da laje
        g_wall (float): carga do peso próprio da parede
        n_pavtos (int): número de pavimentos
        x_total (float): comprimento total da estrutura
        y_total (float): largura total da estrutura
        tipo_argamassa (str): tipo de argamassa
        
        Returns:
        n_rd (list): lista contendo as resistências de cada parede
        n_sd (list): lista contendo as ações de cada parede
        g_0 (list): lista contendo os coeficientes de segurança de cada parede
        dados_parede (pd.DataFrame): dataframe contendo os dados das paredes
    """

    # Dados geométricos do modelo
    dados_parede = dados_parede_aux.copy()
    dados_parede['carga g laje (kN)'] = x_total * y_total * g
    dados_parede['carga q laje (kN)'] = x_total * y_total * q 
    dados_parede['area (m2)'] = dados_parede['l (m)'] * dados_parede['t (m)']
    dados_parede['area . x_g (m3)'] = dados_parede['area (m2)'] * dados_parede['x_g (m)']
    dados_parede['area . y_g (m3)'] = dados_parede['area (m2)'] * dados_parede['y_g (m)']
    x_g_global = dados_parede['area . x_g (m3)'].sum() / dados_parede['area (m2)'].sum()
    y_g_global = dados_parede['area . y_g (m3)'].sum() / dados_parede['area (m2)'].sum()
    dados_parede['x_1g (m)'] = dados_parede['x_g (m)'] - x_g_global
    dados_parede['y_1g (m)'] = dados_parede['y_g (m)'] - y_g_global
    dados_parede['area . x_g . x_g (m4)'] = dados_parede['area (m2)'] * dados_parede['x_1g (m)'] ** 2
    dados_parede['area . y_g . y_g (m4)'] = dados_parede['area (m2)'] * dados_parede['y_1g (m)'] ** 2
    e_x = x_total / 2 - x_g_global
    e_y = y_total / 2 - y_g_global
    ai_soma = dados_parede['area (m2)'].sum()
    aix_soma = dados_parede['area . x_g . x_g (m4)'].sum() 
    aiy_soma = dados_parede['area . y_g . y_g (m4)'].sum()
    
    # Cálculo do carregamento de cada parede
    dados_parede['parcela quinhão (valor/100)'] = dados_parede.apply(quinhao_de_carga, axis = 1, args = (ai_soma, aix_soma, aiy_soma, e_x, e_y))
    dados_parede['parcela_gi (kN)'] = dados_parede['carga g laje (kN)'] * dados_parede['parcela quinhão (valor/100)']
    dados_parede['parcela_gi_pp (kN)'] = g_wall * dados_parede['h (m)'] * dados_parede['l (m)']
    dados_parede['parcela_gi_total (kN)'] = dados_parede['parcela_gi (kN)'] + dados_parede['parcela_gi_pp (kN)']
    dados_parede['parcela_qi (kN)'] = dados_parede['carga q laje (kN)'] * dados_parede['parcela quinhão (valor/100)']
    dados_parede['n_sd (kN)'] = (dados_parede['parcela_qi (kN)'] + dados_parede['parcela_gi_total (kN)']) * gamma_f * n_pavtos

    # Cálculo da resistência de cada parede
    dados_parede['lambda'] = dados_parede['h (m)'] / dados_parede['t (m)']
    dados_parede['redutor R de resistência'] = 1 - (dados_parede['lambda'] / 40) ** 3
    if tipo_argamassa == 'total' or tipo_argamassa == 'argamassa de bloco inteiro':
        alpha_arg = 1.00
    else:
        alpha_arg = 0.80
    f_pd = 0.70 * (f_pk / gamma_w) * alpha_arg
    dados_parede['n_rd (kN)'] = dados_parede['area (m2)'] * f_pd * dados_parede['redutor R de resistência']
    dados_parede['g (kN)'] = dados_parede['n_sd (kN)'] - dados_parede['n_rd (kN)']
    n_rd = dados_parede['n_rd (kN)'].tolist()
    n_sd = dados_parede['n_sd (kN)'].tolist()
    g_0 = dados_parede['g (kN)'].tolist()
    
    return n_rd, n_sd, g_0, dados_parede


def download_excel(df, nome_df):
    if df is not None:
        excel_file_name = nome_df.split(".")[0] + "_copia.xlsx"

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            with pd.ExcelWriter(tmp.name, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)

            tmp.flush()

            with open(tmp.name, 'rb') as f:
                excel_file_content = f.read()
                
def plot_data(data):
    """
    Plota um gráfico com quadrados azuis em torno dos pontos e anotações a partir dos dados fornecidos.
    Retorna a figura gerada.

    Parâmetros:
    data (dict): Um dicionário com chaves 'label', 'x', 'y', 'L x', e 'L y'.
                 'label' deve ser uma lista de rótulos, 'x' e 'y' devem ser listas de coordenadas.
                 'L x' e 'L y' definem as dimensões dos quadrados ao redor dos pontos.
                 
    Retorna:
    plt.Figure: A figura gerada.
    """
    labels = data['label']
    x = data['x']
    y = data['y']
    L_x = data['L x']
    L_y = data['L y']

    # Criando a figura e os eixos
    fig, ax = plt.subplots(figsize=(10, 10))

    # Desenhando os quadrados e pontos
    for i in range(len(x)):
        # Adiciona um quadrado azul ao redor do ponto
        square = patches.Rectangle((x[i] - L_x[i] / 2, y[i] - L_y[i] / 2),
                                   L_x[i], L_y[i], linewidth=1, edgecolor='blue', facecolor='none')
        ax.add_patch(square)

        # Adiciona o ponto
        ax.scatter(x[i], y[i], color='red', marker='+', s=100)

        # Adiciona a anotação
        ax.annotate(labels[i], (x[i], y[i]), textcoords="offset points", xytext=(0, 10), ha='center')

    # Configurando o gráfico
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Posicionamento das sapatas')
    ax.grid(True)

    # Retorna a figura
    return fig

def run_python_script():
    # Usando sys.executable para garantir que o mesmo Python do ambiente Streamlit seja usado
    result = subprocess.run([sys.executable, './paginas/otimizador/hill_climbing.py'], capture_output=True, text=True)

    if result.returncode == 0:
        st.write("Resultado do script:")
        st.text(result.stdout)  # Exibe a saída do script
    else:
        st.write("Erro ao executar o script:")
        st.text(result.stderr)  # Exibe o erro, caso haja
    

def prop_geometrica_estadio_ii(H_F, B_F, B_W, A_ST, A_SC, ALPHA_MOD, D, D_L, PRINT=False):
    """
    Esta função calcula as propriedades geométricas de uma peça de concreto armado no estádio II.

    Entrada:
    H_F        | Altura de mesa superior da seção Tê                     | m    | float
    B_F        | Base de mesa superior da seção Tê                       | m    | float
    B_W        | Base de alma da seção Tê                                | m    | float
    A_ST       | Área de aço na seção tracionada                         | m²   | float
    A_SC       | Área de aço na seção comprimida                         | m²   | float
    ALPHA_MOD  | Relação entre os módulos de elasticidade aço-concreto   |      | float
    D          | Altura útil da armadura tracionada                      | m    | float
    D_L        | Altura útil da armadura comprimida                      | m    | float
    PRINT      | Critério de impressão dos resultados para visualização  |      | string

    Saída:
    X_II       | Centro geometrico da viga no estádio 2                  | m    | float
    I_II       | Inércia da viga no estádio 2                            | m^4  | float
    """
    
    # Checagem do primeiro teste de linha neutra. Hipótese de B_W = B_F
    A_1 = B_F / 2
    H_FAUX = H_F * 0 
    A_2 = H_FAUX * (B_F - B_W) + (ALPHA_MOD - 1) * A_SC + ALPHA_MOD * A_ST
    A_3 = - D_L * (ALPHA_MOD - 1) * A_SC - D * ALPHA_MOD * A_ST - (H_FAUX ** 2 / 2) * (B_F - B_W)
    X_IITESTE = (- A_2 + (A_2 ** 2 - 4 * A_1 * A_3) ** 0.50) / (2 * A_1)
    
    # Cálculo da linha neutra em função do teste de 1º chute
    if X_IITESTE <= H_F:
        # L.N. passando pela mesa
        X_II = X_IITESTE
        PASSA_ONDE = "mesa"
    elif X_IITESTE > H_F:
        # L.N. passando pela alma
        A_1 = B_W / 2
        A_2 = H_F * (B_F - B_W) + (ALPHA_MOD - 1) * A_SC + ALPHA_MOD * A_ST
        A_3 = - D_L * (ALPHA_MOD - 1) * A_SC - D * ALPHA_MOD * A_ST - (H_F ** 2 / 2) * (B_F - B_W)
        X_II = (- A_2 + (A_2 ** 2 - 4 * A_1 * A_3) ** 0.50) / (2 * A_1)
        PASSA_ONDE = "alma"
    
    # Inércia estádio II
    if X_II <= H_F:
        # L.N. passando pela mesa
        I_II = (B_F * X_II ** 3) / 3 + ALPHA_MOD * A_ST * (X_II - D) ** 2 + (ALPHA_MOD - 1) * A_SC * (X_II - D_L) ** 2
    else:
        # L.N. passando pela alma
        I_II = ((B_F - B_W) * H_F ** 3) / 12 + (B_W * X_II ** 3) / 3 + (B_F - B_W) * (X_II - H_F * 0.50) ** 2 + ALPHA_MOD * A_ST * (X_II - D) ** 2 + (ALPHA_MOD - 1) * A_SC * (X_II - D_L) ** 2
   
    # Impressões
    if PRINT == True:
        print("\n")
        print("PROP. ESTÁDIO II")
        print("X_IITESTE: ", X_IITESTE)
        print("X_II: ", X_II)
        print("I_II: ", I_II)
        print("\n")

    return X_II, I_II, A_1, A_2, A_3, PASSA_ONDE, X_IITESTE

def vazio():
    texto = r'''
    '''
    st.write(texto)
def prop_geometrica_estadio_i(H, H_F, B_F, B_W, A_ST, ALPHA_MOD, D, PRINT=False):
    """
    Esta função calcula as propriedades geométricas de uma peça de concreto armado no estádio I.

    Entrada:
    H          | Altura total da seção Tê                                  | m    | float
    H_F        | Altura de mesa superior da seção Tê                       | m    | float
    B_F        | Base de mesa superior da seção Tê                         | m    | float
    B_W        | Base de alma da seção Tê                                  | m    | float
    A_ST       | Area de aço na seção tracionada                           | m²   | float
    ALPHA_MOD  | Relação entre os módulos de elasticidade aço-concreto     |      | float
    D          | Altura útil da armadura tracionada                        | m    | float
    PRINT      | Critério de impressão dos resultados para visualização    |      | string

    Saída:
    A_CI       | Área de concreto homogeneizada no estádio I               | m²   | float
    X_I        | Centro geometrico da seção no estádio I bordo comprimido  | m    | float
    I_I        | Inércia homogeneizada da seção no estádio I               | m^4  | float
    W_INF      | Módulo resistente da seção bordo inferior                 | m³   | float
    W_SUP      | Módulo resistente da seção bordo superior                 | m³   | float    
    """
    
    # Área, Linha Neutra e Inércia
    A_CI = H_F * (B_F - B_W) + B_W * H + A_ST * (ALPHA_MOD - 1)
    PARCELA_1 = (B_F - B_W) * ((H_F ** 2) / 2)
    PARCELA_2 = 0.50 * B_W * H ** 2
    PARCELA_3 = A_ST * (ALPHA_MOD - 1) * D
    X_I = (PARCELA_1 + PARCELA_2 + PARCELA_3) / A_CI
    I_I = ((B_F - B_W) * H_F ** 3) / 12 + (B_W * H ** 3) / 12 + H_F * (B_F - B_W) * (X_I - H_F * 0.50) ** 2 + B_W * H * (X_I - 0.50 * H) ** 2 + A_ST * (ALPHA_MOD - 1) * (X_I - D) ** 2
    W_SUP = I_I / X_I
    W_INF = I_I / (H - X_I)

    # Impressões
    if PRINT == True:
        print("\n")
        print("PROP. GEOMETRICAS ESTÁDIO I")
        print("A_CI:  ", A_CI)
        print("X_I:   ", X_I)
        print("I_I:   ", I_I)
        print("W_INF: ", X_I)
        print("W_SUP: ", I_I)
        print("\n")
    
    return A_CI, X_I, I_I, W_INF, W_SUP


def circulo_mohr_2d(sigma_x, sigma_y, tal_xy, impressoes=False):
    """Está função determina o círculo de Mohr para tensões planas 2D.
    
    Args:
        sigma_x (float): Tensão normal em x.
        sigma_y (float): Tensão normal em y.
        tal_xy (float): Tensão de cisalhamento xy.
        impressoes (bool): Se True, imprime os valores calculados.
    
    Returns:
        fig: Retorna a figura com o círculo de Mohr.
    """
    
    # Determinação das tensões máximas, mínimas e suas inclinações
    sigma_med = (sigma_x + sigma_y) / 2
    raio = np.sqrt((0.50 * (sigma_x - sigma_y))**2 + tal_xy**2)
    sigma_maxx = sigma_med + raio
    sigma_minn = sigma_med - raio
    theta_p_radianos = np.arctan2(2*tal_xy, (sigma_x-sigma_y)) / 2
    theta_p_graus = np.degrees(theta_p_radianos)
    theta_c_radianos = np.arctan2(-(sigma_x-sigma_y), 2*tal_xy) / 2
    theta_c_graus = np.degrees(theta_c_radianos)
    def calcular_ponto_circunferencia(x_c, y_c, raio, angulo_graus):
        angulo_radianos = np.radians(angulo_graus)
        x = x_c + raio * np.cos(angulo_radianos)
        y = y_c + raio * np.sin(angulo_radianos)
        return x, y
    sigma_x_linha1, sigma_y_linha1 = calcular_ponto_circunferencia(sigma_med, 0, raio, -theta_p_graus)
    sigma_x_linha2, sigma_y_linha2 = calcular_ponto_circunferencia(sigma_med, 0, raio, -theta_p_graus+180)

    # Criando uma nova figura
    fig, ax = plt.subplots()

    # Centro e raio da circunferência
    x_c, y_c = sigma_med, 0

    # Criando os pontos para a circunferência
    theta = np.linspace(0, 2*np.pi, 100)
    x_circle = x_c + raio * np.cos(theta)
    y_circle = y_c + raio * np.sin(theta)

    # Plotando a circunferência
    ax.plot(x_circle, y_circle, color='blue')

    # Pontos de sigma_min e sigma_max
    sigma_min = (sigma_minn, 0)
    sigma_max = (sigma_maxx, 0)

    # Plotando os pontos de máximo e mínimo e adicionando as anotações
    ax.scatter(*sigma_min, color='red')
    ax.text(sigma_min[0]-0.27*np.abs(sigma_min[0]), raio*0.10, f'σmin=\n{sigma_minn:.3f}', verticalalignment='top', horizontalalignment='left', color='red')
    ax.scatter(*sigma_max, color='red')
    ax.text(sigma_max[0]+0.15*np.abs(sigma_max[0]), raio*0.10, f'σmax=\n{sigma_maxx:.3f}', verticalalignment='top', horizontalalignment='left', color='red')
    
    # Plotando os pontos A e B
    xa, ya = sigma_x, tal_xy
    xb, yb = sigma_y, -tal_xy
    m = (yb - ya) / (xb - xa)
    b = ya - m * xa
    # print(f"m = {m}")
    # print(f"b = {b}")
    # print(f"xa = {xa}")
    # print(f"ya = {ya}")
    # print(f"xb = {xb}")
    # print(f"yb = {yb}")
    # print(xb-0.30*xb)
    ax.plot([xa, xb], [ya, yb], color='magenta')
    ax.scatter([xa, xb], [ya, yb], color='magenta')
    ax.text(xa+0.27*xa, m*(xa+0.27*xa)+b, 'A=σx,τxy', verticalalignment='bottom', horizontalalignment='left', color='magenta')
    ax.text(xb+0.27*xb, m*(xb+0.27*xb)+b, 'B=σy,-τxy', verticalalignment='bottom', horizontalalignment='left', color='magenta')

    # Adicionando o eixo x passando por y=0
    ax.axhline(y=0, color='black', linestyle='--')
    ax.axvline(x=sigma_med, color='black', linestyle='--')

    # Adicionando legendas e título
    ax.set_xlabel('Eixo x')
    ax.set_ylabel('Eixo y')

    # Definindo limites dos eixos
    ax.set_xlim(x_c - raio - 5, x_c + raio + 5)
    ax.set_ylim(-raio - 1, raio + 1)

    # Exibindo o gráfico
    ax.grid(True, alpha=0.5)
    ax.axis('equal')
    plt.gca().invert_yaxis()
    # plt.show()

    if impressoes is True:
        print(f"sigma_med = {sigma_med:.3e}")
        print(f"tal_max = {raio:.3e}")
        print(f"sigma_max = {sigma_maxx:.3e}")
        print(f"sigma_min = {sigma_minn:.3e}")
        print(f"inclinação tensões principais theta_p = {theta_p_graus:.3e}")
        print(f"inclinação tensão máxima cisalhamento theta_c = {theta_c_graus:.3e}")
        print(f"sigma_x_linha1 = {sigma_x_linha1:.3e}")
        print(f"sigma_y_linha1 = {sigma_y_linha1:.3e}")
        print(f"sigma_x_linha2 = {sigma_x_linha2:.3e}")
        print(f"sigma_y_linha2 = {sigma_y_linha2:.3e}")

    return fig, sigma_med, raio, sigma_maxx, sigma_minn, theta_p_graus, theta_c_grausdef area_aco_flexao_simples(b_w, h, d, f_ck, f_ywk, gamma_c, gamma_s, m_sd, v_sd, cob, phi_est, d_max, impressao=False):
    """
    Esta função determina a área de aço necessária para combater os esforços de flexão na peça de concreto armado de acordo com a NBR 6118.

    Args:
        b_w (float): Largura da viga (m)
        h (float): Altura da viga (m)
        d (float): Altura útil da seção (m)
        f_ck (float): Resistência característica à compressão (kPa)
        f_ywk (float): Resistência característica do aço (kPa)
        gamma_c (float): Coeficiente de minoração da resistência do concreto
        gamma_s (float): Coeficiente de minoração da resistência do aço
        m_sd (float): Momento fletor de cálculo (kNm)
        v_sd (float): Esforço cortante de cálculo (kN)
        cob (float): Cobrimento da armadura (m)
        phi_est (float): Diâmetro do estribo (m)
        d_max (float): Diâmetro máximo do agregado graudo (m)
        impressao (bool): Critério de impressão dos resultados para visualização
    
    Returns:
        x_iii (float): Linha neutra da peça (m)
        z_iii (float): Braço de alavanca (m)
        a_slmin (float): Área de aço mínima (m2)
        a_sl (float): Área de aço longitudinal (m2)
        v_rd2 (float): Esforço cortante resistente (kN)
        v_c0 (float): Esforço cortante resistente do concreto (kN)
        a_swmin (float): Área de aço transversal mínima (m2)
        a_sw90 (float): Área de aço transversal (m2)
        a_h (list): Espaçamento horizontal entre as barras (m)
        a_v (list): Espaçamento vertical entre as barras (m)
        n_bar_cam (list): Quantidade de barras por camada
        fig (matplotlib.figure): Figura com os desenhos das barras de aço na seção transversal da viga
    """

    # Verificação constates de projeto
    f_ck /= 1E3
    if f_ck >  50:
        lambda_c = 0.80 - ((f_ck - 50) / 400)
        alpha_c = (1.00 - ((f_ck - 50) / 200)) * 0.85
        beta = 0.35
        f_ctm = 2.12 * np.log(1 + 0.10 * (f_ck + 8.00))
    else:
        lambda_c = 0.80
        alpha_c = 0.85
        beta = 0.45
        f_ctm = 0.30 * f_ck**(2 / 3)
    alpha_v2 = 1 - f_ck / 250
    f_ctm *= 1E3
    f_ctksup = 1.30 * f_ctm
    #f_ctkinf = 0.7 * f_ctm
    f_ck *= 1E3
    f_cd = f_ck / gamma_c
    f_yd = f_ywk / gamma_s
    # Armadura flexão mínima
    inercia = b_w * h**3 / 12
    w_0 = inercia / (h / 2)
    m_sdmin = 0.80 * w_0 * f_ctksup
    zeta_min = m_sdmin / (b_w * alpha_c * f_cd)
    aux_min = d**2 - 2 * zeta_min
    numerador_min = d - np.sqrt(aux_min)
    denominador_min = lambda_c
    x_iii_min = numerador_min / denominador_min
    z_iii_min = d - 0.50 * lambda_c * x_iii_min
    a_slmin = m_sdmin / (z_iii_min * f_yd)

    # Cálculo da área de aço armadura simples/dupla e esforços resistentes
    m_rdlim = b_w * d**2 * lambda_c * beta * alpha_c * f_cd * (1 - 0.50 * lambda_c * beta)
    v_rd2 = 0.27 * alpha_v2 * f_cd * b_w * d
    if m_sd > m_rdlim:
        if impressao is True:
            print("O momento fletor de cálculo é maior que o momento fletor mínimo. Portanto deve-se usar armadura dupla")  
    else:
        zeta = m_sd / (b_w * alpha_c * f_cd)
        aux = d**2 - 2 * zeta
        numerador = d - np.sqrt(aux)
        denominador = lambda_c
        x_iii = numerador / denominador
        z_iii = d - 0.50 * lambda_c * x_iii
        f_yd = f_ywk / gamma_s
        a_slaux = m_sd / (z_iii * f_yd)
        a_sl = max(a_slmin, a_slaux)

    # Cálcuo da área de aço transversal
    f_ctd = (0.7 * f_ctm) / gamma_c
    v_c0 = 0.6 * f_ctd * b_w * d
    v_c = v_c0
    inclinacao_est = np.pi / 2
    pho_sw = 0.20 * (f_ctm / f_ywk)
    a_swmin = pho_sw * b_w * np.sin(inclinacao_est)
    if v_sd <= v_c:
        a_swaux = a_swmin
        v_sw = 0
    else:
        v_sw = v_sd - v_c
        f_ywdaux = f_ywk / gamma_s
        f_ywdmax = 500E3 / gamma_s 
        f_ywd = min(f_ywdaux, f_ywdmax)
        a_swaux = v_sw / (0.90 * d * f_ywd * (np.sin(inclinacao_est) + np.cos(inclinacao_est)))
    a_sw90 = max(a_swaux, a_swmin)

    # Espaçamento entre as barras
    phi_l = [6.3, 8.0, 10, 12.5, 16, 20, 25, 32]
    phi_l_aux = [x / 1000 for x in phi_l]
    a_h = []
    a_v = []
    for i in phi_l_aux:
        a_h1 = 2 / 100
        a_h2 = 1.04 * i 
        a_h3 = 1.20 * d_max
        a_v3 = 0.50 * d_max
        a_h.append(max(a_h1, a_h2, a_h3))
        a_v.append(max(a_h1, a_h2, a_v3))

    # Geração da figura da seção
    desenhos, n_bar_cam = quantidade_barras_por_camada(phi_est, cob, b_w, a_h, a_sl, impressao)
    fig = desenho_armadura_secao(b_w, h, phi_est, cob, a_v, phi_l, desenhos)
    
    # Impressões
    if impressao is True:
        print("\n")
        print("Determinação da quantidade de área de aço longitudinal")
        print(f"m_Rdlim={m_rdlim:.3e} kNm (limite armadura simples)", )
        print(f"x_iii={x_iii:.3e} m", )
        print(f"z_iii={z_iii:.3e} m")
        print(f"a_slmin={a_slmin:.3e} m2")
        print(f"a_sl={a_sl:.3e} m2")
        print("Determinação da quantidade de área de aço transversal")
        print(f"v_Rd2={v_rd2:.3e} kN")
        print(f"v_c0={v_c0:.3e} kN")
        print(f"a_swmin={a_swmin:.3e} m2/m")
        print(f"a_sw90={a_sw90:.3e} m2/m")

    return x_iii, z_iii, a_slmin, a_sl, v_rd2, v_c0, a_swmin, a_sw90, a_h, a_v, n_bar_cam, fig

def desenho_armadura_secao(b_w, h, phi_est, cob, a_v, barras_long, desenhos):
    """Desenho das barras de aço na seção transversal da viga de concreto armado.
    
    Args:
        b_w (float): Largura da viga (m)
        h (float): Altura da viga (m)
        phi_est (float): Diâmetro do estribo (m)
        cob (float): Cobrimento da armadura (m)
        a_v (list): Espaçamento vertical entre as barras (m)
        barras_long (list): Lista com as bitolas disponíveis (mm)
        desenhos (list): Lista com as quantidades de barras para cada bitola disponível

    Returns:
        fig (matplotlib.figure): Figura com os desenhos das barras de aço na seção transversal da viga
    """
    
    # Criando os desenhos da viga e estribo
    viga_x = [0, b_w, b_w, 0, 0]
    viga_y = [0, 0, h, h,0] 
    est_ext_x = [cob, b_w - cob, b_w - cob, cob, cob]
    est_ext_y = [cob, cob, h - cob, h - cob, cob]
    est_int_x = [cob + phi_est, b_w - cob - phi_est, b_w - cob - phi_est, cob + phi_est, cob + phi_est]
    est_int_y = [cob + phi_est, cob + phi_est, h - cob - phi_est, h - cob - phi_est, cob + phi_est]

    # Criando a figura de 8 partes
    fig, axs = plt.subplots(4, 2, figsize=(5, 10), dpi=300)

    # Iterar sobre os eixos e bitolas disponíveis
    cont = 0
    for ax, titulo in zip(axs.ravel(), barras_long):
        ax.set_title(f'detalhe {titulo} mm')
        ax.plot(viga_x, viga_y, color='gray', linewidth=1)
        ax.plot(est_ext_x, est_ext_y, color='blue', linewidth=0.5)
        ax.plot(est_int_x, est_int_y, color='blue', linewidth=0.5)
        # Determinando o valor de espaçamento e posição das barras para as bitolas disponíveis
        phi_l = titulo / 1000
        raio = phi_l / 2
        desenho_bars = desenhos[cont]
        y_coord = []
        y_aux = cob + phi_est + phi_l/2
        for m in range(len(desenho_bars)):
            y_coord_aux = []
            for n in range(int(desenho_bars[m])):
                y_coord_aux.append(y_aux)
            y_coord.append(y_coord_aux)
            y_aux += phi_l + a_v[cont]
        cont += 1
        x_coord = []
        for k in range(len(desenho_bars)):
            x_coord_aux = []
            n_esp = desenho_bars[k] - 1
            b_disp = b_w - 2 * (cob + phi_est + phi_l/2)
            for l in range(int(desenho_bars[k])):
                if desenho_bars[k] == 1:
                  x_coord_aux.append(cob + phi_est + phi_l/2)
                  break
                elif desenho_bars[k] == 2:
                  x_coord_aux.append(cob + phi_est + phi_l/2)
                  x_coord_aux.append(b_w - cob - phi_est - phi_l/2)
                  break
                else:
                  dist = b_disp / n_esp
                  if l == 0:
                    aux = cob + phi_est + phi_l/2
                  elif l == desenho_bars[k] - 1:
                    aux = b_w - cob - phi_est - phi_l/2
                  else:
                    aux = x_coord_aux[l-1] + dist
                  x_coord_aux.append(aux)
            x_coord.append(x_coord_aux)
        for i in range(len(desenho_bars)):
          for j in range(int(desenho_bars[i])):
              x = x_coord[i][j] 
              y = y_coord[i][j] 
              circulo = patches.Circle((x, y), raio, edgecolor='red', facecolor='none', linewidth=0.5)
              ax.add_patch(circulo)
        ax.set_xlim(-0.05, b_w+0.05)
        ax.set_ylim(-0.05, h+0.05)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.tight_layout() 
               
    return fig
    
def quantidade_barras_por_camada(phi_est, cob, b_w, a_h, a_sl, impressao=False):
    """
    Quantidade de barras por camadas.

    Args:
        phi_est (float): Diâmetro do estribo (m)
        cob (float): Cobrimento da armadura (m)
        b_w (float): Largura da viga (m)
        a_h (list): Espaçamento horizontal entre as barras (m)
        a_sl (float): Área de aço longitudinal (m2)

    Returns:
        desenhos (list): Lista com as quantidades de barras por camada para cada bitola disponível
        n_bar_por_camada (list): Lista com as quantidades de barras por camada para cada bitola disponível
    """

    # Largura disponível
    phi_l = [6.3, 8.0, 10, 12.5, 16, 20, 25, 32]
    phi_l = [x / 1000 for x in phi_l]
    n_bar_por_camada = []
    asl_phi = []
    n_bar_tot = []
    phi_cor = []
    b_disp = b_w - 2 * (cob + phi_est)

    # Cálculo da quantidade de barras por camada
    for chave, valor in enumerate(phi_l):
        asl_phi.append(np.pi * ((valor * 1.04) ** 2) / 4)
        phi_cor.append(valor + (4/100 * valor))
        n_bar_por_camada.append(round((b_disp + a_h[chave]) / (valor + a_h[chave])))

    # Cálculo da quantidade total de barras
    for chave, valor in enumerate(asl_phi):
        n_bar_tot.append(a_sl/valor)
    n_bar_tot = list(map(np.ceil, n_bar_tot))

    # Cálculo da quantidade de barras por camada
    n_cam = [x / y for x, y in zip(n_bar_tot, n_bar_por_camada)]
    n_cam = list(map(np.ceil, n_cam))

    # Barras por camada
    desenhos = []
    for chave, valor in enumerate(n_cam):
        desenho_phi = []
        n_bar_tot_aux = n_bar_tot[chave]
        for i in range(int(valor)):
            if i == valor - 1:
                desenho_phi.append(n_bar_tot_aux)
            else:
                desenho_phi.append(n_bar_por_camada[chave])
                n_bar_tot_aux -= n_bar_por_camada[chave]
        desenhos.append(desenho_phi)

    # Impressões
    if impressao is True:
        print("\n")
        print("Detalhamento das camadas de armadura")
        for chave, valor in enumerate(phi_l):
            print(f"Bitola: {valor * 1000} mm")
            print(f"Quantidade de camadas: {n_cam[chave]}")
            print(f"Quantidade total de barras: {n_bar_tot[chave]}")
            print(f"Quantidade total de barras por camada: {n_bar_por_camada[chave]}")
            print(f"Quantidade de barras por camada: {desenhos[chave]}")

    return desenhos, n_bar_por_camada

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
