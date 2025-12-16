"""
Página de Configurações Iniciais
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import (
    carregar_config, salvar_config, carregar_pesos,
    carregar_temas, calcular_dias_ate_prova
)
from utils.constants import (
    GRANDES_AREAS, MODOS_ESTUDO, MARGENS_ESTUDO,
    META_QUESTOES_SEMANA
)
from utils.styles import inject_css, render_main_header

st.set_page_config(
    page_title="Configurações - Plataforma de Estudos",
    page_icon="⚙️",
    layout="wide"
)

# Injetar CSS
inject_css()

# Header
st.markdown(
    render_main_header("⚙️ Configurações", "Configure sua jornada de estudos"),
    unsafe_allow_html=True
)

# Carregar configuração atual
config = carregar_config()

# Tabs para organizar as configurações
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Dados Pessoais", 
    "🎯 Metas", 
    "📊 Diagnóstico Inicial",
    "⚡ Modo de Estudo"
])

with tab1:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon primary">👤</div>
            <div class="section-title">Dados Pessoais</div>
        </div>
        <div class="section-body">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input(
            "Seu Nome",
            value=config.get("usuario", {}).get("nome", ""),
            placeholder="Digite seu nome"
        )
        
        ano_estudo = st.selectbox(
            "Ano de Estudo Atual",
            options=[1, 2],
            index=config.get("usuario", {}).get("ano_estudo", 1) - 1,
            help="Ano 1: 5º ano (9º e 10º períodos) | Ano 2: 6º ano (11º e 12º períodos)"
        )
    
    with col2:
        data_inicio = st.date_input(
            "Data de Início do Estudo",
            value=datetime.strptime(
                config.get("usuario", {}).get("data_inicio_estudo", "2026-01-15"),
                "%Y-%m-%d"
            ).date(),
            min_value=date(2025, 1, 1),
            max_value=date(2028, 12, 31)
        )
        
        data_prova = st.date_input(
            "Data Estimada da Prova (ENAMED)",
            value=datetime.strptime(
                config.get("usuario", {}).get("data_prova_estimada", "2027-11-15"),
                "%Y-%m-%d"
            ).date(),
            min_value=date(2026, 1, 1),
            max_value=date(2029, 12, 31),
            help="O ENAMED geralmente ocorre em novembro/dezembro"
        )
    
    # Mostrar dias até a prova
    if data_prova:
        dias_restantes = (data_prova - date.today()).days
        if dias_restantes > 0:
            semanas = dias_restantes // 7
            st.info(f"📅 Faltam **{dias_restantes} dias** ({semanas} semanas) até a prova estimada.")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon success">🎯</div>
            <div class="section-title">Metas de Estudo</div>
        </div>
        <div class="section-body">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        banca = st.selectbox(
            "Banca Principal",
            options=["ENAMED", "ENARE-FGV", "SUS-SP", "AMRIGS", "PSU-MG", "Outro"],
            index=0 if config.get("metas", {}).get("banca_principal", "ENAMED") == "ENAMED" else 0
        )
        
        nota_meta = st.slider(
            "Meta de Nota (%)",
            min_value=60,
            max_value=100,
            value=config.get("metas", {}).get("nota_meta", 90),
            step=1,
            help="Baseado na análise, notas acima de 85% garantem boas colocações"
        )
    
    with col2:
        questoes_semana = st.number_input(
            "Meta de Questões por Semana",
            min_value=50,
            max_value=1000,
            value=config.get("metas", {}).get("questoes_semana_meta", META_QUESTOES_SEMANA),
            step=10,
            help="Recomendado: 320 questões/semana para meta de 90% em 2 anos"
        )
        
        st.markdown("""
        **📈 Referências de Meta:**
        - **Baixa concorrência**: 150-200 questões/semana
        - **Média concorrência**: 200-500 questões/semana  
        - **Alta concorrência**: 500+ questões/semana
        """)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon warning">📊</div>
            <div class="section-title">Diagnóstico Inicial por Grande Área</div>
        </div>
        <div class="section-body">
    """, unsafe_allow_html=True)
    
    st.markdown("""
    Informe sua porcentagem de acerto atual em cada grande área.
    Isso ajudará o algoritmo a personalizar suas recomendações desde o início.
    
    💡 *Faça algumas provas antigas na íntegra para ter esses números.*
    """)
    
    diagnostico = config.get("diagnostico_inicial", {})
    
    col1, col2 = st.columns(2)
    
    areas_inputs = {}
    
    with col1:
        areas_inputs["clinica_medica"] = st.slider(
            "Clínica Médica (%)",
            0, 100,
            value=diagnostico.get("clinica_medica") or 50,
            key="diag_clinica"
        )
        
        areas_inputs["saude_coletiva"] = st.slider(
            "Saúde Coletiva / MFC (%)",
            0, 100,
            value=diagnostico.get("saude_coletiva") or 50,
            key="diag_coletiva"
        )
        
        areas_inputs["pediatria"] = st.slider(
            "Pediatria (%)",
            0, 100,
            value=diagnostico.get("pediatria") or 50,
            key="diag_peds"
        )
    
    with col2:
        areas_inputs["ginecologia_obstetricia"] = st.slider(
            "Ginecologia e Obstetrícia (%)",
            0, 100,
            value=diagnostico.get("ginecologia_obstetricia") or 50,
            key="diag_go"
        )
        
        areas_inputs["cirurgia_geral"] = st.slider(
            "Cirurgia Geral (%)",
            0, 100,
            value=diagnostico.get("cirurgia_geral") or 50,
            key="diag_cir"
        )
        
        areas_inputs["saude_mental"] = st.slider(
            "Saúde Mental (%)",
            0, 100,
            value=diagnostico.get("saude_mental") or 50,
            key="diag_mental"
        )
    
    # Calcular média ponderada
    pesos = carregar_pesos()
    pesos_areas = pesos.get("pesos_areas", {})
    
    media_ponderada = (
        areas_inputs["clinica_medica"] * pesos_areas.get("Clinica Medica", 0.325) +
        areas_inputs["saude_coletiva"] * pesos_areas.get("Saude Coletiva", 0.225) +
        areas_inputs["pediatria"] * pesos_areas.get("Pediatria", 0.175) +
        areas_inputs["ginecologia_obstetricia"] * pesos_areas.get("Ginecologia e Obstetricia", 0.175) +
        areas_inputs["cirurgia_geral"] * pesos_areas.get("Cirurgia Geral", 0.125) +
        areas_inputs["saude_mental"] * pesos_areas.get("Saude Mental", 0.075)
    )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col2:
        st.metric(
            "Nota Estimada Atual (Ponderada ENAMED)",
            f"{media_ponderada:.1f}%",
            delta=f"{media_ponderada - nota_meta:.1f}% da meta" if 'nota_meta' in dir() else None
        )
    
    st.markdown("</div></div>", unsafe_allow_html=True)

