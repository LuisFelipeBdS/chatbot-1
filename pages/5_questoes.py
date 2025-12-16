"""
Página de Banco de Questões
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import carregar_questoes, salvar_questoes, carregar_estudo, salvar_estudo
from utils.styles import inject_css, render_main_header

st.set_page_config(
    page_title="Banco de Questões - Plataforma de Estudos",
    page_icon="❓",
    layout="wide"
)

# Injetar CSS
inject_css()

# Header
st.markdown(
    render_main_header("❓ Banco de Questões", "Importe e gerencie suas questões"),
    unsafe_allow_html=True
)

# Carregar dados
questoes = carregar_questoes()
estudo = carregar_estudo()

# Tabs
tab1, tab2, tab3 = st.tabs(["📥 Importar", "🔍 Visualizar", "⭐ Importantes"])

with tab1:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon primary">📥</div>
            <div class="section-title">Importar Banco de Questões (JSON)</div>
        </div>
        <div class="section-body">
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### Formato Esperado do JSON
    
    ```json
    {
      "questoes": [
        {
          "id": "001",
          "enunciado": "Paciente de 45 anos...",
          "alternativas": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."],
          "gabarito": "B",
          "tema": "Tuberculose",
          "grande_area": "Clinica Medica",
          "banca": "ENARE 2023"
        }
      ]
    }
    ```
    """)
    
    uploaded_file = st.file_uploader(
        "Selecione o arquivo JSON",
        type=["json"],
        help="Arquivo JSON com o banco de questões"
    )
    
    if uploaded_file is not None:
        try:
            conteudo = json.load(uploaded_file)
            
            if "questoes" not in conteudo:
                st.error("❌ Formato inválido: campo 'questoes' não encontrado")
            else:
                questoes_importadas = conteudo["questoes"]
                
                st.success(f"✅ {len(questoes_importadas)} questões encontradas!")
                
                st.markdown("**Preview:**")
                for i, q in enumerate(questoes_importadas[:3]):
                    with st.expander(f"Questão {i+1}: {q.get('tema', 'Sem tema')}"):
                        st.markdown(f"**Enunciado:** {q.get('enunciado', '')[:200]}...")
                        st.markdown(f"**Gabarito:** {q.get('gabarito', '?')}")
                        st.markdown(f"**Área:** {q.get('grande_area', 'Não informada')}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    modo_import = st.radio(
                        "Modo de importação",
                        options=["Substituir tudo", "Adicionar às existentes"]
                    )
                
                if st.button("📥 Confirmar Importação", type="primary"):
                    if modo_import == "Substituir tudo":
                        questoes["questoes"] = questoes_importadas
                    else:
                        questoes["questoes"].extend(questoes_importadas)
                    
                    questoes["total"] = len(questoes["questoes"])
                    salvar_questoes(questoes)
                    
                    st.success(f"✅ {len(questoes_importadas)} questões importadas!")
                    st.balloons()
                    
        except json.JSONDecodeError:
            st.error("❌ Erro ao ler JSON. Verifique o formato.")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon success">🔍</div>
            <div class="section-title">Visualizar Questões</div>
        </div>
        <div class="section-body">
    """, unsafe_allow_html=True)
    
    todas_questoes = questoes.get("questoes", [])
    
    if not todas_questoes:
        st.info("📝 Nenhuma questão no banco. Importe questões na aba anterior.")
    else:
        st.markdown(f"**Total: {len(todas_questoes)} questões**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            areas = list(set(q.get("grande_area", "Não classificada") for q in todas_questoes))
            area_filtro = st.selectbox("Área", ["Todas"] + sorted(areas))
        
        with col2:
            temas_unicos = list(set(q.get("tema", "Não classificado") for q in todas_questoes))
            tema_filtro = st.selectbox("Tema", ["Todos"] + sorted(temas_unicos))
        
        with col3:
            bancas = list(set(q.get("banca", "Não informada") for q in todas_questoes))
            banca_filtro = st.selectbox("Banca", ["Todas"] + sorted(bancas))
        
        questoes_filtradas = todas_questoes
        
        if area_filtro != "Todas":
            questoes_filtradas = [q for q in questoes_filtradas if q.get("grande_area") == area_filtro]
        
        if tema_filtro != "Todos":
            questoes_filtradas = [q for q in questoes_filtradas if q.get("tema") == tema_filtro]
        
        if banca_filtro != "Todas":
            questoes_filtradas = [q for q in questoes_filtradas if q.get("banca") == banca_filtro]
        
        st.markdown(f"**Mostrando: {len(questoes_filtradas)} questões**")
        
        questoes_por_pagina = 10
        total_paginas = max(1, len(questoes_filtradas) // questoes_por_pagina + 1)
        
        pagina = st.number_input("Página", min_value=1, max_value=total_paginas, value=1)
        
        inicio = (pagina - 1) * questoes_por_pagina
        fim = inicio + questoes_por_pagina
        
        for i, q in enumerate(questoes_filtradas[inicio:fim], start=inicio+1):
            questao_id = q.get("id", str(i))
            marcada = questao_id in estudo.get("questoes_marcadas_importantes", [])
            
            col1, col2 = st.columns([10, 1])
            
            with col1:
                with st.expander(f"📝 Questão {i} - {q.get('tema', 'Sem tema')} {'⭐' if marcada else ''}"):
                    st.markdown(f"**Enunciado:**\n{q.get('enunciado', 'Não disponível')}")
                    
                    st.markdown("**Alternativas:**")
                    for alt in q.get("alternativas", []):
                        st.markdown(f"- {alt}")
                    
                    if st.button(f"Ver Gabarito", key=f"gab_{questao_id}"):
                        st.success(f"**Gabarito:** {q.get('gabarito', '?')}")
                    
                    st.caption(f"Área: {q.get('grande_area', '?')} | Tema: {q.get('tema', '?')} | Banca: {q.get('banca', '?')}")
            
            with col2:
                if st.button("⭐" if not marcada else "★", key=f"mark_{questao_id}"):
                    marcadas = estudo.get("questoes_marcadas_importantes", [])
                    
                    if marcada:
                        marcadas.remove(questao_id)
                    else:
                        marcadas.append(questao_id)
                    
                    estudo["questoes_marcadas_importantes"] = marcadas
                    salvar_estudo(estudo)
                    st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon warning">⭐</div>
            <div class="section-title">Questões Marcadas como Importantes</div>
        </div>
        <div class="section-body">
    """, unsafe_allow_html=True)
    
    st.markdown("""
    Questões marcadas serão usadas na **Revisão Final** antes da prova.
    
    Use para marcar:
    - 📌 Conceitos-chave
    - 📊 Classificações e escalas
    - 🔑 Achados patognomônicos
    """)
    
    marcadas = estudo.get("questoes_marcadas_importantes", [])
    
    if not marcadas:
        st.info("⭐ Nenhuma questão marcada ainda.")
    else:
        st.metric("Total de Questões Importantes", len(marcadas))
        
        todas_questoes = questoes.get("questoes", [])
        questoes_importantes = [q for q in todas_questoes if q.get("id") in marcadas]
        
        por_area = {}
        for q in questoes_importantes:
            area = q.get("grande_area", "Outras")
            if area not in por_area:
                por_area[area] = []
            por_area[area].append(q)
        
        for area, qs in por_area.items():
            st.subheader(f"📁 {area} ({len(qs)} questões)")
            
            for q in qs[:5]:
                with st.expander(f"📝 {q.get('tema', 'Sem tema')}"):
                    st.markdown(q.get("enunciado", "")[:300] + "...")
                    st.markdown(f"**Gabarito:** {q.get('gabarito', '?')}")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Estatísticas")
    
    total = len(questoes.get("questoes", []))
    st.metric("Total de Questões", total)
    
    marcadas_count = len(estudo.get("questoes_marcadas_importantes", []))
    st.metric("Questões Importantes", marcadas_count)
    
    st.markdown("---")
    
    if total > 0:
        st.markdown("**Por Área:**")
        todas = questoes.get("questoes", [])
        
        contagem = {}
        for q in todas:
            area = q.get("grande_area", "Outras")
            contagem[area] = contagem.get(area, 0) + 1
        
        for area, qtd in sorted(contagem.items(), key=lambda x: x[1], reverse=True):
            st.caption(f"• {area}: {qtd}")
    
    st.markdown("---")
    st.markdown("""
    ### 💡 Dica
    
    Marque questões importantes ao longo do ano para a **Revisão Final**!
    """)
