import pandas as pd
import numpy as np
import os


df = pd.read_csv('Itens.csv')

col_tipo = [c for c in df.columns if 'Tipo' in c][0]
col_status_reg =[c for c in df.columns if 'Status do Registro' in c][0]
col_status_mod =[c for c in df.columns if 'Status do Modelo' in c][0]

df_util = (
    (df[col_status_reg] == 'Ativo') &
     (df[col_status_mod] != 'Excluido') &
      (df[col_tipo] == 'Split Hi-Wall'))


df_filtrado = df[df_util].copy()

col_marca = [c for c in df_filtrado.columns if 'Marca' in c][0]
col_modelo = [c for c in df_filtrado if 'Modelo' in c][0]

col_btu = [c for c in df_filtrado if 'BTU' in c or 'Btu' in c][0]
col_consumo = [c for c in df_filtrado if 'Consumo Anual' in c][0]
col_eficiencia = [c for c in df_filtrado if 'IDRS' in c][0]



print(df[col_status_mod].value_counts())

print(df[col_status_reg].value_counts())



df_limpo = df_filtrado[[col_marca,col_modelo,col_tipo, col_btu,col_consumo,col_eficiencia]].copy()


df_final = df_limpo.reset_index(drop=True)

#df_final.head()

df_final.value_counts()


df_final[[col_marca, col_btu, col_consumo, col_eficiencia]].max()






#df_final.to_csv('dados_limpos.csv', index=False)

def calcular_economia(kwh1, kwh2, area, tarifa):
    # Aquela função matemática que a gente fez
    fator = 1 + (area / 40)
    custo1 = kwh1 * fator * tarifa
    custo2 = kwh2 * fator * tarifa
    
    diff = abs(custo1 - custo2)
    maior = max(custo1, custo2)
    pct = ((maior - min(custo1, custo2)) / maior) * 100 if maior > 0 else 0
    
    # Retorna um "dicionário" (pacote) com os resultados
    return {
        "custo1": custo1,
        "custo2": custo2,
        "diferenca": diff,
        "porcentagem": pct
    }


# NOME DO ARQUIVO
ARQUIVO_ANEEL = "data.xlsx" \
"" 

def converter():
    if not os.path.exists(ARQUIVO_ANEEL):
        print(f"Erro: Não achei o arquivo '{ARQUIVO_ANEEL}'. Baixe do site e coloque na pasta!")
        return

    print("Lendo arquivo da ANEEL...")
    
    try:
      # Lê o Excel
        df_raw = pd.read_excel(ARQUIVO_ANEEL)
        
        # Limpa nomes das colunas
        df_raw.columns = df_raw.columns.str.strip().str.lower()
        
        # Procura as colunas exatas que vimos na sua imagem
        # Geralmente: 'uf', 'distribuidora', 'tarifa convencional'
        col_empresa = next((c for c in df_raw.columns if 'distribuidora' in c), None)
        col_uf = next((c for c in df_raw.columns if 'uf' in c or 'estado' in c), None)
        # Pega especificamente a "Tarifa Convencional" que é o dado concreto
        col_valor = next((c for c in df_raw.columns if 'tarifa convencional' in c), None)

        if not all([col_empresa, col_uf, col_valor]):
            print(f"⚠️ Colunas não identificadas. Achei: {df_raw.columns.tolist()}")
            return

        # Cria o DataFrame final SOMENTE com o que existe no arquivo
        df_limpo = pd.DataFrame()
        df_limpo['estado'] = df_raw[col_uf]
        df_limpo['empresa'] = df_raw[col_empresa]
        df_limpo['tarifa'] = df_raw[col_valor]

        # Salva sem criar linhas de bandeira
        df_limpo.to_csv("Tarifas.csv", index=False)
        print("✅ Tarifas.csv gerado apenas com os dados originais (Tarifa Convencional).")
        print(df_limpo.head())

    except Exception as e:
        print(f"Deu ruim na conversão: {e}")

if __name__ == "__main__":
    converter()