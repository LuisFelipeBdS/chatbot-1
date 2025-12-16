"""
Página de Revisão Final - Pré-Prova
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import (
    carregar_estudo, carregar_config, carregar_questoes,
    carregar_pesos, calcular_dias_ate_prova
)
from utils.styles import inject_css

st.set_page_config(
    page_title="Revisão Final - Plataforma de Estudos",
    page_icon="🎯",
    layout="wide"
)

# Injetar CSS
inject_css()

# Header
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h1 style="font-size: 2rem; font-weight: 800; 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;">
        🎯 Revisão Final Pré-Prova
    </h1>
    <p style="color: #94a3b8; font-size: 0.95rem;">
        Concentre-se nos pontos críticos | Últimas semanas antes do ENAMED
    </p>
</div>
""", unsafe_allow_html=True)

# Carregar dados com tratamento de erro
try:
    config = carregar_config()
    estudo = carregar_estudo()
    questoes = carregar_questoes()
    pesos = carregar_pesos()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Importar com tratamento de erro
try:
    from core.priorizador_enamed import PriorizadorENAMED
    from core.metricas import SistemaMetricas
    priorizador = PriorizadorENAMED()
    metricas = SistemaMetricas()
except Exception as e:
    st.warning(f"Alguns módulos não puderam ser carregados: {e}")
    priorizador = None
    metricas = None

# Calcular dias até a prova
data_prova = config.get("usuario", {}).get("data_prova_estimada", "2027-11-15")
dias_ate_prova = calcular_dias_ate_prova(data_prova)

JANELA_REVISAO_FINAL = 14

# Card de status
if dias_ate_prova > JANELA_REVISAO_FINAL:
    st.markdown(f"""
    <div style="background: #1e293b; border-radius: 16px; padding: 2rem; text-align: center; margin-bottom: 1.5rem;
         border: 1px solid #334155;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">⏰</div>
        <h2 style="color: #f8fafc; margin-bottom: 0.5rem;">Ainda não é hora da Revisão Final</h2>
        <p style="color: #94a3b8; margin-bottom: 1rem;">
            A revisão final é recomendada nos últimos <strong>7-14 dias</strong> antes da prova.
        </p>
        <div style="display: inline-block; background: #f59e0b20; border: 1px solid #f59e0b; 
             border-radius: 12px; padding: 1rem 2rem;">
            <div style="font-size: 2.5rem; font-weight: 800; color: #f59e0b;">{dias_ate_prova}</div>
            <div style="color: #94a3b8; font-size: 0.85rem;">dias até a prova</div>
        </div>
        <p style="color: #64748b; font-size: 0.9rem; margin-top: 1rem;">
            Liberação: em aproximadamente {dias_ate_prova - JANELA_REVISAO_FINAL} dias
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("📚 Continue seu ciclo normal de revisões e marque questões importantes!")
else:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
         border-radius: 16px; padding: 2rem; text-align: center; margin-bottom: 1.5rem;">
        <h2 style="color: white; margin-bottom: 0.5rem;">🎯 Modo Revisão Final Ativado!</h2>
        <p style="color: rgba(255,255,255,0.9);">{dias_ate_prova} dias até a prova</p>
    </div>
    """, unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 High-Yield",
    "⭐ Questões Importantes", 
    "📊 Pontos Críticos",
    "📋 Checklist"
])

# ============================================
# TAB 1: HIGH-YIELD
# ============================================

