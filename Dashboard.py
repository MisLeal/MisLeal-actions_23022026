import pandas as pd
import streamlit as st
from datetime import date

# ================================
# CONFIGURAÇÕES INICIAIS
# ================================
st.set_page_config(layout='wide', page_title="Actions Televendas")
st.title('ACTIONS TELEVENDAS :chart_with_upwards_trend:')

# ================================
# FUNÇÕES AUXILIARES
# ================================

@st.cache_data
def carregar_dados():
    # Leitura dos arquivos
    dados = pd.read_csv('dados_analisados.csv')
    hora = pd.read_csv('HORA.csv')
    
    # 1. TRATAMENTO GLOBAL: Trim (remover espaços vazios)
    dados = dados.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    hora = hora.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # 2. PADRONIZAÇÃO: Maiúsculas para evitar 'Joao' vs 'JOAO'
    if 'SUPERVISOR' in dados.columns:
        dados['SUPERVISOR'] = dados['SUPERVISOR'].str.upper()
    
    if 'SUPERVISOR' in hora.columns:
        hora['SUPERVISOR'] = hora['SUPERVISOR'].str.upper()
    
    if 'NOME' in hora.columns:
        hora['NOME'] = hora['NOME'].str.upper()

    # 3. DATAS: Conversão e remoção de inválidos
    dados['fecha_accion'] = pd.to_datetime(dados['fecha_accion'], errors='coerce')
    hora['DATA'] = pd.to_datetime(hora['DATA'], errors='coerce')
    
    dados = dados.dropna(subset=['fecha_accion'])
    hora = hora.dropna(subset=['DATA'])
    
    return dados, hora

def color_total(val):
    try:
        val = float(val)
        if val > 130:
            return 'background-color: green; color: white'
        elif val < 130:
            return 'background-color: yellow; color: black'
    except:
        pass
    return ''

# ================================
# CARREGANDO DADOS
# ================================
dados, hora = carregar_dados()

# ================================
# PREPARANDO FILTROS
# ================================
hoje = date.today()

datas_dados = dados[dados['fecha_accion'].dt.date <= hoje]['fecha_accion'].dt.date.unique()
datas_hora = hora[hora['DATA'].dt.date <= hoje]['DATA'].dt.date.unique()
datas_disponiveis = sorted(set(datas_dados) | set(datas_hora), reverse=True)

opcoes_datas = ['Todas as datas'] + [str(data) for data in datas_disponiveis]
todos_supervisores = sorted(set(dados['SUPERVISOR'].dropna().unique()) | set(hora['SUPERVISOR'].dropna().unique()))

# ================================
# SIDEBAR - FILTROS
# ================================
st.sidebar.header('Filtros')
data_selecionada = st.sidebar.selectbox('📅 Selecione uma data:', opcoes_datas, index=0)
supervisores_selecionados = st.sidebar.multiselect(
    '👤 Selecione Supervisor(es):',
    options=todos_supervisores,
    default=[]
)


dados_filtrados = dados.copy()
hora_filtrada = hora.copy()

if data_selecionada != 'Todas as datas':
    data_filtro = pd.to_datetime(data_selecionada).date()
    dados_filtrados = dados_filtrados[dados_filtrados['fecha_accion'].dt.date == data_filtro]
    hora_filtrada = hora_filtrada[hora_filtrada['DATA'].dt.date == data_filtro]

if supervisores_selecionados:
    dados_filtrados = dados_filtrados[dados_filtrados['SUPERVISOR'].isin(supervisores_selecionados)]
    hora_filtrada = hora_filtrada[hora_filtrada['SUPERVISOR'].isin(supervisores_selecionados)]


coluna1, coluna2 = st.columns(2)

