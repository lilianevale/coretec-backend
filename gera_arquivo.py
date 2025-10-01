import pandas as pd

# Criando dados de exemplo
data = {
    "Data Medicao": pd.date_range(start="2020-01-01", periods=20, freq="D"),
    "PRECIPITACAO TOTAL DIARIA (mm)": [10, 5, 0, 12, 8, 15, 20, 0, 5, 7, 6, 4, 0, 3, 10, 5, 0, 8, 7, 9]
}

df = pd.DataFrame(data)

# Salvar como Excel sem index
df.to_excel("exemplo_precipitacao.xlsx", index=False)