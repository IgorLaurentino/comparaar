import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Comparador de Ar Condicionado", page_icon="❄️", layout="wide")

# ==========================================
#  CONFIGURAÇÃO DE AFILIADO (SECRETS)
try:
    AMAZON_TAG = st.secrets["AMAZON_TAG"]
except:
    st.error("⚠️ ERRO: ID de Afiliado não configurado! Configure nos 'Secrets'.")
    st.stop()
# ==========================================

# --- ESTILOS CSS ---
st.markdown("""
<style>
    /* Esconde menus do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Estilos Gerais */
    .main { background-color: #f8f9fa; }
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    .amazon-btn { background-color: #FF9900 !important; color: black !important; border: none; }
    
    /* Rodapé com Aviso Legal */
    .footer-legal {
        font-size: 0.75rem; color: #6c757d; text-align: center; 
        margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO GERADORA DE LINK AMAZON ---
def gerar_link_amazon(marca, modelo):
    termo_busca = f"Ar condicionado {marca} {modelo}"
    termo_formatado = termo_busca.replace(" ", "+")
    return f"https://www.amazon.com.br/s?k={termo_formatado}&tag={AMAZON_TAG}"

# --- CARREGAMENTO DE DADOS ---
@st.cache_data
def carregar_dados():
    if not os.path.exists("dados_limpos.csv") or not os.path.exists("Tarifas.csv"):
        return None, None
    
    df_i = pd.read_csv("dados_limpos.csv")
    mapa = {'Capacidade de Refrigeração Nominal (Btu/h)': 'BTU', 'Consumo Anual de Energia (kWh)': 'Consumo'}
    df_i = df_i.rename(columns=mapa)
    
    if not {'Marca', 'Modelo', 'BTU', 'Consumo'}.issubset(df_i.columns): return None, None
    
    df_i = df_i.dropna(subset=['Marca', 'Modelo'])
    
    def limpar_marca(texto):
        texto = str(texto).upper().strip()
        for sep in ['|', '/', '+']: texto = texto.split(sep)[0]
        return " ".join([p for p in texto.split() if not any(c.isdigit() for c in p)]).strip()
        
    df_i['Marca'] = df_i['Marca'].apply(limpar_marca)
    df_i['Modelo'] = df_i['Modelo'].astype(str).str.strip()
    if 'preco' not in df_i.columns: df_i['preco'] = 0.0
    
    df_t = pd.read_csv("Tarifas.csv")
    df_t = df_t.dropna(subset=['estado'])
    df_t['estado'] = df_t['estado'].astype(str)
    
    return df_i, df_t

df_itens, df_tarifas = carregar_dados()

if df_itens is None:
    st.error("Erro: Arquivos CSV não encontrados.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configurações")
    lista_estados = ["Selecione"] + sorted(df_tarifas['estado'].unique())
    est_sel = st.selectbox("Estado", lista_estados)
    
    if est_sel == "Selecione":
        dist_sel = None
        band_sel = "Verde"
        st.warning("👈 Comece selecionando seu Estado.")
    else:
        lista_dist = ["Selecione"] + sorted(df_tarifas[df_tarifas['estado'] == est_sel]['empresa'].unique())
        dist_sel = st.selectbox("Distribuidora", lista_dist)
        band_sel = st.selectbox("Bandeira Tarifária", ["Verde", "Amarela", "Vermelha P1", "Vermelha P2"])
        
    st.divider()
    horas = st.number_input("Horas de uso/dia", 1, 24, 8)
    dias = st.slider("Dias de uso/mês", 1, 30, 30)

if est_sel == "Selecione" or dist_sel == "Selecione":
    st.title(" Comparador Inteligente de Climatização")
    st.info(" Bem-vindo! Selecione seu Estado e Distribuidora na barra lateral para começar.")
    
    # Aviso legal mesmo na tela inicial (Segurança)
    st.markdown("""
    <div class='footer-legal'>
        Participamos do Programa de Associados da Amazon Services LLC, um programa de afiliados projetado para fornecer um meio de ganharmos taxas vinculando à Amazon.com.br e sites afiliados.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- CÁLCULO TARIFA ---
try:
    base = df_tarifas[(df_tarifas['estado'] == est_sel) & (df_tarifas['empresa'] == dist_sel)]['tarifa'].values[0]
except: base = 0.85
add = {"Verde": 0, "Amarela": 0.018, "Vermelha P1": 0.044, "Vermelha P2": 0.078}
tarifa = base + add.get(band_sel, 0)

st.title("❄️ Comparador Inteligente de Climatização")
st.caption(f"Tarifa calculada: R$ {tarifa:.3f}/kWh ({dist_sel})")
st.divider()

# --- BLOCO DE PRODUTO ---
def bloco_produto(label, key):
    st.markdown(f"### Opção {label}")
    marcas = ["Selecione"] + sorted(df_itens['Marca'].unique())
    marca = st.selectbox(f"Marca {label}", marcas, key=f"m{key}")
    
    if marca == "Selecione": return None
    
    df_m = df_itens[df_itens['Marca'] == marca].copy()
    df_m['BTU_N'] = pd.to_numeric(df_m['BTU'], errors='coerce')
    btus = sorted(df_m['BTU_N'].dropna().unique())
    lista_btus = ["Selecione"] + btus
    btu_val = st.selectbox(f"BTU {label}", lista_btus, format_func=lambda x: f"{int(x)}" if x != "Selecione" else x, key=f"b{key}")
    
    if btu_val == "Selecione": return None
    
    df_b = df_m[df_m['BTU_N'] == btu_val]
    mods = sorted(df_b['Modelo'].unique())
    lista_mods = ["Selecione"] + mods
    modelo = st.selectbox(f"Modelo {label}", lista_mods, key=f"mod{key}")
    
    if modelo == "Selecione": return None
    
    item = df_b[df_b['Modelo'] == modelo].iloc[0]
    link_amazon = gerar_link_amazon(item['Marca'], item['Modelo'])
    st.link_button(f"🛒 Ver Preço na Amazon ({label})", link_amazon, type="primary")
    
    preco = st.number_input(f"Preço Encontrado {label} (R$)", 0.0, step=50.0, key=f"p{key}")
    cons_mensal = (item['Consumo']/365) * horas * dias
    custo_mensal = cons_mensal * tarifa
    st.metric("Custo Energia/Mês", f"R$ {custo_mensal:.2f}")
    
    return {'p': preco, 'c': custo_mensal, 'nome': f"{marca} {modelo}", 'link': link_amazon}

c1, c2 = st.columns(2)
with c1: res_a = bloco_produto("A", "a")
with c2: res_b = bloco_produto("B", "b")

# --- ANÁLISE ---
st.divider()

if res_a is not None and res_b is not None:
    st.subheader("A melhor opção")
    col_res1, col_res2 = st.columns([1,1])
    
    sao_iguais = (res_a['nome'] == res_b['nome'])
    empate = (abs(res_a['c'] - res_b['c']) < 0.01) and (abs(res_a['p'] - res_b['p']) < 0.01)
    
    with col_res1:
        if sao_iguais:
            st.warning("⚠️ Mesmo modelo selecionado.")
        elif empate:
            st.info("⚖️ Empate Técnico!")
        else:
            diff = abs(res_a['c'] - res_b['c'])
            venc = "A" if res_a['c'] < res_b['c'] else "B"
            link_venc = res_a['link'] if venc == "A" else res_b['link']
            
            st.success(f"Opção **{venc}** economiza **R$ {diff:.2f}/mês**.")
            st.link_button(f"Comprar Opção {venc} na Amazon", link_venc)

    with col_res2:
        meses = list(range(37))
        va = [res_a['p'] + (res_a['c']*m) for m in meses]
        vb = [res_b['p'] + (res_b['c']*m) for m in meses]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=meses, y=va, name="Opção A"))
        fig.add_trace(go.Scatter(x=meses, y=vb, name="Opção B"))
        fig.update_layout(title="Gasto Total (3 Anos)", height=300, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, width="stretch")
else:
    st.info("👆 Preencha as opções acima para comparar.")

# --- RODAPÉ OFICIAL  ---
st.markdown("""
<div class='footer-legal'>
    <p><strong>Dados Técnicos:</strong> INMETRO | <strong>Tarifas:</strong> ANEEL</p>
    <p>Participamos do Programa de Associados da Amazon Services LLC, um programa de afiliados projetado para fornecer um meio de ganharmos taxas vinculando à Amazon.com.br e sites afiliados.</p>
</div>
""", unsafe_allow_html=True)