with tab4:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon danger">⚡</div>
            <div class="section-title">Modo de Estudo</div>
        </div>
        <div class="section-body">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        modo = st.radio(
            "Foco do Estudo",
            options=list(MODOS_ESTUDO.keys()),
            format_func=lambda x: MODOS_ESTUDO[x],
            index=0 if config.get("modo_estudo", {}).get("tipo", "focado_resultado") == "focado_resultado" else 1,
            help="""
            **Focado no Resultado**: O sistema calcula quantas questões você precisa fazer para atingir sua meta.
            
            **Focado na Quantidade**: Você define quantas questões quer fazer e o sistema otimiza a distribuição.
            """
        )
        
        margem = st.radio(
            "Margem de Segurança",
            options=list(MARGENS_ESTUDO.keys()),
            format_func=lambda x: MARGENS_ESTUDO[x],
            index=1,  # equilibrado como padrão
            help="""
            **Reduzido**: Estudo mínimo para atingir a meta (arriscado)
            
            **Equilibrado**: Margem razoável de segurança (recomendado)
            
            **Rigoroso**: Máxima preparação (para alta competitividade)
            """
        )
    
    with col2:
        ano_valer = st.checkbox(
            "Este é meu ano para valer?",
            value=config.get("modo_estudo", {}).get("ano_para_valer", False),
            help="Marque se este é o ano em que você PRECISA passar. O sistema ajustará a intensidade."
        )
        
        st.markdown("---")
        
        if modo == "focado_resultado":
            st.success("""
            **Modo: Focado no Resultado** ✓
            
            O sistema calculará automaticamente:
            - Quantas questões fazer por semana
            - Priorização dinâmica de temas
            - Ajustes baseados na sua performance
            """)
        else:
            st.info("""
            **Modo: Focado na Quantidade**
            
            Você define a quantidade e o sistema:
            - Distribui otimamente entre os temas
            - Prioriza pelo peso ENAMED
            - Ajusta conforme rodízio atual
            """)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# Botão de salvar
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("💾 Salvar Configurações", type="primary", width="stretch"):
        # Montar configuração atualizada
        nova_config = {
            "usuario": {
                "nome": nome,
                "ano_estudo": ano_estudo,
                "data_inicio_estudo": data_inicio.strftime("%Y-%m-%d"),
                "data_prova_estimada": data_prova.strftime("%Y-%m-%d")
            },
            "metas": {
                "banca_principal": banca,
                "nota_meta": nota_meta,
                "questoes_semana_meta": questoes_semana
            },
            "modo_estudo": {
                "tipo": modo,
                "margem": margem,
                "ano_para_valer": ano_valer
            },
            "diagnostico_inicial": areas_inputs,
            "configurado": True
        }
        
        salvar_config(nova_config)
        st.success("✅ Configurações salvas com sucesso!")
        st.balloons()

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ Informações")
    
    if config.get("configurado"):
        st.success("Sistema configurado ✓")
        st.markdown(f"""
        **Usuário:** {config.get('usuario', {}).get('nome', 'Não informado')}
        
        **Ano:** {config.get('usuario', {}).get('ano_estudo', 1)}º ano
        
        **Meta:** {config.get('metas', {}).get('nota_meta', 90)}%
        """)
    else:
        st.warning("Configure o sistema para começar!")
    
    st.markdown("---")
    st.markdown("""
    ### 📚 Pesos ENAMED
    
    - **Clínica Médica**: 32.5%
    - **Saúde Coletiva**: 22.5%
    - **Pediatria**: 17.5%
    - **GO**: 17.5%
    - **Cirurgia**: 12.5%
    - **Saúde Mental**: 7.5%
    """)