with coluna1:
    st.header("ACTIONS :pushpin:")
    if not dados_filtrados.empty:
        # Consolidação de Actions por Supervisor/Data se necessário
        # (Aqui você pode adicionar um groupby similar ao da coluna 2 se houver duplicatas)
        st.dataframe(
            dados_filtrados.style.applymap(color_total, subset=['Total']),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Nenhum dado encontrado para ACTIONS.")

with coluna2:import pandas as pd
import streamlit as st
from datetime import date
import os

# ================================
# CONFIGURAÇÕES INICIAIS
# ================================
st.set_page_config(layout='wide', page_title="Actions Televendas")
st.title('ACTIONS TELEVENDAS :chart_with_upwards_trend:')

# Identifica o caminho da pasta onde o Dashboard.py está
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================================
# FUNÇÕES AUXILIARES
# ================================

@st.cache_data
def carregar_dados():
    # Caminhos absolutos para evitar o FileNotFoundError no Streamlit Cloud
    caminho_dados = os.path.join(BASE_DIR, 'dados_analisados.csv')
    caminho_hora = os.path.join(BASE_DIR, 'HORA.csv')
    
    # Verifica se os arquivos realmente existem antes de tentar ler
    if not os.path.exists(caminho_dados) or not os.path.exists(caminho_hora):
        st.error(f"⚠️ Erro: Arquivos CSV não encontrados na pasta do projeto!")
        st.info(f"Certifique-se de que 'dados_analisados.csv' e 'HORA.csv' estão na raiz do seu GitHub.")
        st.stop()

    # Leitura dos arquivos
    dados = pd.read_csv(caminho_dados)
    hora = pd.read_csv(caminho_hora)
    
    # 1. TRATAMENTO GLOBAL: Trim (remover espaços vazios)
    # .map é o substituto moderno do .applymap para DataFrames
    dados = dados.map(lambda x: x.strip() if isinstance(x, str) else x)
    hora = hora.map(lambda x: x.strip() if isinstance(x, str) else x)
    
    # 2. PADRONIZAÇÃO: Maiúsculas para evitar 'Joao' vs 'JOAO'
    if 'SUPERVISOR' in dados.columns:
        dados['SUPERVISOR'] = dados['SUPERVISOR'].str.upper()
    
    if 'SUPERVISOR' in hora.columns:
        hora['SUPERVISOR'] = hora['SUPERVISOR'].str.upper()
    
    if 'NOME' in hora.columns:
        hora['NOME'] = hora['NOME'].str.upper()

    # 3. DATAS: Conversão e remoção de inválidos
    dados['fecha_accion'] = pd.to_datetime(dados['fecha_accion'], errors='coerce')
    hora['DATA'] = pd.to_datetime(hora['DATA'], errors='coerce')
    
    dados = dados.dropna(subset=['fecha_accion'])
    hora = hora.dropna(subset=['DATA'])
    
    return dados, hora

def color_total(val):
    try:
        val = float(val)
        if val > 130:
            return 'background-color: green; color: white'
        elif val < 130:
            return 'background-color: yellow; color: black'
    except:
        pass
    return ''

# ================================
# CARREGANDO DADOS
# ================================
# Tenta carregar os dados. Se falhar, o st.stop() dentro da função interrompe aqui.
dados, hora = carregar_dados()

# ================================
# PREPARANDO FILTROS
# ================================
hoje = date.today()

datas_dados = dados[dados['fecha_accion'].dt.date <= hoje]['fecha_accion'].dt.date.unique()
datas_hora = hora[hora['DATA'].dt.date <= hoje]['DATA'].dt.date.unique()
datas_disponiveis = sorted(set(datas_dados) | set(datas_hora), reverse=True)

opcoes_datas = ['Todas as datas'] + [str(data) for data in datas_disponiveis]
todos_supervisores = sorted(set(dados['SUPERVISOR'].dropna().unique()) | set(hora['SUPERVISOR'].dropna().unique()))

# ================================
# SIDEBAR - FILTROS
# ================================
st.sidebar.header('Filtros')
data_selecionada = st.sidebar.selectbox('📅 Selecione uma data:', opcoes_datas, index=0)
supervisores_selecionados = st.sidebar.multiselect(
    '👤 Selecione Supervisor(es):',
    options=todos_supervisores,
    default=[]
)

# Filtros Lógicos
dados_filtrados = dados.copy()
hora_filtrada = hora.copy()

if data_selecionada != 'Todas as datas':
    data_filtro = pd.to_datetime(data_selecionada).date()
    dados_filtrados = dados_filtrados[dados_filtrados['fecha_accion'].dt.date == data_filtro]
    hora_filtrada = hora_filtrada[hora_filtrada['DATA'].dt.date == data_filtro]

if supervisores_selecionados:
    dados_filtrados = dados_filtrados[dados_filtrados['SUPERVISOR'].isin(supervisores_selecionados)]
    hora_filtrada = hora_filtrada[hora_filtrada['SUPERVISOR'].isin(supervisores_selecionados)]

# ================================
# EXIBIÇÃO DO DASHBOARD
# ================================
coluna1, coluna2 = st.columns(2)

with coluna1:
    st.header("ACTIONS :pushpin:")
    if not dados_filtrados.empty:
        # Nota: Ajustado applymap para map aqui também para seguir padrão Pandas 2.x
        st.dataframe(
            dados_filtrados.style.map(color_total, subset=['Total']),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Nenhum dado encontrado para ACTIONS.")

with coluna2:
    st.header('CRM 💼')
    if not hora_filtrada.empty:
        hora_consolidada = hora_filtrada.groupby(
            ['NOME', 'DATA', 'SUPERVISOR', 'CONTATO DIRETO'], 
            as_index=False
        )['GESTIONES'].sum()

        hora_consolidada = hora_consolidada.sort_values(['DATA', 'GESTIONES'], ascending=[False, False])

        st.dataframe(
            hora_consolidada.style.map(color_total, subset=['GESTIONES']),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Nenhum dado encontrado para CRM.")
    st.header('CRM 💼')
    if not hora_filtrada.empty:

        hora_consolidada = hora_filtrada.groupby(
            ['NOME', 'DATA', 'SUPERVISOR', 'CONTATO DIRETO'], 
            as_index=False
        )['GESTIONES'].sum()


        hora_consolidada = hora_consolidada.sort_values(['DATA', 'GESTIONES'], ascending=[False, False])

        st.dataframe(
            hora_consolidada.style.applymap(color_total, subset=['GESTIONES']),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Nenhum dado encontrado para CRM.")