"""
Página de Resolução de Questões

Interface interativa para resolver questões do banco,
com filtros, aleatorização e integração com o workflow de estudo.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import random
import json
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import (
    carregar_questoes, carregar_temas, carregar_estudo, salvar_estudo,
    carregar_config
)
from utils.styles import inject_css

st.set_page_config(
    page_title="Resolver Questões - Plataforma de Estudos",
    page_icon="✏️",
    layout="wide"
)

# Injetar CSS
inject_css()

# Inicializar session state
if "questoes_selecionadas" not in st.session_state:
    st.session_state.questoes_selecionadas = []
if "indice_atual" not in st.session_state:
    st.session_state.indice_atual = 0
if "respostas" not in st.session_state:
    st.session_state.respostas = {}
if "mostrar_gabarito" not in st.session_state:
    st.session_state.mostrar_gabarito = False
if "sessao_finalizada" not in st.session_state:
    st.session_state.sessao_finalizada = False
if "tema_sessao" not in st.session_state:
    st.session_state.tema_sessao = None

# Header
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h1 style="font-size: 2rem; font-weight: 800; 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;">
        ✏️ Resolver Questões
    </h1>
    <p style="color: #94a3b8; font-size: 0.95rem;">
        Pratique com questões do seu banco | Acompanhe seu desempenho
    </p>
</div>
""", unsafe_allow_html=True)

# Carregar dados
questoes_data = carregar_questoes()
temas_data = carregar_temas()
estudo = carregar_estudo()
config = carregar_config()

todas_questoes = questoes_data.get("questoes", [])

# Extrair opções únicas
temas_unicos = sorted(list(set(q.get("tema", "Não classificado") for q in todas_questoes)))
areas_unicas = sorted(list(set(q.get("grande_area", "Não classificada") for q in todas_questoes)))
bancas_unicas = sorted(list(set(q.get("banca", "Não informada") for q in todas_questoes)))

# ============================================
# MODO: CONFIGURAÇÃO DE SESSÃO
# ============================================

if not st.session_state.questoes_selecionadas or st.session_state.sessao_finalizada:
    
    st.subheader("🎯 Configurar Sessão de Questões")
    
    col1, col2 = st.columns(2)
    
    with col1:
        modo = st.selectbox(
            "📋 Modo de Estudo:",
            ["Por Tema", "Por Grande Área", "Aleatório", "Todas"]
        )
        
        if modo == "Por Tema":
            tema_selecionado = st.selectbox("Selecione o tema:", temas_unicos)
            questoes_filtradas = [q for q in todas_questoes if q.get("tema") == tema_selecionado]
            st.session_state.tema_sessao = tema_selecionado
            
        elif modo == "Por Grande Área":
            area_selecionada = st.selectbox("Selecione a área:", areas_unicas)
            questoes_filtradas = [q for q in todas_questoes if q.get("grande_area") == area_selecionada]
            st.session_state.tema_sessao = area_selecionada
            
        elif modo == "Aleatório":
            questoes_filtradas = todas_questoes.copy()
            st.session_state.tema_sessao = "Aleatório"
            
        else:
            questoes_filtradas = todas_questoes.copy()
            st.session_state.tema_sessao = "Geral"
        
        st.caption(f"📊 {len(questoes_filtradas)} questões disponíveis")
    
    with col2:
        # Garantir que max_value seja maior que min_value
        max_questoes = max(6, min(100, len(questoes_filtradas))) if questoes_filtradas else 6
        valor_padrao = min(20, max_questoes - 1) if max_questoes > 5 else 5
        
        quantidade = st.slider(
            "📏 Quantidade de questões:",
            min_value=1,
            max_value=max_questoes,
            value=min(valor_padrao, len(questoes_filtradas)) if questoes_filtradas else 5
        )
        
        aleatorizar = st.checkbox("🔀 Aleatorizar ordem", value=True)
        
        # Filtros adicionais
        with st.expander("⚙️ Filtros Avançados"):
            banca_filtro = st.multiselect(
                "Filtrar por banca:",
                bancas_unicas,
                default=[]
            )
            
            if banca_filtro:
                questoes_filtradas = [q for q in questoes_filtradas if q.get("banca") in banca_filtro]
                st.caption(f"📊 {len(questoes_filtradas)} após filtro de banca")
    
    st.markdown("---")
    
    if questoes_filtradas:
        if st.button("🚀 Iniciar Sessão", type="primary", width="stretch"):
            # Selecionar questões
            if aleatorizar:
                random.shuffle(questoes_filtradas)
            
            st.session_state.questoes_selecionadas = questoes_filtradas[:quantidade]
            st.session_state.indice_atual = 0
            st.session_state.respostas = {}
            st.session_state.mostrar_gabarito = False
            st.session_state.sessao_finalizada = False
            st.rerun()
    else:
        st.warning("⚠️ Nenhuma questão encontrada com os filtros selecionados.")

