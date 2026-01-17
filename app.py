import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Comparador Pro de Ar Condicionado", page_icon="❄️", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .card-produto {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e9ecef;
    }
    .metric-value { font-size: 1.5rem; font-weight: bold; color: #2c3e50; }
    .fonte-dados { font-size: 0.8rem; color: #6c757d; text-align: center; margin-top: 40px; border-top: 1px solid #ddd; padding-top: 10px;}
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE CARREGAMENTO ---
@st.cache_data
def carregar_dados():
    # Verifica arquivos
    if not os.path.exists("dados_limpos.csv") or not os.path.exists("Tarifas.csv"):
        return None, None
    
    # --- CARREGA E LIMPA ITENS ---
    df_i = pd.read_csv("dados_limpos.csv")
    
    # 1. REMOVE DADOS VAZIOS
    df_i = df_i.dropna(subset=['Marca', 'Modelo'])
    
    # 2. LIMPEZA AVANÇADA DE MARCAS (ATUALIZADO)
    def limpar_marca(texto):
        texto = str(texto).upper().strip()
        
        # Passo 1: Corta separadores explícitos de concatenação
        separadores = ['|', '/', '+']
        for sep in separadores:
            texto = texto.split(sep)[0]
            
        # Passo 2: Heurística de Código
        # Se uma palavra tiver NÚMEROS (ex: 'AQ09...', '12000'), assume que é o modelo e corta dali pra frente.
        palavras = texto.split()
        marca_limpa = []
        for p in palavras:
            # Verifica se tem algum dígito na palavra
            if any(char.isdigit() for char in p): 
                break # Para de ler, pois achou o modelo misturado
            marca_limpa.append(p)
        
        return " ".join(marca_limpa).strip()
        
    df_i['Marca'] = df_i['Marca'].apply(limpar_marca)
    
    # Limpeza básica do Modelo
    df_i['Modelo'] = df_i['Modelo'].astype(str).str.strip()
    
    # Cria preço se não existir
    if 'preco' not in df_i.columns:
        df_i['preco'] = 0.0
    
    # --- CARREGA TARIFAS ---
    df_t = pd.read_csv("Tarifas.csv")
    df_t = df_t.dropna(subset=['estado'])
    df_t['estado'] = df_t['estado'].astype(str)
    df_t = df_t.sort_values(by='estado')
    
    return df_i, df_t

df_itens, df_tarifas = carregar_dados()

if df_itens is None or df_tarifas is None:
    st.error("🚨 Arquivos CSV não encontrados.")
    st.stop()

# --- SIDEBAR: CONFIGURAÇÕES ---
with st.sidebar:
    st.header(" Configurações de Energia")
    
    estados_disp = sorted(df_tarifas['estado'].unique())
    estado_sel = st.selectbox("Estado", estados_disp)
    
    distribuidoras = sorted(df_tarifas[df_tarifas['estado'] == estado_sel]['empresa'].unique())
    distribuidora_sel = st.selectbox("Distribuidora", distribuidoras)
    
    bandeira_sel = st.selectbox("Bandeira Tarifária", ["Verde", "Amarela", "Vermelha P1", "Vermelha P2"])
    
    st.divider()
    st.subheader("🕒 Perfil de Uso")
    horas_dia = st.number_input("Horas de uso por dia", min_value=1, max_value=24, value=8)
    dias_mes = st.slider("Dias de uso por mês", 1, 30, 30)

# --- CÁLCULO DA TARIFA ---
try:
    tarifa_base = df_tarifas[
        (df_tarifas['estado'] == estado_sel) & 
        (df_tarifas['empresa'] == distribuidora_sel)
    ]['tarifa'].values[0]
except IndexError:
    tarifa_base = 0.85

adicionais = {"Verde": 0.0, "Amarela": 0.018, "Vermelha P1": 0.044, "Vermelha P2": 0.078}
tarifa_final = tarifa_base + adicionais.get(bandeira_sel, 0)

# --- APP PRINCIPAL ---
st.title("❄️ Comparador Inteligente de Climatização")
st.markdown(f"Tarifa aplicada: **R$ {tarifa_final:.3f}/kWh** ({distribuidora_sel})")
st.divider()

# --- FUNÇÃO DE SELEÇÃO DE PRODUTO ---
def selecionar_produto(label, key_suffix):
    # Filtro de Marca
    marcas = sorted(df_itens['Marca'].unique())
    if not marcas:
        st.warning("Nenhuma marca encontrada.")
        return None
        
    marca = st.selectbox(f"Filtrar Marca ({label})", ["Todas"] + marcas, key=f"marca_{key_suffix}")
    
    df_filt = df_itens.copy()
    if marca != "Todas":
        df_filt = df_filt[df_filt['Marca'] == marca]
    
    # Filtro de BTUs
    df_filt['BTU_Num'] = pd.to_numeric(df_filt['Capacidade de Refrigeração Nominal (Btu/h)'], errors='coerce')
    btus = sorted(df_filt['BTU_Num'].dropna().unique())
    
    if not btus:
        st.warning("Sem dados para essa seleção.")
        return None

    btu_sel = st.selectbox(f"Filtrar BTU ({label})", ["Todos"] + [f"{b:.0f}" for b in btus], key=f"btu_{key_suffix}")
    
    if btu_sel != "Todos":
        df_filt = df_filt[df_filt['BTU_Num'] == float(btu_sel)]
        
    # Seleção Final do Modelo
    modelos = sorted(df_filt['Modelo'].unique())
    
    if len(modelos) == 0:
        st.warning("Nenhum modelo encontrado com esses filtros.")
        return None

    modelo_escolhido = st.selectbox(f"Selecione o Modelo {label}", modelos, key=f"mod_{key_suffix}")
    
    resultado = df_filt[df_filt['Modelo'] == modelo_escolhido]
    
    if resultado.empty:
        return None
        
    return resultado.iloc[0]

# --- COLUNAS DE COMPARAÇÃO ---
col_a, col_b = st.columns(2)
custo_mensal_a = 0
custo_mensal_b = 0
preco_a = 0
preco_b = 0
valid_a = False
valid_b = False

# --- PRODUTO A ---
with col_a:
    st.markdown("###  Opção A")
    try:
        item_a = selecionar_produto("A", "a")
        
        if item_a is not None:
            valid_a = True
            with st.container(border=True):
                preco_a = st.number_input("Preço do Aparelho (R$)", value=float(item_a.get('preco', 0)), key="price_a", step=50.0)
                
                try:
                    kwh_anual = float(item_a['Consumo Anual de Energia (kWh)'])
                except:
                    kwh_anual = 0
                    
                st.caption(f"Marca: {item_a['Marca']} | BTU: {item_a['Capacidade de Refrigeração Nominal (Btu/h)']}")
                
                consumo_kwh_mensal_a = (kwh_anual / 365) * horas_dia * dias_mes
                custo_mensal_a = consumo_kwh_mensal_a * tarifa_final
                st.metric("Custo Mensal Estimado", f"R$ {custo_mensal_a:.2f}")
    except Exception as e:
        st.error(f"Erro ao carregar A: {e}")

# --- PRODUTO B ---
with col_b:
    st.markdown("###  Opção B")
    try:
        item_b = selecionar_produto("B", "b")
        
        if item_b is not None:
            valid_b = True
            with st.container(border=True):
                preco_b = st.number_input("Preço do Aparelho (R$)", value=float(item_b.get('preco', 0)), key="price_b", step=50.0)
                
                try:
                    kwh_anual = float(item_b['Consumo Anual de Energia (kWh)'])
                except:
                    kwh_anual = 0
                    
                st.caption(f"Marca: {item_b['Marca']} | BTU: {item_b['Capacidade de Refrigeração Nominal (Btu/h)']}")
                
                consumo_kwh_mensal_b = (kwh_anual / 365) * horas_dia * dias_mes
                custo_mensal_b = consumo_kwh_mensal_b * tarifa_final
                st.metric("Custo Mensal Estimado", f"R$ {custo_mensal_b:.2f}")
    except Exception as e:
        st.error(f"Erro ao carregar B: {e}")

# --- ANÁLISE ---
st.divider()

if valid_a and valid_b:
    st.subheader(" Análise Financeira")
    
    diff_mensal = abs(custo_mensal_a - custo_mensal_b)
    diff_preco = abs(preco_a - preco_b)
    mais_economico = "A" if custo_mensal_a < custo_mensal_b else "B"
    mais_caro_compra = "A" if preco_a > preco_b else "B"
    
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.info(f" Economia mensal escolhendo a Opção {mais_economico}: **R$ {diff_mensal:.2f}**")
        
        if diff_mensal > 0 and diff_preco > 0:
            if mais_economico == mais_caro_compra:
                meses_payback = diff_preco / diff_mensal
                if meses_payback < 120:
                    anos = int(meses_payback // 12)
                    meses = int(meses_payback % 12)
                    st.success(f" **Payback:** O investimento se paga em **{anos} anos e {meses} meses**.")
                else:
                    st.warning("O retorno financeiro demora mais de 10 anos.")
            else:
                st.success(f" O modelo {mais_economico} é mais barato e mais econômico!")
        elif diff_mensal == 0:
            st.warning("Consumo idêntico.")
            
    with c2:
        meses_proj = list(range(0, 37))
        custo_acum_a = [preco_a + (custo_mensal_a * m) for m in meses_proj]
        custo_acum_b = [preco_b + (custo_mensal_b * m) for m in meses_proj]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=meses_proj, y=custo_acum_a, mode='lines', name='Opção A'))
        fig.add_trace(go.Scatter(x=meses_proj, y=custo_acum_b, mode='lines', name='Opção B'))
        fig.update_layout(title="Custo Acumulado (3 Anos)", xaxis_title="Meses", yaxis_title="R$ Total", height=300)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class='fonte-dados'>
    <p><strong>Fontes dos Dados:</strong></p>
    <p> Tarifas: ANEEL (Agência Nacional de Energia Elétrica).</p>
    <p> Eficiência: INMETRO (Programa Brasileiro de Etiquetagem).</p>
</div>

""", unsafe_allow_html=True)
