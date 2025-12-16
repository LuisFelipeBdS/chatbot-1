"""
Página de Revisão Final - Pré-Prova

Concentra o estudo nos 7-14 dias antes da prova com:
- Questões marcadas como importantes
- Temas High-Yield
- Resumo de pontos críticos
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
from core.priorizador_enamed import PriorizadorENAMED
from core.metricas import SistemaMetricas

st.set_page_config(
    page_title="Revisão Final - Plataforma de Estudos",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Revisão Final Pré-Prova")
st.markdown("---")

# Carregar dados
config = carregar_config()
estudo = carregar_estudo()
questoes = carregar_questoes()
pesos = carregar_pesos()

priorizador = PriorizadorENAMED()
metricas = SistemaMetricas()

# Calcular dias até a prova
data_prova = config.get("usuario", {}).get("data_prova_estimada", "2027-11-15")
dias_ate_prova = calcular_dias_ate_prova(data_prova)

# Verificar se está na janela de revisão final
JANELA_REVISAO_FINAL = 14  # dias

if dias_ate_prova > JANELA_REVISAO_FINAL:
    st.info(f"""
    ### ⏰ Ainda não é hora da Revisão Final
    
    A revisão final é recomendada nos últimos **7-14 dias** antes da prova.
    
    **Dias até a prova:** {dias_ate_prova}
    
    **Liberação da Revisão Final:** em aproximadamente {dias_ate_prova - JANELA_REVISAO_FINAL} dias
    
    ---
    
    Continue seu ciclo normal de revisões e marque questões importantes para a revisão final!
    """)
    
    # Mostrar prévia
    st.markdown("### 📋 Prévia do que será revisado")
    
else:
    st.success(f"""
    ### 🎯 Modo Revisão Final Ativado!
    
    **{dias_ate_prova} dias até a prova**
    
    Foque nos pontos abaixo para maximizar sua pontuação.
    """)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 Temas High-Yield",
    "⭐ Questões Importantes", 
    "📊 Pontos Críticos",
    "📋 Checklist Final"
])

with tab1:
    st.header("🔥 Temas High-Yield para Revisar")
    
    st.markdown("""
    Estes são os temas com maior probabilidade de cobrança no ENAMED.
    Certifique-se de dominar todos antes da prova.
    """)
    
    # Obter high-yield pendentes
    pendentes = priorizador.obter_high_yield_pendentes()
    cobertura = priorizador.calcular_cobertura_high_yield()
    
    # Métricas de cobertura
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total = cobertura["total"]["high_yield_total"]
        revisados = cobertura["total"]["high_yield_revisados"]
        st.metric(
            "Cobertura Total",
            f"{cobertura['total']['percentual_cobertura']}%",
            f"{revisados}/{total} temas"
        )
    
    with col2:
        st.metric("Pendentes", len(pendentes))
    
    with col3:
        if len(pendentes) > 0:
            st.warning("⚠️ Atenção!")
        else:
            st.success("✅ Tudo revisado!")
    
    st.markdown("---")
    
    # Listar por área
    for area, temas in pesos.get("temas_high_yield", {}).items():
        cobertura_area = cobertura["por_area"].get(area, {})
        
        with st.expander(f"📁 {area} - {cobertura_area.get('percentual', 0)}% coberto"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Temas High-Yield:**")
                for tema in temas:
                    # Verificar se foi revisado
                    revisado = any(
                        tema.lower() in k.lower() 
                        for k, v in estudo.get("registro_temas", {}).items()
                        if v.get("r1")
                    )
                    
                    status = "✅" if revisado else "❌"
                    st.markdown(f"{status} {tema}")
            
            with col2:
                st.markdown(f"""
                **Peso ENAMED:** {pesos['pesos_areas'].get(area, 0) * 100:.1f}%
                
                **Status:**
                - Revisados: {cobertura_area.get('revisados', 0)}
                - Total: {cobertura_area.get('total', 0)}
                """)

with tab2:
    st.header("⭐ Questões Marcadas como Importantes")
    
    marcadas = estudo.get("questoes_marcadas_importantes", [])
    todas_questoes = questoes.get("questoes", [])
    
    if not marcadas:
        st.info("""
        📝 Nenhuma questão marcada como importante.
        
        Volte para o **Banco de Questões** e marque questões com:
        - Classificações importantes
        - Critérios diagnósticos
        - Escalas e scores
        - Achados patognomônicos
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
        
        # Criar modo de estudo sequencial
        st.markdown("---")
        st.markdown("### 📚 Modo Revisão Sequencial")
        
        if st.button("🎲 Iniciar Revisão Aleatória"):
            import random
            if questoes_importantes:
                q = random.choice(questoes_importantes)
                st.session_state["questao_atual"] = q
        
        if "questao_atual" in st.session_state:
            q = st.session_state["questao_atual"]
            
            st.markdown(f"**Tema:** {q.get('tema', 'Não informado')}")
            st.markdown(f"**Enunciado:**\n{q.get('enunciado', '')}")
            
            st.markdown("**Alternativas:**")
            for alt in q.get("alternativas", []):
                st.markdown(f"- {alt}")
            
            if st.button("👁️ Ver Gabarito"):
                st.success(f"**Gabarito:** {q.get('gabarito', '?')}")
        
        st.markdown("---")
        
        # Listar todas
        for area, qs in por_area.items():
            st.subheader(f"📁 {area} ({len(qs)} questões)")
            
            for i, q in enumerate(qs):
                with st.expander(f"📝 {q.get('tema', 'Sem tema')}"):
                    st.markdown(q.get("enunciado", "")[:500] + "..." if len(q.get("enunciado", "")) > 500 else q.get("enunciado", ""))
                    st.markdown(f"**Gabarito:** ||{q.get('gabarito', '?')}||")

