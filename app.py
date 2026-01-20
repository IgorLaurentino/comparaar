import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Comparador de Ar Condicionado", page_icon="❄️", layout="wide")

# --- GESTÃO DE SEGREDOS ---
try:
    AMAZON_TAG = st.secrets.get("AMAZON_TAG", "")
    MAGALU_ID = st.secrets.get("MAGALU_ID", "") 
    ML_TAG = st.secrets.get("ML_TAG", "")
except:
    st.error("Erro de configuração: IDs de afiliado não encontrados nos Secrets.")
    st.stop()

# --- ESTILIZAÇÃO CSS (VISUAL HARMONIZADO) ---
st.markdown("""
<style>
  
    
    .main { background-color: #f8f9fa; }
    
    /* Estilos dos Botões Personalizados */
    .btn-store {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 6px 12px; /* Menor padding = botão mais fino */
        margin-top: 5px;
        border-radius: 8px;
        text-decoration: none !important;
        font-weight: 600;
        font-size: 0.85rem; /* Fonte levemente menor */
        transition: all 0.2s ease;
        border: 1px solid transparent;
        color: white !important;
    }
    
    .btn-store:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        filter: brightness(1.05);
    }

    /* Cores das Marcas (Tons mais harmoniosos) */
    .btn-amazon {
        background-color: #FF9900; 
        color: #232F3E !important; /* Texto escuro para contraste no laranja */
    }
    
    .btn-magalu {
        background-color: #0086FF; 
    }
    
    .btn-ml {
        background-color: #FFE600;
        color: #2D3277 !important; /* Texto azul para contraste no amarelo */
    }
    
    /* Caixa de Recomendação de BTU */
    .btu-box {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 20px;
        font-size: 0.9rem;
        color: #0d47a1;
    }
    
    .footer-legal {
        font-size: 0.7rem; color: #868e96; text-align: center; 
        margin-top: 60px; padding-top: 20px; border-top: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE GERAÇÃO DE LINKS ---
def gerar_link_amazon(marca, modelo):
    termo = f"Ar condicionado {marca} {modelo}".replace(" ", "+")
    tag = f"&tag={AMAZON_TAG}" if AMAZON_TAG else ""
    return f"https://www.amazon.com.br/s?k={termo}{tag}"

def gerar_link_magalu(marca, modelo):
    termo = f"Ar condicionado {marca} {modelo}".replace(" ", "+")
    base_url = f"https://www.magazinevoce.com.br/magazine{MAGALU_ID}/busca/" if MAGALU_ID else "https://www.magazineluiza.com.br/busca/"
    return f"{base_url}{termo}/"

def gerar_link_mercadolivre(marca, modelo):
    termo = f"Ar condicionado {marca} {modelo}".replace(" ", "-")
    return f"https://lista.mercadolivre.com.br/{termo}"

# --- CARREGAMENTO DE DADOS ---
@st.cache_data
def carregar_dados():
    if not os.path.exists("dados_limpos.csv") or not os.path.exists("Tarifas.csv"):
        return None, None
    
    df_i = pd.read_csv("dados_limpos.csv")
    mapa_cols = {'Capacidade de Refrigeração Nominal (Btu/h)': 'BTU', 'Consumo Anual de Energia (kWh)': 'Consumo'}
    df_i = df_i.rename(columns=mapa_cols)
    
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
    st.error("Erro crítico: Dados não encontrados.")
    st.stop()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Parâmetros")
    
    lista_estados = ["Selecione"] + sorted(df_tarifas['estado'].unique())
    est_sel = st.selectbox("Estado", lista_estados)
    
    if est_sel == "Selecione":
        dist_sel = None
        band_sel = "Verde"
    else:
        lista_dist = ["Selecione"] + sorted(df_tarifas[df_tarifas['estado'] == est_sel]['empresa'].unique())
        dist_sel = st.selectbox("Distribuidora", lista_dist)
        band_sel = st.selectbox("Bandeira Tarifária", ["Verde", "Amarela", "Vermelha P1", "Vermelha P2"])
        
    st.divider()
    st.subheader("Perfil de Uso")
    
    # --- NOVO: CÁLCULO DE BTU ---
    area_m2 = st.number_input("Tamanho do cômodo (m²)", 5, 100, 12, help="Área aproximada do ambiente onde o ar será instalado.")
    
    # Regra simples: 600 BTU/m² (base) + fator sol/pessoas. Simplificado para 700 médio.
    btu_estimado = area_m2 * 700
    
    # Arredonda para tamanhos comerciais comuns (9k, 12k, 18k, 24k)
    tamanhos_comuns = [9000, 12000, 18000, 24000, 30000]
    btu_recomendado = min(tamanhos_comuns, key=lambda x: abs(x - btu_estimado))
    if btu_estimado > 30000: btu_recomendado = 30000 # Teto simples
    
    st.markdown(f"""
    <div class='btu-box'>
        <b>💡 Recomendação:</b><br>
        Para <b>{area_m2}m²</b>, sugerimos um modelo de aproximadamente <b>{btu_recomendado} BTUs</b>.
    </div>
    """, unsafe_allow_html=True)
    
    horas = st.number_input("Horas/dia", 1, 24, 8)
    dias = st.slider("Dias/mês", 1, 30, 30)

# Tela inicial
if est_sel == "Selecione" or dist_sel == "Selecione":
    st.title("❄️ Comparador de Climatização")
    st.write("Configure os parâmetros de energia na barra lateral para iniciar a comparação.")
    st.markdown("<div class='footer-legal'>Ferramenta independente. Participamos do Programa de Associados da Amazon Services LLC. Links podem gerar comissão.</div>", unsafe_allow_html=True)
    st.stop()

# --- CÁLCULO TARIFA ---
try:
    base = df_tarifas[(df_tarifas['estado'] == est_sel) & (df_tarifas['empresa'] == dist_sel)]['tarifa'].values[0]
except: base = 0.85
adicionais = {"Verde": 0, "Amarela": 0.018, "Vermelha P1": 0.044, "Vermelha P2": 0.078}
tarifa = base + adicionais.get(band_sel, 0)

st.title("❄️ Comparador de Climatização")
st.caption(f"Tarifa vigente: R$ {tarifa:.3f}/kWh ({dist_sel})")
st.divider()

# --- FUNÇÃO DE RENDERIZAÇÃO DE BOTÕES (REUTILIZÁVEL) ---
def renderizar_botoes_lojas(marca, modelo):
    l_az = gerar_link_amazon(marca, modelo)
    l_ml = gerar_link_mercadolivre(marca, modelo)
    l_mg = gerar_link_magalu(marca, modelo)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<a href="{l_az}" target="_blank" class="btn-store btn-amazon">Amazon</a>', unsafe_allow_html=True)
    with c2: st.markdown(f'<a href="{l_ml}" target="_blank" class="btn-store btn-ml">M. Livre</a>', unsafe_allow_html=True)
    with c3: st.markdown(f'<a href="{l_mg}" target="_blank" class="btn-store btn-magalu">Magalu</a>', unsafe_allow_html=True)
    
    return l_az # Retorna link amazon principal se precisar

# --- COMPONENTE DE PRODUTO ---
def renderizar_bloco_produto(label, key_suffix):
    st.markdown(f"### Opção {label}")
    
    marcas = ["Selecione"] + sorted(df_itens['Marca'].unique())
    marca = st.selectbox(f"Marca", marcas, key=f"m{key_suffix}", label_visibility="collapsed")
    if marca == "Selecione": return None
    
    df_m = df_itens[df_itens['Marca'] == marca].copy()
    df_m['BTU_N'] = pd.to_numeric(df_m['BTU'], errors='coerce')
    btus = sorted(df_m['BTU_N'].dropna().unique())
    lista_btus = ["Selecione"] + btus
    btu_val = st.selectbox(f"BTU", lista_btus, format_func=lambda x: f"{int(x)} BTU" if x != "Selecione" else x, key=f"b{key_suffix}", label_visibility="collapsed")
    if btu_val == "Selecione": return None
    
    df_b = df_m[df_m['BTU_N'] == btu_val]
    mods = sorted(df_b['Modelo'].unique())
    lista_mods = ["Selecione"] + mods
    modelo = st.selectbox(f"Modelo", lista_mods, key=f"mod{key_suffix}", label_visibility="collapsed")
    if modelo == "Selecione": return None
    
    item = df_b[df_b['Modelo'] == modelo].iloc[0]
    
    # Renderiza os 3 botões
    st.caption("Verificar preço:")
    link_principal = renderizar_botoes_lojas(item['Marca'], item['Modelo'])
    
    st.divider()
    
    preco = st.number_input(f"Preço (R$)", 0.0, step=50.0, key=f"p{key_suffix}")
    cons_mensal = (item['Consumo']/365) * horas * dias
    custo_mensal = cons_mensal * tarifa
    st.metric("Estimativa Mensal", f"R$ {custo_mensal:.2f}")
    
    return {'p': preco, 'c': custo_mensal, 'nome': f"{marca} {modelo}", 'marca': item['Marca'], 'modelo': item['Modelo']}

col_a, col_b = st.columns(2)
with col_a: dados_a = renderizar_bloco_produto("A", "a")
with col_b: dados_b = renderizar_bloco_produto("B", "b")

# --- ANÁLISE COMPARATIVA ---
st.divider()

if dados_a and dados_b:
    st.subheader("Análise Financeira")
    col_res1, col_res2 = st.columns([1,1])
    
    sao_iguais = (dados_a['nome'] == dados_b['nome'])
    diff_custo = abs(dados_a['c'] - dados_b['c'])
    diff_preco = abs(dados_a['p'] - dados_b['p'])
    empate = (diff_custo < 0.01) and (diff_preco < 0.01)
    
    with col_res1:
        if sao_iguais:
            st.warning("Modelos idênticos selecionados.")
        elif empate:
            st.info("Empate técnico em custo e eficiência.")
        else:
            venc = "A" if dados_a['c'] < dados_b['c'] else "B"
            dados_vencedor = dados_a if venc == "A" else dados_b
            
            st.success(f"A Opção **{venc}** apresenta maior eficiência energética.")
            st.write(f"Economia estimada: **R$ {diff_custo:.2f}/mês**.")
            
            if diff_custo > 0:
                projecao_5_anos = diff_custo * 60
                st.write(f"Projeção de economia (5 anos): **R$ {projecao_5_anos:.2f}**")
            
            st.markdown("---")
            st.write("**Compre a melhor opção:**")
            # Renderiza os botões novamente para o vencedor
            renderizar_botoes_lojas(dados_vencedor['marca'], dados_vencedor['modelo'])

    with col_res2:
        meses = list(range(37))
        prog_a = [dados_a['p'] + (dados_a['c'] * m) for m in meses]
        prog_b = [dados_b['p'] + (dados_b['c'] * m) for m in meses]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=meses, y=prog_a, name="Opção A", line=dict(width=3)))
        fig.add_trace(go.Scatter(x=meses, y=prog_b, name="Opção B", line=dict(width=3)))
        
        fig.update_layout(
            title="Custo Total Acumulado",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, width="stretch")

else:
    st.info("Preencha ambas as opções acima para visualizar a análise comparativa.")

# --- RODAPÉ ---
st.markdown("""
<div class='footer-legal'>
    <p>Fonte dos Dados: INMETRO (Eficiência) e ANEEL (Tarifas).</p>
    <p>Participamos do Programa de Associados da Amazon Services LLC. Links apresentados podem gerar comissão sem custo adicional ao usuário.</p>
</div>
""", unsafe_allow_html=True)

