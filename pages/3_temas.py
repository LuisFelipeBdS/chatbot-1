"""
Página de Gerenciamento de Temas
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import carregar_temas, carregar_pesos, carregar_estudo
from utils.styles import inject_css, render_main_header, render_progress_bar
from core.priorizador_enamed import PriorizadorENAMED
from core.algoritmo_sugestao import AlgoritmoSugestao

st.set_page_config(
    page_title="Temas - Plataforma de Estudos",
    page_icon="📚",
    layout="wide"
)

# Injetar CSS
inject_css()

# Header
st.markdown(
    render_main_header("📚 Gerenciamento de Temas", "Explore todos os temas por grande área"),
    unsafe_allow_html=True
)

# Carregar dados
temas = carregar_temas()
pesos = carregar_pesos()
estudo = carregar_estudo()

priorizador = PriorizadorENAMED()
algoritmo = AlgoritmoSugestao()

# Filtros
col1, col2 = st.columns(2)

with col1:
    areas_disponiveis = list(temas.get("grandes_areas", {}).keys())
    area_selecionada = st.selectbox(
        "Filtrar por Grande Área",
        options=["Todas"] + areas_disponiveis
    )

with col2:
    filtro_yield = st.selectbox(
        "Filtrar por Classificação",
        options=["Todos", "High-Yield 🔥", "Normal", "Low-Yield"]
    )

st.markdown("---")

# Mostrar temas
for area, dados in temas.get("grandes_areas", {}).items():
    if area_selecionada != "Todas" and area != area_selecionada:
        continue
    
    peso_area = pesos["pesos_areas"].get(area, 0)
    
    with st.expander(f"📁 {area} (Peso ENAMED: {peso_area * 100:.1f}%)", expanded=(area_selecionada != "Todas")):
        
        temas_lista = dados.get("temas", [])
        
        # Preparar dados para tabela
        dados_tabela = []
        
        for tema_info in temas_lista:
            nome = tema_info["nome"]
            classificacao = priorizador.classificar_tema(nome, area)
            
            # Aplicar filtro
            if filtro_yield == "High-Yield 🔥" and classificacao["classificacao"] != "high_yield":
                continue
            elif filtro_yield == "Normal" and classificacao["classificacao"] != "normal":
                continue
            elif filtro_yield == "Low-Yield" and classificacao["classificacao"] != "low_yield":
                continue
            
            # Verificar status no estudo
            registro_tema = estudo.get("registro_temas", {}).get(nome, {})
            
            status_teoria = "✅" if registro_tema.get("data_teoria") else "⬜"
            status_r1 = "✅" if registro_tema.get("r1", {}).get("data") else "⬜"
            status_r2 = "✅" if registro_tema.get("r2", {}).get("data") else "⬜"
            status_r3 = "✅" if registro_tema.get("r3", {}).get("data") else "⬜"
            
            # Calcular prioridade
            prioridade = algoritmo.calcular_prioridade_tema(nome, area)
            
            dados_tabela.append({
                "Tema": nome,
                "Tipo": classificacao["icone"],
                "Prioridade": f"{int(prioridade * 100)}%",
                "Teoria": status_teoria,
                "R1": status_r1,
                "R2": status_r2,
                "R3": status_r3
            })
        
        if dados_tabela:
            df = pd.DataFrame(dados_tabela)
            st.dataframe(df, width="stretch", hide_index=True)
            
            # Resumo
            total = len(dados_tabela)
            teoria_feita = sum(1 for d in dados_tabela if d["Teoria"] == "✅")
            r1_feita = sum(1 for d in dados_tabela if d["R1"] == "✅")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Temas", total)
            col2.metric("Teoria", teoria_feita)
            col3.metric("1ª Revisão", r1_feita)
        else:
            st.info("Nenhum tema encontrado com os filtros selecionados.")

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Estatísticas Gerais")
    
    total_temas = sum(len(d.get("temas", [])) for d in temas.get("grandes_areas", {}).values())
    st.metric("Total de Temas", total_temas)
    
    # Contar por classificação
    high_yield = 0
    normal = 0
    low_yield = 0
    
    for area, dados in temas.get("grandes_areas", {}).items():
        for tema_info in dados.get("temas", []):
            classificacao = priorizador.classificar_tema(tema_info["nome"], area)
            if classificacao["classificacao"] == "high_yield":
                high_yield += 1
            elif classificacao["classificacao"] == "low_yield":
                low_yield += 1
            else:
                normal += 1
    
    st.metric("🔥 High-Yield", high_yield)
    st.metric("📖 Normal", normal)
    st.metric("📉 Low-Yield", low_yield)
    
    st.markdown("---")
    st.markdown("""
    ### 📖 Legenda
    
    - 🔥 **High-Yield**: Alta chance de cair
    - 📖 **Normal**: Chance regular
    - 📉 **Low-Yield**: Baixa chance
    
    ---
    
    - ✅ Concluído
    - ⬜ Pendente
    """)