with tab3:
    st.header("📊 Pontos Críticos - Menor Performance")
    
    st.markdown("""
    Temas onde sua performance está abaixo da meta.
    Priorize estes na reta final!
    """)
    
    registro = estudo.get("registro_temas", {})
    
    # Calcular temas com baixa performance
    temas_criticos = []
    
    for tema, dados in registro.items():
        questoes_total = 0
        acertos_total = 0
        
        for rev in ["r1", "r2", "r3"]:
            rev_dados = dados.get(rev, {})
            if rev_dados.get("questoes"):
                questoes_total += rev_dados["questoes"]
                acertos_total += rev_dados.get("acertos", 0)
        
        if questoes_total > 0:
            taxa = (acertos_total / questoes_total) * 100
            
            if taxa < 70:  # Abaixo da média aceitável
                temas_criticos.append({
                    "tema": tema,
                    "area": dados.get("grande_area", "?"),
                    "taxa": taxa,
                    "questoes": questoes_total
                })
    
    if temas_criticos:
        # Ordenar por taxa (menor primeiro)
        temas_criticos.sort(key=lambda x: x["taxa"])
        
        st.warning(f"⚠️ {len(temas_criticos)} temas precisam de atenção!")
        
        dados_tabela = []
        for t in temas_criticos[:10]:
            dados_tabela.append({
                "Tema": t["tema"][:40],
                "Área": t["area"][:15],
                "Taxa de Acerto": f"{t['taxa']:.1f}%",
                "Questões": t["questoes"],
                "Status": "🔴" if t["taxa"] < 50 else "🟡"
            })
        
        df = pd.DataFrame(dados_tabela)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Nenhum tema crítico! Sua performance está boa em todos os temas revisados.")

with tab4:
    st.header("📋 Checklist Final")
    
    st.markdown("Use esta lista para garantir que está pronto para a prova.")
    
    checklist = [
        ("Todos os temas High-Yield foram revisados pelo menos 1x", len(priorizador.obter_high_yield_pendentes()) == 0),
        ("Atingiu meta de questões (33.500)", estudo.get("estatisticas_gerais", {}).get("total_questoes_feitas", 0) >= 30000),
        ("Taxa de acerto acima de 80%", metricas.calcular_nota_estimada()["nota_estimada"] >= 80),
        ("Questões importantes revisadas", len(estudo.get("questoes_marcadas_importantes", [])) > 0),
        ("Simulados realizados", estudo.get("estatisticas_gerais", {}).get("simulados_realizados", 0) >= 3)
    ]
    
    concluidos = 0
    
    for item, status in checklist:
        if status:
            st.checkbox(item, value=True, disabled=True)
            concluidos += 1
        else:
            st.checkbox(item, value=False, disabled=True)
    
    st.markdown("---")
    
    progresso = concluidos / len(checklist)
    st.progress(progresso, text=f"Progresso: {concluidos}/{len(checklist)} itens")
    
    if progresso >= 0.8:
        st.success("🎉 Você está pronto para a prova! Confie no seu preparo!")
    elif progresso >= 0.5:
        st.warning("⚠️ Bom progresso, mas ainda há itens pendentes.")
    else:
        st.error("❌ Atenção: Muitos itens pendentes. Intensifique os estudos!")
    
    st.markdown("---")
    
    st.markdown("""
    ### 📝 Dicas Finais
    
    1. **Não estudar novos conteúdos** nos últimos 3 dias
    2. **Revisar apenas** questões marcadas e resumos
    3. **Dormir bem** nas noites anteriores
    4. **Alimentação leve** no dia da prova
    5. **Chegar cedo** ao local da prova
    6. **Confiar no processo** - você se preparou!
    """)

# Sidebar
with st.sidebar:
    st.header("⏱️ Contagem Regressiva")
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: #ff6b6b20; border-radius: 10px;">
        <h1 style="margin: 0; color: #ff6b6b">{dias_ate_prova}</h1>
        <p style="margin: 0;">dias para a prova</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f"""
    **Data da Prova:**
    {datetime.strptime(data_prova, '%Y-%m-%d').strftime('%d/%m/%Y')}
    
    **Revisão Final:**
    {(datetime.strptime(data_prova, '%Y-%m-%d') - timedelta(days=14)).strftime('%d/%m/%Y')}
    """)
    
    st.markdown("---")
    
    # Estatísticas rápidas
    stats = metricas.gerar_estatisticas_completas()
    
    st.metric("Nota Estimada", f"{stats['nota_estimada']['nota_estimada']}%")
    st.metric("Questões Feitas", stats['questoes_total'])
    
    st.markdown("---")
    
    st.markdown("""
    ### 🎯 Foco Final
    
    1. High-Yield pendentes
    2. Questões marcadas
    3. Temas críticos
    4. Descanso adequado
    """)