# ============================================
# MODO: RESOLVENDO QUESTÕES
# ============================================

else:
    questoes = st.session_state.questoes_selecionadas
    idx = st.session_state.indice_atual
    total = len(questoes)
    
    # Barra de progresso
    progresso = (idx + 1) / total
    respondidas = len(st.session_state.respostas)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.progress(progresso, text=f"Questão {idx + 1} de {total}")
    with col2:
        st.metric("Respondidas", f"{respondidas}/{total}")
    with col3:
        if respondidas > 0:
            acertos = sum(1 for r in st.session_state.respostas.values() if r.get("correta"))
            taxa = (acertos / respondidas) * 100
            st.metric("Taxa de Acerto", f"{taxa:.0f}%")
    
    st.markdown("---")
    
    # Questão atual
    questao = questoes[idx]
    
    # Card da questão
    st.markdown(f"""
    <div style="background: #1e293b; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;
         border-left: 4px solid #3b82f6;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <span style="background: #3b82f620; color: #3b82f6; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">
                {questao.get('tema', 'Tema não informado')}
            </span>
            <span style="color: #64748b; font-size: 0.85rem;">
                {questao.get('banca', '')}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enunciado
    st.markdown(f"**Enunciado:**")
    st.markdown(questao.get("enunciado", "Enunciado não disponível"))
    
    st.markdown("---")
    
    # Alternativas
    alternativas = questao.get("alternativas", [])
    gabarito = questao.get("gabarito", "")
    
    resposta_atual = st.session_state.respostas.get(idx, {}).get("resposta")
    
    st.markdown("**Alternativas:**")
    
    for alt in alternativas:
        # Extrair letra da alternativa (suporta formatos: "(A)", "A)", "A.")
        letra = ""
        if alt:
            # Procurar letra entre parênteses ou no início
            match = re.search(r'\(?([A-Ea-e])\)?', alt[:5])
            if match:
                letra = match.group(1).upper()
            else:
                letra = alt[0].upper() if alt[0].isalpha() else ""
        
        # Determinar estilo baseado no estado
        if st.session_state.mostrar_gabarito:
            if letra.upper() == gabarito.upper():
                estilo = "background: #10b98130; border: 2px solid #10b981;"
                icone = "✅"
            elif letra.upper() == resposta_atual:
                estilo = "background: #ef444430; border: 2px solid #ef4444;"
                icone = "❌"
            else:
                estilo = "background: #1e293b; border: 1px solid #334155;"
                icone = ""
        else:
            if letra.upper() == resposta_atual:
                estilo = "background: #3b82f630; border: 2px solid #3b82f6;"
                icone = "📌"
            else:
                estilo = "background: #1e293b; border: 1px solid #334155;"
                icone = ""
        
        if st.button(
            f"{icone} {alt}" if icone else alt,
            key=f"alt_{idx}_{letra}",
            width="stretch",
            disabled=st.session_state.mostrar_gabarito
        ):
            st.session_state.respostas[idx] = {
                "resposta": letra.upper(),
                "correta": letra.upper() == gabarito.upper()
            }
            st.rerun()
    
    st.markdown("---")
    
    # Botões de ação
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⬅️ Anterior", disabled=(idx == 0)):
            st.session_state.indice_atual -= 1
            st.session_state.mostrar_gabarito = False
            st.rerun()
    
    with col2:
        if not st.session_state.mostrar_gabarito:
            if st.button("👁️ Ver Gabarito", type="primary", disabled=(idx not in st.session_state.respostas)):
                st.session_state.mostrar_gabarito = True
                st.rerun()
        else:
            st.success(f"Gabarito: **{gabarito}**")
    
    with col3:
        if st.button("⭐ Marcar Importante"):
            # Salvar como importante
            if "questoes_marcadas_importantes" not in estudo:
                estudo["questoes_marcadas_importantes"] = []
            
            q_id = questao.get("id", str(idx))
            if q_id not in estudo["questoes_marcadas_importantes"]:
                estudo["questoes_marcadas_importantes"].append(q_id)
                salvar_estudo(estudo)
                st.toast("⭐ Questão marcada como importante!")
    
    with col4:
        if idx < total - 1:
            if st.button("Próxima ➡️"):
                st.session_state.indice_atual += 1
                st.session_state.mostrar_gabarito = False
                st.rerun()
        else:
            if st.button("📊 Finalizar", type="primary"):
                st.session_state.sessao_finalizada = True
                st.rerun()
    
    # Navegação rápida
    with st.expander("🔢 Navegação Rápida"):
        cols = st.columns(10)
        for i in range(total):
            with cols[i % 10]:
                status = ""
                if i in st.session_state.respostas:
                    if st.session_state.respostas[i].get("correta"):
                        status = "✅"
                    else:
                        status = "❌"
                else:
                    status = str(i + 1)
                
                if st.button(status, key=f"nav_{i}"):
                    st.session_state.indice_atual = i
                    st.session_state.mostrar_gabarito = False
                    st.rerun()

# ============================================
# MODO: RESULTADO FINAL
# ============================================

if st.session_state.sessao_finalizada and st.session_state.questoes_selecionadas:
    st.markdown("---")
    st.subheader("📊 Resultado da Sessão")
    
    total = len(st.session_state.questoes_selecionadas)
    respondidas = len(st.session_state.respostas)
    acertos = sum(1 for r in st.session_state.respostas.values() if r.get("correta"))
    erros = respondidas - acertos
    taxa = (acertos / respondidas * 100) if respondidas > 0 else 0
    
    # Cards de resultado
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total", total)
    with col2:
        st.metric("Acertos", acertos, delta=f"{taxa:.0f}%")
    with col3:
        st.metric("Erros", erros)
    with col4:
        cor_taxa = "#10b981" if taxa >= 80 else ("#f59e0b" if taxa >= 60 else "#ef4444")
        st.markdown(f"""
        <div style="background: {cor_taxa}20; border: 1px solid {cor_taxa}; border-radius: 12px; padding: 1rem; text-align: center;">
            <div style="font-size: 2rem; font-weight: 800; color: {cor_taxa};">{taxa:.0f}%</div>
            <div style="color: #94a3b8; font-size: 0.85rem;">Taxa de Acerto</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Salvar resultado no workflow
    if st.button("💾 Salvar no Histórico de Estudo", type="primary"):
        tema_sessao = st.session_state.tema_sessao or "Geral"
        
        # Atualizar registro de estudo
        if "registro_temas" not in estudo:
            estudo["registro_temas"] = {}
        
        if tema_sessao not in estudo["registro_temas"]:
            estudo["registro_temas"][tema_sessao] = {
                "data_teoria": datetime.now().strftime("%Y-%m-%d"),
                "grande_area": st.session_state.questoes_selecionadas[0].get("grande_area", "Geral") if st.session_state.questoes_selecionadas else "Geral"
            }
        
        # Determinar qual revisão registrar
        registro = estudo["registro_temas"][tema_sessao]
        
        if not registro.get("r1"):
            rev_key = "r1"
        elif not registro.get("r2"):
            rev_key = "r2"
        elif not registro.get("r3"):
            rev_key = "r3"
        else:
            rev_key = "extra"
        
        if rev_key != "extra":
            registro[rev_key] = {
                "data": datetime.now().strftime("%Y-%m-%d"),
                "questoes": respondidas,
                "acertos": acertos
            }
        
        # Atualizar estatísticas gerais
        if "estatisticas_gerais" not in estudo:
            estudo["estatisticas_gerais"] = {"total_questoes_feitas": 0, "total_acertos": 0}
        
        estudo["estatisticas_gerais"]["total_questoes_feitas"] = estudo["estatisticas_gerais"].get("total_questoes_feitas", 0) + respondidas
        estudo["estatisticas_gerais"]["total_acertos"] = estudo["estatisticas_gerais"].get("total_acertos", 0) + acertos
        estudo["ultima_atualizacao"] = datetime.now().isoformat()
        
        salvar_estudo(estudo)
        st.success(f"✅ Resultado salvo! {rev_key.upper()} registrada para '{tema_sessao}'")
        st.balloons()
    
    st.markdown("---")
    
    if st.button("🔄 Nova Sessão"):
        st.session_state.questoes_selecionadas = []
        st.session_state.indice_atual = 0
        st.session_state.respostas = {}
        st.session_state.mostrar_gabarito = False
        st.session_state.sessao_finalizada = False
        st.session_state.tema_sessao = None
        st.rerun()

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### ✏️ Resolver Questões")
    
    if st.session_state.questoes_selecionadas and not st.session_state.sessao_finalizada:
        st.markdown(f"""
        **Sessão Atual:**
        - Tema: {st.session_state.tema_sessao}
        - Total: {len(st.session_state.questoes_selecionadas)}
        - Respondidas: {len(st.session_state.respostas)}
        """)
        
        if st.button("❌ Cancelar Sessão"):
            st.session_state.questoes_selecionadas = []
            st.session_state.sessao_finalizada = False
            st.rerun()
    
    st.markdown("---")
    
    st.markdown(f"""
    **📊 Banco de Questões:**
    - Total: {len(todas_questoes)}
    - Temas: {len(temas_unicos)}
    - Áreas: {len(areas_unicas)}
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 💡 Dicas
    
    - Selecione alternativa antes de ver gabarito
    - Use ⭐ para marcar questões importantes
    - Salve o resultado para registrar revisão
    - Navegue rapidamente pelos números
    """)

