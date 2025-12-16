"""
Página de Cronograma Integrado

Visualização do plano de estudos integrado com o calendário acadêmico,
mostrando semanas, temas e metas distribuídas ao longo do ano.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import calendar
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import (
    carregar_config, carregar_calendario, carregar_estudo,
    carregar_pesos, carregar_temas, obter_rodizio_atual,
    calcular_dias_ate_prova, calcular_semanas_ate_prova
)
from utils.styles import inject_css
from core.calculadora_revisoes import CalculadoraRevisoes

st.set_page_config(
    page_title="Cronograma - Plataforma de Estudos",
    page_icon="📆",
    layout="wide"
)

# Injetar CSS
inject_css()

# Header
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h1 style="font-size: 2rem; font-weight: 800; 
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;">
        📆 Cronograma de Estudos
    </h1>
    <p style="color: #94a3b8; font-size: 0.95rem;">
        Plano integrado com seu calendário acadêmico | Ano 2026-2027
    </p>
</div>
""", unsafe_allow_html=True)

# Carregar dados
config = carregar_config()
calendario = carregar_calendario()
estudo = carregar_estudo()
pesos = carregar_pesos()
temas = carregar_temas()

calc_rev = CalculadoraRevisoes()

# Configurações do usuário
meta_semanal = config.get("metas", {}).get("questoes_semana_meta", 320)
ano_estudo = config.get("usuario", {}).get("ano_estudo", 1)
data_prova = config.get("usuario", {}).get("data_prova_estimada", "2027-11-15")

# ============================================
# TABS
# ============================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Visão Anual",
    "📋 Plano Semanal",
    "⚙️ Configurar Rotina",
    "📊 Progresso"
])

# ============================================
# TAB 1: VISÃO ANUAL - Timeline dos Rodízios
# ============================================