with tab1:
    st.subheader("🔥 Cobertura de Temas High-Yield")
    
    if priorizador:
        try:
            cobertura = priorizador.calcular_cobertura_high_yield()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Cobertura Total",
                    f"{cobertura['total']['percentual_cobertura']}%",
                    f"{cobertura['total']['high_yield_revisados']}/{cobertura['total']['high_yield_total']} temas"
                )
            
            with col2:
                pendentes = priorizador.obter_high_yield_pendentes()
                st.metric("Pendentes", len(pendentes))
            
            with col3:
                if len(pendentes) > 0:
                    st.error("⚠️ Atenção necessária!")
                else:
                    st.success("✅ Tudo revisado!")
            
            st.markdown("---")
            
            # Lista de temas por área
            for area, temas_list in pesos.get("temas_high_yield", {}).items():
                cobertura_area = cobertura["por_area"].get(area, {})
                percentual = cobertura_area.get('percentual', 0)
                
                cor = "#10b981" if percentual >= 80 else ("#f59e0b" if percentual >= 50 else "#ef4444")
                
                with st.expander(f"📁 {area} - {percentual}% coberto"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Temas High-Yield:**")
                        for tema in temas_list:
                            revisado = any(
                                tema.lower() in k.lower() 
                                for k, v in estudo.get("registro_temas", {}).items()
                                if v.get("r1")
                            )
                            
                            status = "✅" if revisado else "❌"
                            st.markdown(f"{status} {tema}")
                    
                    with col2:
                        peso_area = pesos.get('pesos_areas', {}).get(area, 0) * 100
                        st.markdown(f"""
                        **Peso ENAMED:** {peso_area:.1f}%
                        
                        **Status:**
                        - Revisados: {cobertura_area.get('revisados', 0)}
                        - Total: {cobertura_area.get('total', 0)}
                        """)
                        
                        st.progress(percentual / 100)
        except Exception as e:
            st.error(f"Erro ao calcular cobertura: {e}")
    else:
        st.warning("Módulo de priorização não disponível.")

# ============================================
# TAB 2: QUESTÕES IMPORTANTES
# ============================================

with tab2:
    st.subheader("⭐ Questões Marcadas como Importantes")
    
    marcadas = estudo.get("questoes_marcadas_importantes", [])
    todas_questoes = questoes.get("questoes", [])
    
    if not marcadas:
        st.info("""
        📝 Nenhuma questão marcada como importante ainda.
        
        Para marcar questões importantes:
        1. Vá para a página **Resolver Questões**
        2. Clique em ⭐ **Marcar Importante** nas questões relevantes
        
        **Sugestão de questões para marcar:**
        - Classificações importantes (RIFLE, KDIGO, etc.)
        - Critérios diagnósticos
        - Escalas e scores
        - Fórmulas essenciais
        """)
    else:
        st.metric("Questões para Revisar", len(marcadas))
        
        questoes_importantes = [q for q in todas_questoes if q.get("id") in marcadas]
        
        # Agrupar por área
        por_area = {}
        for q in questoes_importantes:
            area = q.get("grande_area", "Outras")
            if area not in por_area:
                por_area[area] = []
            por_area[area].append(q)
        
        st.markdown("---")
        
        # Botão de questão aleatória
        if st.button("🎲 Questão Aleatória", key="btn_aleatorio_rev"):
            import random
            if questoes_importantes:
                q = random.choice(questoes_importantes)
                st.session_state["questao_revisao"] = q
        
        if "questao_revisao" in st.session_state:
            q = st.session_state["questao_revisao"]
            
            st.markdown(f"""
            <div style="background: #1e293b; border-radius: 12px; padding: 1.25rem; margin: 1rem 0;
                 border-left: 4px solid #f59e0b;">
                <div style="color: #f59e0b; font-size: 0.85rem; margin-bottom: 0.5rem;">
                    📁 {q.get('tema', 'Tema não informado')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**Enunciado:**\n\n{q.get('enunciado', '')}")
            
            st.markdown("**Alternativas:**")
            for alt in q.get("alternativas", []):
                st.markdown(f"- {alt}")
            
            if st.button("👁️ Ver Gabarito", key="ver_gab_rev"):
                st.success(f"**Gabarito:** {q.get('gabarito', '?')}")
        
        st.markdown("---")
        
        # Lista por área
        for area, qs in por_area.items():
            st.markdown(f"### 📁 {area} ({len(qs)} questões)")
            
            for i, q in enumerate(qs[:5]):
                with st.expander(f"📝 {q.get('tema', 'Sem tema')}", expanded=False):
                    enunciado = q.get("enunciado", "")
                    if len(enunciado) > 400:
                        enunciado = enunciado[:400] + "..."
                    st.markdown(enunciado)
                    st.markdown(f"**Gabarito:** {q.get('gabarito', '?')}")
            
            if len(qs) > 5:
                st.caption(f"+ {len(qs) - 5} questões adicionais")

# ============================================
# TAB 3: PONTOS CRÍTICOS
# ============================================

with tab3:
    st.subheader("📊 Temas com Baixo Desempenho")
    
    registro = estudo.get("registro_temas", {})
    
    temas_criticos = []
    
    for tema, dados in registro.items():
        questoes_total = 0
        acertos_total = 0
        
        for rev in ["r1", "r2", "r3"]:
            rev_dados = dados.get(rev, {})
            if rev_dados and rev_dados.get("questoes"):
                questoes_total += rev_dados["questoes"]
                acertos_total += rev_dados.get("acertos", 0)
        
        if questoes_total > 0:
            taxa = (acertos_total / questoes_total) * 100
            
            if taxa < 70:
                temas_criticos.append({
                    "tema": tema,
                    "area": dados.get("grande_area", "?"),
                    "taxa": taxa,
                    "questoes": questoes_total
                })
    
    if temas_criticos:
        temas_criticos.sort(key=lambda x: x["taxa"])
        
        st.warning(f"⚠️ {len(temas_criticos)} tema(s) precisam de atenção!")
        
        # Tabela
        dados_tabela = []
        for t in temas_criticos[:10]:
            dados_tabela.append({
                "Tema": t["tema"][:35] if len(t["tema"]) > 35 else t["tema"],
                "Área": t["area"][:15] if len(t["area"]) > 15 else t["area"],
                "Taxa": f"{t['taxa']:.1f}%",
                "Questões": t["questoes"],
                "Status": "🔴 Crítico" if t["taxa"] < 50 else "🟡 Atenção"
            })
        
        df = pd.DataFrame(dados_tabela)
        st.dataframe(df, width="stretch", hide_index=True)
        
        st.markdown("---")
        
        st.markdown("""
        **💡 Recomendações:**
        - Refaça questões desses temas
        - Revise a teoria dos pontos-chave
        - Foque nos High-Yield primeiro
        """)
    else:
        if registro:
            st.success("✅ Excelente! Nenhum tema crítico encontrado. Boa performance em todos!")
        else:
            st.info("📝 Nenhum estudo registrado ainda. Comece a resolver questões para ver seu desempenho.")

# ============================================
# TAB 4: CHECKLIST
# ============================================

with tab4:
    st.subheader("📋 Checklist Pré-Prova")
    
    # Calcular métricas
    total_questoes = estudo.get("estatisticas_gerais", {}).get("total_questoes_feitas", 0)
    total_acertos = estudo.get("estatisticas_gerais", {}).get("total_acertos", 0)
    taxa_acerto = (total_acertos / total_questoes * 100) if total_questoes > 0 else 0
    
    if metricas:
        try:
            nota_atual = metricas.calcular_nota_estimada()["nota_estimada"]
        except:
            nota_atual = taxa_acerto
    else:
        nota_atual = taxa_acerto
    
    pendentes_hy = 0
    if priorizador:
        try:
            pendentes_hy = len(priorizador.obter_high_yield_pendentes())
        except:
            pass
    
    # Checklist items
    checklist = [
        ("Todos os temas High-Yield revisados", pendentes_hy == 0),
        ("Meta de questões (>30.000)", total_questoes >= 30000),
        ("Taxa de acerto >80%", nota_atual >= 80),
        ("Questões importantes marcadas", len(estudo.get("questoes_marcadas_importantes", [])) > 0),
        ("Simulados realizados (3+)", estudo.get("estatisticas_gerais", {}).get("simulados_realizados", 0) >= 3)
    ]
    
    concluidos = 0
    
    for item, status in checklist:
        col1, col2 = st.columns([10, 1])
        with col1:
            if status:
                st.markdown(f"✅ ~~{item}~~")
                concluidos += 1
            else:
                st.markdown(f"⬜ {item}")
        with col2:
            st.markdown("✓" if status else "")
    
    st.markdown("---")
    
    # Barra de progresso
    progresso = concluidos / len(checklist) if checklist else 0
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(progresso)
    with col2:
        st.markdown(f"**{concluidos}/{len(checklist)}** itens")
    
    # Feedback
    if progresso >= 0.8:
        st.success("🎉 Você está pronto! Confie no seu preparo!")
    elif progresso >= 0.5:
        st.warning("⚠️ Bom progresso, mas ainda há pendências importantes.")
    else:
        st.error("❌ Muitos itens pendentes. Intensifique os estudos!")
    
    st.markdown("---")
    
    st.markdown("""
    ### 📝 Dicas para os Últimos Dias
    
    1. **Não estudar conteúdos novos** nos últimos 3 dias
    2. **Revisar apenas** questões marcadas e resumos pessoais
    3. **Dormir bem** nas noites anteriores (mínimo 7h)
    4. **Alimentação leve** no dia da prova
    5. **Chegar cedo** ao local de prova
    6. **Confiar no processo** - você se preparou!
    
    ---
    
    ### 🧘 Controle da Ansiedade
    
    - Respiração profunda antes de começar
    - Leia todas as questões antes de responder
    - Comece pelas questões que domina
    - Não fique preso em questões difíceis
    - Gerencie bem o tempo
    """)

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### ⏱️ Contagem Regressiva")
    
    # Countdown simples
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.15) 100%);
         border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 1.25rem; text-align: center;">
        <div style="font-size: 2.5rem; font-weight: 800; color: #f59e0b;">{dias_ate_prova}</div>
        <div style="font-size: 0.85rem; color: #94a3b8;">dias até a prova</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    try:
        data_prova_fmt = datetime.strptime(data_prova, '%Y-%m-%d').strftime('%d/%m/%Y')
        data_revisao = (datetime.strptime(data_prova, '%Y-%m-%d') - timedelta(days=14)).strftime('%d/%m/%Y')
    except:
        data_prova_fmt = data_prova
        data_revisao = "N/A"
    
    st.markdown(f"""
    **📅 Data da Prova:**  
    {data_prova_fmt}
    
    **🎯 Início Revisão Final:**  
    {data_revisao}
    """)
    
    st.markdown("---")
    
    # Stats rápidas
    st.metric("Questões Feitas", f"{total_questoes:,}")
    st.metric("Taxa de Acerto", f"{taxa_acerto:.1f}%")
    
    st.markdown("---")
    
    st.markdown("""
    ### 🎯 Foco Final
    
    1. High-Yield pendentes
    2. Questões marcadas ⭐
    3. Temas críticos 🔴
    4. Descanso adequado 😴
    """)
