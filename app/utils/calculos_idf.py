import pandas as pd

def calcular_hmax(media, desvio_padrao, tr):
    """
    Calcula precipitação máxima diária para um tempo de retorno (tr).
    Fórmula simplificada: média + desvio_padrao * fator do tempo de retorno
    """
    return media + desvio_padrao * (tr / 10)

def desagragacao_precipitacao(h_max1):
    """
    Desagrega a precipitação máxima diária em diferentes durações (td)
    Retorna um DataFrame com td (min) e colunas para cada tr
    """
    td = [10, 30, 60]  # minutos
    df = pd.DataFrame({'td (min)': td})
    for i, h in enumerate(h_max1, start=1):
        df[f"{i}"] = [h * 0.1, h * 0.2, h * 0.3]  # exemplo simplificado
    return df

def conversao_intensidade(precipitacao):
    """
    Converte precipitação (mm) em intensidade (mm/h)
    """
    df = precipitacao.copy()
    for col in df.columns:
        if col != 'td (min)':
            df[col] = df[col] / (df['td (min)'] / 60)  # mm/h
    return df

def calculo_precipitacoes(df_inmet):
    """
    Calcula precipitações máximas, intensidades e tabela longa IDF.
    Retorna h_max1aux, preciptacao, intensidade, df_longo, media, desvio_padrao
    """
    df = df_inmet.copy()

    # Renomear coluna de precipitação
    col_prec = [c for c in df.columns if "PRECIPITACAO" in c.upper()]
    if not col_prec:
        raise ValueError(f"Coluna de precipitação não encontrada. Colunas disponíveis: {df.columns.tolist()}")
    df.rename(columns={col_prec[0]: "PRECIPITACAO TOTAL DIARIA (mm)"}, inplace=True)

    # Garantir colunas corretas
    if 'Data Medicao' not in df.columns:
        raise ValueError("Coluna 'Data Medicao' não encontrada.")
    df['Data Medicao'] = pd.to_datetime(df['Data Medicao'])
    df['ano hidrológico'] = df['Data Medicao'].dt.year
    df['PRECIPITACAO TOTAL DIARIA (mm)'] = pd.to_numeric(df['PRECIPITACAO TOTAL DIARIA (mm)'], errors='coerce')
    df.dropna(subset=['PRECIPITACAO TOTAL DIARIA (mm)'], inplace=True)

    # Precipitação máxima anual
    maiores_precipitacoes_por_ano = df.groupby('ano hidrológico')['PRECIPITACAO TOTAL DIARIA (mm)'].max()
    media = maiores_precipitacoes_por_ano.mean()
    desvio_padrao = maiores_precipitacoes_por_ano.std()

    # Proteção contra NaN
    if pd.isna(desvio_padrao) or desvio_padrao == 0:
        desvio_padrao = 0.1 * media  # valor conservador

    tempo_retorno = [2, 5, 10, 15, 20, 25, 50, 100, 250, 500, 1000]
    h_max1 = [calcular_hmax(media, desvio_padrao, tr) for tr in tempo_retorno]
    h_max1aux = pd.DataFrame({'tempo de retorno (anos)': tempo_retorno, 'Pmax diária (mm)': h_max1})

    # Desagregação da precipitação e intensidade
    preciptacao = desagragacao_precipitacao(h_max1)
    intensidade = conversao_intensidade(preciptacao)

    # Tabela longa IDF
    df_longo = intensidade.melt(id_vars='td (min)', var_name='tr', value_name='y_obs (mm/h)')
    df_longo['tr'] = df_longo['tr'].astype(float)

    return h_max1aux, preciptacao, intensidade, df_longo, media, desvio_padrao