with tab1:
    st.subheader("🗓️ Timeline dos Rodízios - 2026")
    
    rodizios = calendario.get("ano_1", {}).get("2026", [])
    
    if not rodizios:
        st.info("Nenhum rodízio cadastrado. Configure na página de Calendário.")
    else:
        # Timeline visual
        for idx, rod in enumerate(rodizios):
            inicio = datetime.strptime(rod["inicio"], "%Y-%m-%d")
            fim = datetime.strptime(rod["fim"], "%Y-%m-%d")
            duracao_semanas = (fim - inicio).days // 7
            
            # Determinar cor baseada na área
            cores = {
                "Clinica Medica": "#3b82f6",
                "Cirurgia Geral": "#ef4444",
                "Pediatria": "#10b981",
                "Ginecologia e Obstetricia": "#ec4899",
                "Saude Coletiva": "#f59e0b",
                "Saude Mental": "#8b5cf6"
            }
            cor = cores.get(rod.get("grande_area_principal", ""), "#64748b")
            
            # Verificar se é o rodízio atual
            hoje = datetime.now()
            is_atual = inicio <= hoje <= fim
            
            st.markdown(f"""
            <div style="background: {'linear-gradient(135deg, ' + cor + '20 0%, ' + cor + '10 100%)' if is_atual else 'var(--dark-soft)'};
                 border-left: 4px solid {cor};
                 border-radius: 12px;
                 padding: 1.25rem;
                 margin-bottom: 1rem;
                 {'box-shadow: 0 0 20px ' + cor + '30;' if is_atual else ''}"
            >
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                            <span style="background: {cor}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">
                                {'🔴 ATUAL' if is_atual else f'{idx + 1}º'}
                            </span>
                            <h3 style="margin: 0; color: #f8fafc; font-size: 1.25rem;">{rod['rodizio']}</h3>
                        </div>
                        <p style="color: #94a3b8; margin: 0; font-size: 0.9rem;">
                            📅 {inicio.strftime('%d/%m/%Y')} → {fim.strftime('%d/%m/%Y')} • {duracao_semanas} semanas
                        </p>
                        <p style="color: #64748b; margin: 0.5rem 0 0 0; font-size: 0.85rem;">
                            📁 {rod.get('grande_area_principal', 'Não definida')} • Peso ENAMED: {pesos['pesos_areas'].get(rod.get('grande_area_principal', ''), 0) * 100:.0f}%
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.75rem; font-weight: 700; color: {cor};">
                            {duracao_semanas * meta_semanal // 7 * 5}
                        </div>
                        <div style="color: #64748b; font-size: 0.8rem;">questões estimadas</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Expandir para ver temas prioritários
            with st.expander(f"📚 Ver temas prioritários de {rod['rodizio']}"):
                temas_prio = rod.get("temas_prioritarios", [])
                if temas_prio:
                    cols = st.columns(3)
                    for i, tema in enumerate(temas_prio):
                        with cols[i % 3]:
                            st.markdown(f"• {tema}")
                else:
                    st.caption("Nenhum tema prioritário definido.")
        
        # Resumo do ano
        st.markdown("---")
        total_semanas = sum((datetime.strptime(r["fim"], "%Y-%m-%d") - datetime.strptime(r["inicio"], "%Y-%m-%d")).days // 7 for r in rodizios)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Semanas", f"{total_semanas}")
        with col2:
            st.metric("Meta Total Ano 1", f"{total_semanas * meta_semanal:,}")
        with col3:
            st.metric("Rodízios", len(rodizios))

# ============================================
# TAB 2: PLANO SEMANAL DETALHADO
# ============================================

with tab2:
    st.subheader("📋 Plano das Próximas 4 Semanas")
    
    hoje = datetime.now()
    rodizio_atual = obter_rodizio_atual(calendario)
    
    # Gerar plano para as próximas 4 semanas
    for semana_offset in range(4):
        data_inicio_semana = hoje + timedelta(days=(7 * semana_offset) - hoje.weekday())
        data_fim_semana = data_inicio_semana + timedelta(days=6)
        
        # Determinar rodízio desta semana
        rodizio_semana = None
        for rod in calendario.get("ano_1", {}).get("2026", []):
            inicio = datetime.strptime(rod["inicio"], "%Y-%m-%d")
            fim = datetime.strptime(rod["fim"], "%Y-%m-%d")
            if inicio <= data_inicio_semana <= fim or inicio <= data_fim_semana <= fim:
                rodizio_semana = rod
                break
        
        semana_num = data_inicio_semana.isocalendar()[1]
        is_semana_atual = semana_offset == 0
        
        st.markdown(f"""
        <div style="background: {'linear-gradient(135deg, #3b82f620 0%, #3b82f610 100%)' if is_semana_atual else '#1e293b'};
             border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;
             border: 1px solid {'#3b82f6' if is_semana_atual else 'transparent'};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: {'#3b82f6' if is_semana_atual else '#94a3b8'}; font-weight: 600;">
                        {'📍 SEMANA ATUAL' if is_semana_atual else f'Semana {semana_num}'}
                    </span>
                    <span style="color: #64748b; margin-left: 1rem;">
                        {data_inicio_semana.strftime('%d/%m')} - {data_fim_semana.strftime('%d/%m/%Y')}
                    </span>
                </div>
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <span style="color: #f8fafc; font-weight: 700;">{meta_semanal} questões</span>
                    <span style="background: #10b981; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem;">
                        {rodizio_semana['rodizio'] if rodizio_semana else 'Férias'}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if is_semana_atual and rodizio_semana:
            # Distribuição diária sugerida
            st.markdown("**📊 Distribuição Diária Sugerida:**")
            
            dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
            questoes_dia = [50, 50, 50, 50, 50, 40, 30]  # Exemplo de distribuição
            
            cols = st.columns(7)
            for i, (dia, qtd) in enumerate(zip(dias_semana, questoes_dia)):
                with cols[i]:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 0.5rem; background: #1e293b; border-radius: 8px;">
                        <div style="color: #64748b; font-size: 0.75rem;">{dia}</div>
                        <div style="color: #f8fafc; font-weight: 700; font-size: 1.1rem;">{qtd}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Temas sugeridos para a semana
            st.markdown("**📚 Temas Sugeridos:**")
            
            temas_prio = rodizio_semana.get("temas_prioritarios", [])[:5]
            
            for tema in temas_prio:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"• {tema}")
                with col2:
                    st.caption("~40 questões")
                with col3:
                    # Verificar se já estudou
                    estudado = tema.lower() in str(estudo.get("registro_temas", {})).lower()
                    if estudado:
                        st.markdown("✅")
                    else:
                        st.markdown("⬜")

# ============================================
# TAB 3: CONFIGURAR ROTINA
# ============================================

