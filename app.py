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

# --- ESTILIZAÇÃO CSS (Botões Menores e Harmônicos) ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .main { background-color: #f8f9fa; }
    
    /* Estilo dos Botões de Loja - Mais compactos e elegantes */
    .btn-store {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 6px 0; /* Menor altura */
        margin-top: 4px;
        border-radius: 4px; /* Bordas levemente arredondadas */
        text-decoration: none !important;
        font-weight: 600;
        font-size: 0.8rem; /* Fonte menor */
        transition: all 0.2s;
        border: 1px solid transparent;
        color: white !important;
    }
    
    .btn-store:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }

    /* Cores das Marcas (Suavizadas para combinar, mas mantendo identidade) */
    .btn-amazon {
        background-color: #F90; /* Laranja Amazon clássico */
        color: #111 !important; /* Texto escuro para contraste */
    }
    
    .btn-magalu {
        background-color: #0086FF; /* Azul Magalu */
    }
    
    .btn-ml {
        background-color: #FFE600; /* Amarelo ML */
        color: #2D3277 !important; /* Azul ML para contraste */
    }
    
    /* Input e Métricas */
    .stNumberInput input { font-weight: bold; }
    
    .footer-legal {
        font-size: 0.7rem; color: #868e96; text-align: center; 
        margin-top: 60px; padding-top: 20px; border-top: 1px solid #dee2e6;
    }
    
    /* Caixa de Recomendação de BTU */
    .btu-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 10px;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #0d47a1;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
