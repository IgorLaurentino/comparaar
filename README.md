# ❄️ Comparador Inteligente de Ar Condicionado

Bem-vindo ao repositório do **Comparador de Climatização**, uma ferramenta desenvolvida para ajudar consumidores e instaladores a escolherem o ar-condicionado mais eficiente financeiramente.

🔗 **Acesse a aplicação aqui: https://comparaar.streamlit.app/ ou https://bit.ly/compara-ar

## 🎯 Objetivo
Muitas vezes, o ar-condicionado mais barato na loja é o que gera a conta de luz mais cara no final do mês. Este projeto cruza dados técnicos de consumo com as tarifas de energia de cada estado brasileiro para calcular o **Custo Total de Propriedade (TCO)** e o **Payback** de modelos mais eficientes.

## 🚀 Funcionalidades
- **Cálculo Real de Tarifa:** Seleção automática da tarifa de energia baseada no Estado, Distribuidora e Bandeira Tarifária.
- **Comparação Lado a Lado:** Compare dois modelos diferentes (ex: Inverter vs Convencional).
- **Cálculo de Payback:** Descubra em quantos meses a economia de energia paga a diferença de preço entre um aparelho mais caro e um mais barato.
- **Projeção de 3 Anos:** Gráficos interativos mostrando o gasto acumulado ao longo do tempo.

## 🛠️ Tecnologias Utilizadas
- **Python:** Linguagem principal.
- **Streamlit:** Framework para criação da interface web interativa.
- **Pandas:** Manipulação e análise de dados (ETL).
- **Plotly:** Geração de gráficos dinâmicos.

## 📂 Estrutura de Dados
Os dados utilizados neste projeto são provenientes de fontes públicas oficiais:
- `Itens.csv`: Base de dados de eficiência energética do **INMETRO** (Programa Brasileiro de Etiquetagem).
- `Tarifas.csv`: Dados de tarifas residenciais (B1) das concessionárias reguladas pela **ANEEL**.

## 📦 Como rodar localmente
1. Clone este repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/NOME_DO_REPO.git](https://github.com/SEU_USUARIO/NOME_DO_REPO.git)

 Instale as dependências:


pip install -r requirements.txt

streamlit run app.py


