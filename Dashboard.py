import pandas as pd
import streamlit as st
from datetime import date
import os

# ================================
# CONFIGURAÇÕES INICIAIS
# ================================
st.set_page_config(layout='wide', page_title="Actions Televendas")
st.title('ACTIONS TELEVENDAS :chart_with_upwards_trend:')

# Define o caminho base como a pasta onde este script está salvo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================================
# FUNÇÕES AUXILIARES
# ================================

@st.cache_data
def carregar_dados():
    # Nomes dos arquivos padronizados para letras minúsculas
    arquivo_dados = 'dados_analisados.csv'
    arquivo_hora = 'hora.csv'
    
    # Construção dos caminhos absolutos
    caminho_dados = os.path.join(BASE_DIR, arquivo_dados)
    caminho_hora = os.path.join(BASE_DIR, arquivo_hora)
    
    # Validação de existência física dos arquivos
    if not os.path.exists(caminho_dados):
        st.error(f"Arquivo não encontrado: {arquivo_dados}")
        st.stop()
    if not os.path.exists(caminho_hora):
        st.error(f"Arquivo não encontrado: {arquivo_hora}")
        st.info("Certifique-se de que o arquivo no seu computador/GitHub se chama 'hora.csv' (em minúsculo).")
        st.stop()

    # Leitura dos arquivos CSV
    dados = pd.read_csv(caminho_dados)
    hora = pd.read_csv(caminho_hora)
    
    # 1. TRATAMENTO: Remoção de espaços em branco nos textos
    dados = dados.map(lambda x: x.strip() if isinstance(x, str) else x)
    hora = hora.map(lambda x: x.strip() if isinstance(x, str) else x)
    
    # 2. PADRONIZAÇÃO: Conteúdo em maiúsculo para consistência nos filtros
    if 'SUPERVISOR' in dados.columns:
        dados['SUPERVISOR'] = dados['SUPERVISOR'].astype(str).str.upper()
    
    if 'SUPERVISOR' in hora.columns:
        hora['SUPERVISOR'] = hora['SUPERVISOR'].astype(str).str.upper()
    
    if 'OPERADOR' in hora.columns:
        hora['OPERADOR'] = hora['OPERADOR'].astype(str).str.upper()

    # 3. DATAS: Conversão para formato datetime
    dados['fecha_accion'] = pd.to_datetime(dados['fecha_accion'], errors='coerce')
    hora['DATA'] = pd.to_datetime(hora['DATA'], errors='coerce')
    
    # Remove linhas onde a data é inválida
    dados = dados.dropna(subset=['fecha_accion'])
    hora = hora.dropna(subset=['DATA'])
    
    # Garante que GESTIONES seja numérico
    if 'GESTIONES' in hora.columns:
        hora['GESTIONES'] = pd.to_numeric(hora['GESTIONES'], errors='coerce').fillna(0)
    
    return dados, hora

def color_total(val):
    """Aplica cores às células conforme o valor de produtividade"""
    try:
        val = float(val)
        if val >= 130:
            return 'background-color: #2ecc71; color: white'  # Verde
        elif val < 130:
            return 'background-color: #f1c40f; color: black'  # Amarelo
    except:
        pass
    return ''

# ================================
# PROCESSAMENTO DE DADOS
# ================================
dados, hora = carregar_dados()

# --- PREPARAÇÃO DOS FILTROS ---
hoje = date.today()
datas_disponiveis = sorted(
    set(dados['fecha_accion'].dt.date.unique()) | set(hora['DATA'].dt.date.unique()), 
    reverse=True
)

opcoes_datas = ['Todas as datas'] + [str(d) for d in datas_disponiveis]
todos_supervisores = sorted(set(dados['SUPERVISOR'].dropna().unique()) | set(hora['SUPERVISOR'].dropna().unique()))

# --- SIDEBAR (FILTROS) ---
st.sidebar.header('Filtros')
data_sel = st.sidebar.selectbox('📅 Selecione a Data:', opcoes_datas)
super_sel = st.sidebar.multiselect('👤 Selecione o Supervisor:', options=todos_supervisores)

# Criando cópias para filtrar sem alterar o cache original
df_a = dados.copy()
df_h = hora.copy()

# Lógica de Filtragem por Data
if data_sel != 'Todas as datas':
    dt_alvo = pd.to_datetime(data_sel).date()
    df_a = df_a[df_a['fecha_accion'].dt.date == dt_alvo]
    df_h = df_h[df_h['DATA'].dt.date == dt_alvo]

# Lógica de Filtragem por Supervisor
if super_sel:
    df_a = df_a[df_a['SUPERVISOR'].isin(super_sel)]
    df_h = df_h[df_h['SUPERVISOR'].isin(super_sel)]

# ================================
# INTERFACE DO DASHBOARD
# ================================
col1, col2 = st.columns(2)

with col1:
    st.header("ACTIONS :pushpin:")
    if not df_a.empty:
        # Tenta identificar a coluna de performance (Total ou a última numérica)
        col_ref = 'Total' if 'Total' in df_a.columns else df_a.select_dtypes(include='number').columns[-1]
        st.dataframe(
            df_a.style.map(color_total, subset=[col_ref]), 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.warning("Nenhum dado encontrado para Actions.")

with col2:
    st.header('CRM (HORA A HORA) 💼')
    if not df_h.empty:
        # Agrupamento dinâmico conforme as colunas presentes
        colunas_agrupar = [c for c in ['OPERADOR', 'DATA', 'SUPERVISOR', 'CD'] if c in df_h.columns]
        
        # Consolidação e Ordenação
        resumo_crm = df_h.groupby(colunas_agrupar, as_index=False)['GESTIONES'].sum()
        resumo_crm = resumo_crm.sort_values(['DATA', 'GESTIONES'], ascending=[False, False])

        st.dataframe(
            resumo_crm.style.map(color_total, subset=['GESTIONES']), 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.warning("Nenhum dado encontrado para CRM.")
