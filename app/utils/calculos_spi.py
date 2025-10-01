# app/utils/calculos_spi.py

import pandas as pd
import numpy as np
from scipy.stats import gamma, norm

def indice_spi(df_inmet):
    """
    Calcula SPI mensal, ignorando meses sem dados ou com precipitação zero.
    """
    df = df_inmet.copy()

    df.rename(columns=lambda x: x.strip(), inplace=True)
    if 'PRECIPITACAO TOTAL DIARIA (mm)' not in df.columns:
        raise ValueError(f"Coluna 'PRECIPITACAO TOTAL DIARIA (mm)' não encontrada.")

    df['PRECIPITACAO TOTAL DIARIA (mm)'] = pd.to_numeric(df['PRECIPITACAO TOTAL DIARIA (mm)'], errors='coerce')
    df['Data Medicao'] = pd.to_datetime(df['Data Medicao'], errors='coerce')
    df.dropna(subset=['PRECIPITACAO TOTAL DIARIA (mm)', 'Data Medicao'], inplace=True)

    df['AnoMes'] = df['Data Medicao'].dt.to_period('M')
    precip_mensal = df.groupby('AnoMes')['PRECIPITACAO TOTAL DIARIA (mm)'].sum()

    spi_list = []
    estatisticas = []

    for mes in range(1, 13):
        idx = [p.month for p in precip_mensal.index]
        dados_mes = precip_mensal[np.array(idx) == mes]

        if len(dados_mes) == 0:
            continue

        zeros = (dados_mes == 0).sum()
        positivos = dados_mes[dados_mes > 0]
        prob_zeros = zeros / len(dados_mes)

        if len(positivos) > 0 and positivos.std() > 0:
            try:
                shape, loc, scale = gamma.fit(positivos, floc=0)
                cdf = gamma.cdf(dados_mes, shape, loc=loc, scale=scale)
                cdf_adjusted = prob_zeros + (1 - prob_zeros) * cdf
                spi_mes = norm.ppf(cdf_adjusted)
            except:
                spi_mes = np.zeros(len(dados_mes))
                shape, scale = np.nan, np.nan
        else:
            # Todos zeros ou sem variação → SPI = 0
            spi_mes = np.zeros(len(dados_mes))
            shape, scale = np.nan, np.nan

        spi_list.extend(spi_mes)

        estatisticas.append({
            'Mês': mes,
            'Média Mensal': dados_mes.mean(),
            'q (zeros)': prob_zeros,
            'Alpha (shape)': shape,
            'Beta (scale)': scale
        })

    spi_df = pd.DataFrame({
        'AnoMes': precip_mensal.index.astype(str),
        'PrecipitaçãoMensal': precip_mensal.values,
        'SPI': spi_list
    })

    estatisticas_df = pd.DataFrame(estatisticas)

    return spi_df, estatisticas_df