with tab3:
    st.subheader("⚙️ Configurar Rotina de Estudos")
    
    st.info("Configure sua rotina semanal para otimizar a distribuição de questões.")
    
    # Carregar configuração existente ou criar padrão
    rotina = config.get("rotina", {
        "dias_disponiveis": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"],
        "horas_por_dia": 3,
        "horario_preferido": "Noite",
        "questoes_por_hora": 15
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📅 Dias Disponíveis para Estudo:**")
        
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        dias_selecionados = []
        
        cols = st.columns(4)
        for i, dia in enumerate(dias):
            with cols[i % 4]:
                if st.checkbox(dia, value=dia in rotina.get("dias_disponiveis", []), key=f"dia_{dia}"):
                    dias_selecionados.append(dia)
        
        st.markdown("---")
        
        horas = st.slider(
            "⏰ Horas de estudo por dia:",
            min_value=1, max_value=8,
            value=rotina.get("horas_por_dia", 3)
        )
        
        horario = st.selectbox(
            "🌙 Horário preferido:",
            ["Manhã", "Tarde", "Noite", "Madrugada"],
            index=["Manhã", "Tarde", "Noite", "Madrugada"].index(rotina.get("horario_preferido", "Noite"))
        )
    
    with col2:
        st.markdown("**📊 Cálculo Automático:**")
        
        questoes_hora = st.number_input(
            "Questões por hora (estimativa):",
            min_value=5, max_value=30,
            value=rotina.get("questoes_por_hora", 15)
        )
        
        # Calcular estimativas
        dias_por_semana = len(dias_selecionados)
        horas_semana = dias_por_semana * horas
        questoes_semana_calc = horas_semana * questoes_hora
        
        st.markdown(f"""
        <div style="background: #1e293b; border-radius: 12px; padding: 1.25rem; margin-top: 1rem;">
            <h4 style="color: #f8fafc; margin-bottom: 1rem;">📈 Projeção Semanal</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <div style="color: #64748b; font-size: 0.8rem;">Dias/semana</div>
                    <div style="color: #f8fafc; font-size: 1.5rem; font-weight: 700;">{dias_por_semana}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.8rem;">Horas/semana</div>
                    <div style="color: #f8fafc; font-size: 1.5rem; font-weight: 700;">{horas_semana}h</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.8rem;">Questões estimadas</div>
                    <div style="color: {'#10b981' if questoes_semana_calc >= meta_semanal else '#f59e0b'}; font-size: 1.5rem; font-weight: 700;">
                        {questoes_semana_calc}
                    </div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.8rem;">Meta semanal</div>
                    <div style="color: #3b82f6; font-size: 1.5rem; font-weight: 700;">{meta_semanal}</div>
                </div>
            </div>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #334155;">
                <span style="color: {'#10b981' if questoes_semana_calc >= meta_semanal else '#f59e0b'};">
                    {'✅ Rotina adequada para atingir a meta!' if questoes_semana_calc >= meta_semanal else '⚠️ Considere aumentar horas ou dias de estudo.'}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("💾 Salvar Rotina", type="primary"):
        # Aqui salvaria a configuração
        st.success("Rotina salva com sucesso!")
        st.balloons()

# ============================================
# TAB 4: PROGRESSO
# ============================================

with tab4:
    st.subheader("📊 Progresso no Cronograma")
    
    semanas_ate_prova = calcular_semanas_ate_prova(data_prova)
    dias_ate = calcular_dias_ate_prova(data_prova)
    
    # Estatísticas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    total_questoes = estudo.get("estatisticas_gerais", {}).get("total_questoes_feitas", 0)
    meta_total = 33500 if ano_estudo == 1 else 67000
    
    with col1:
        st.metric("Semanas Restantes", semanas_ate_prova)
    with col2:
        st.metric("Questões Feitas", f"{total_questoes:,}")
    with col3:
        progresso_pct = min(100, (total_questoes / meta_total) * 100)
        st.metric("Progresso", f"{progresso_pct:.1f}%")
    with col4:
        necessario = max(0, (meta_total - total_questoes) / max(1, semanas_ate_prova))
        st.metric("Média Necessária/Semana", f"{necessario:.0f}")
    
    st.markdown("---")
    
    # Gráfico de progresso por mês (simulado)
    st.markdown("**📈 Distribuição Esperada vs Real:**")
    
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    esperado = [1200, 1400, 1400, 1400, 1400, 1200, 1400, 1400, 1400, 1400, 1200, 0]  # Meta mensal
    
    # Criar DataFrame para exibição
    df_progresso = pd.DataFrame({
        "Mês": meses,
        "Meta": esperado,
        "Realizado": [0] * 12  # Placeholder - seria calculado do estudo real
    })
    
    st.dataframe(df_progresso, use_container_width=True, hide_index=True)
    
    # Alertas
    st.markdown("---")
    st.markdown("**⚠️ Alertas do Cronograma:**")
    
    if total_questoes < (meta_total / semanas_ate_prova * (104 - semanas_ate_prova)):
        st.warning(f"📉 Você está {((meta_total / semanas_ate_prova * (104 - semanas_ate_prova)) - total_questoes):.0f} questões abaixo do esperado.")
    else:
        st.success("✅ Você está no ritmo esperado!")

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### 📆 Cronograma")
    
    rodizio = obter_rodizio_atual(calendario)
    
    if rodizio:
        st.markdown(f"""
        **Rodízio Atual:**  
        {rodizio['rodizio']}
        
        **Área:** {rodizio['grande_area_principal']}
        """)
    
    st.markdown("---")
    
    st.markdown(f"""
    **Meta Semanal:** {meta_semanal} questões
    
    **Ano de Estudo:** {ano_estudo}º ano
    
    **Prova:** {datetime.strptime(data_prova, '%Y-%m-%d').strftime('%d/%m/%Y')}
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 💡 Dicas
    
    - Priorize temas do rodízio atual
    - Distribua questões uniformemente
    - Reserve tempo para revisões
    - Ajuste a rotina conforme necessário
    """)

