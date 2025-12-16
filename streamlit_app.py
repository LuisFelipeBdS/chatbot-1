"""
Dashboard Principal - Plataforma de Estudos para Residência Médica

Implementação baseada no método SuperPlanner/FluidMed com foco no ENAMED.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date
import pandas as pd

# Configurar path
sys.path.insert(0, str(Path(__file__).parent))

from utils.helpers import (
    carregar_config, carregar_estudo, carregar_calendario,
    carregar_pesos, obter_rodizio_atual, is_configurado,
    calcular_dias_ate_prova
)
from utils.styles import inject_css, render_main_header
from core.metricas import SistemaMetricas, obter_estatisticas
from core.priorizador_enamed import PriorizadorENAMED, obter_alertas
from core.algoritmo_sugestao import AlgoritmoSugestao, obter_plano_semanal
from core.calculadora_revisoes import CalculadoraRevisoes

# Configuração da página
st.set_page_config(
    page_title="Plataforma de Estudos - Residência Médica",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injetar CSS global
inject_css()

# Header Principal
st.markdown(
    render_main_header(
        "🏥 Plataforma de Estudos para Residência Médica",
        "Método baseado em Distributed Practice | Foco: ENAMED"
    ),
    unsafe_allow_html=True
)

# Verificar se está configurado
if not is_configurado():
    st.warning("""
    ### ⚙️ Configure o sistema para começar!
    
    Acesse a página de **Configurações** no menu lateral para definir:
    - 📋 Seus dados pessoais
    - 🎯 Meta de nota
    - 📊 Diagnóstico inicial
    - ⚡ Modo de estudo
    """)
    
    st.info("👈 Clique em **configuracoes** no menu lateral para começar.")
    st.stop()

# Carregar dados
config = carregar_config()
estudo = carregar_estudo()
calendario = carregar_calendario()
pesos = carregar_pesos()

# Instanciar classes
metricas_sys = SistemaMetricas()
priorizador = PriorizadorENAMED()
algoritmo = AlgoritmoSugestao()

# Obter estatísticas
stats = obter_estatisticas()
data_prova = config.get("usuario", {}).get("data_prova_estimada", "2027-11-15")
dias = calcular_dias_ate_prova(data_prova)
meta = config.get("metas", {}).get("nota_meta", 90)

# ============================================
# MÉTRICAS PRINCIPAIS (usando st.metric nativo)
# ============================================

nota = stats["nota_estimada"]["nota_estimada"]
delta_nota = nota - meta
media = stats["media_semanal"]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 Nota Estimada",
        value=f"{nota}%",
        delta=f"{delta_nota:+.1f}% da meta",
        delta_color="normal" if delta_nota >= 0 else "inverse"
    )
    st.caption(f"Meta: {meta}% | Confiança: {stats['nota_estimada']['confianca']}")

with col2:
    st.metric(
        label="📝 Questões/Semana",
        value=f"{int(media['media_necessaria'])}",
        delta="✓ No ritmo" if media["no_ritmo"] else "↑ Acelerar!",
        delta_color="normal" if media["no_ritmo"] else "inverse"
    )
    st.caption(f"Semanas restantes: {media['semanas_restantes']}")

with col3:
    st.metric(
        label="✅ Total Questões",
        value=f"{stats['questoes_total']:,}",
        delta=f"{stats['taxa_acerto_geral']:.1f}% acerto"
    )
    st.caption("Meta 2 anos: 33.500")

with col4:
    st.metric(
        label="📅 Dias até Prova",
        value=f"{dias}",
        delta=f"≈ {dias // 7} semanas"
    )
    st.caption(f"Data: {datetime.strptime(data_prova, '%Y-%m-%d').strftime('%d/%m/%Y')}")

# ============================================
# RODÍZIO ATUAL + ALERTAS
# ============================================

st.markdown("---")

col1, col2 = st.columns([3, 2])

with col1:
    rodizio = obter_rodizio_atual(calendario)
    
    if rodizio:
        inicio = datetime.strptime(rodizio["inicio"], "%Y-%m-%d")
        fim = datetime.strptime(rodizio["fim"], "%Y-%m-%d")
        hoje = datetime.now()
        
        progresso = max(0, min(1.0, (hoje - inicio).days / (fim - inicio).days))
        
        high_yield = pesos.get("temas_high_yield", {}).get(rodizio["grande_area_principal"], [])
        
        # Card do rodízio usando HTML simples
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); 
             border-radius: 16px; padding: 1.5rem; color: white; margin-bottom: 1rem;">
            <div style="background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 20px; 
                 display: inline-block; font-size: 0.75rem; font-weight: 600; margin-bottom: 0.75rem;">
                🏥 RODÍZIO ATUAL
            </div>
            <h2 style="margin: 0 0 0.5rem 0; font-size: 1.5rem;">{rodizio['rodizio']}</h2>
            <p style="opacity: 0.9; margin-bottom: 1rem;">
                {inicio.strftime('%d/%m/%Y')} - {fim.strftime('%d/%m/%Y')} • {(fim - inicio).days // 7} semanas
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(progresso, text=f"Progresso: {int(progresso * 100)}%")
        
        st.markdown(f"""
        **Grande Área:** {rodizio['grande_area_principal']} 
        (Peso ENAMED: {pesos['pesos_areas'].get(rodizio['grande_area_principal'], 0) * 100:.1f}%)
        """)
        
        st.markdown("**🔥 Temas High-Yield:**")
        tags = " ".join([f"`{tema}`" for tema in high_yield[:5]])
        st.markdown(tags)
    else:
        st.info("📅 Nenhum rodízio ativo no momento.")

with col2:
    st.subheader("⚠️ Alertas High-Yield")
    
    alertas = obter_alertas()
    
    if alertas:
        for alerta in alertas[:4]:
            tipo = "error" if "não revisado" in alerta.get('mensagem', '') else "warning"
            icon = "🔴" if tipo == "error" else "🟡"
            
            if tipo == "error":
                st.error(f"{icon} **{alerta['tema']}**\n\nÁrea: {alerta['area']}")
            else:
                st.warning(f"{icon} **{alerta['tema']}**\n\nÁrea: {alerta['area']}")
    else:
        st.success("✅ Todos os temas High-Yield prioritários estão em dia!")

# ============================================
# PRÓXIMAS REVISÕES
# ============================================

st.markdown("---")
st.subheader("📋 Próximas Revisões")

plano = obter_plano_semanal()

if plano["temas"]:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Tabela de revisões próximas
        dados_tabela = []
        for t in plano["temas"][:7]:
            status_emoji = {
                "atrasada": "🔴 Atrasado",
                "disponivel": "🟡 Hoje",
                "pendente": "🟢 Em breve"
            }.get(t.get("status", "pendente"), "⚪ -")
            
            tema_nome = t['tema']
            if t.get("is_high_yield"):
                tema_nome += " 🔥"
            
            # Formatar data sugerida
            data_str = ""
            if t.get("data_sugerida"):
                try:
                    data_obj = datetime.strptime(t["data_sugerida"], "%Y-%m-%d")
                    data_str = data_obj.strftime("%d/%m")
                except:
                    data_str = t["data_sugerida"]
            
            dados_tabela.append({
                "Status": status_emoji,
                "Tema": tema_nome,
                "Área": t["grande_area"],
                "Revisão": f"{t['revisao']}ª",
                "Data": data_str,
                "Questões": t["questoes"]
            })
        
        df = pd.DataFrame(dados_tabela)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with col2:
        st.metric("Total Sugerido", f"{plano['total_sugerido']}")
        st.metric("Meta Semanal", f"{plano['meta_questoes']}")
        
        diferenca = plano['total_sugerido'] - plano['meta_questoes']
        if diferenca > 100:
            st.warning("⚠️ Acumulado alto!")
        elif plano['total_sugerido'] == 0:
            st.success("✅ Sem revisões pendentes!")
        else:
            st.info("📅 Revisões agendadas")
else:
    st.success("✅ Nenhuma revisão pendente nos próximos 7 dias! Continue estudando novos temas.")

# ============================================
# COBERTURA E PERFORMANCE
# ============================================

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 Cobertura High-Yield")
    
    cobertura = priorizador.calcular_cobertura_high_yield()
    
    for area, dados in cobertura["por_area"].items():
        perc = dados["percentual"]
        cor = "🟢" if perc >= 80 else ("🟡" if perc >= 50 else "🔴")
        
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.progress(perc / 100, text=f"{area}")
        with col_b:
            st.caption(f"{cor} {dados['revisados']}/{dados['total']}")

with col2:
    st.subheader("📈 Progresso das Revisões")
    
    registro = estudo.get("registro_temas", {})
    total_temas = len(registro) if registro else 1
    
    r1_count = sum(1 for d in registro.values() if d.get("r1"))
    r2_count = sum(1 for d in registro.values() if d.get("r2"))
    r3_count = sum(1 for d in registro.values() if d.get("r3"))
    
    st.progress(r1_count / total_temas if total_temas > 0 else 0, text=f"1ª Revisão: {r1_count}/{total_temas}")
    st.progress(r2_count / total_temas if total_temas > 0 else 0, text=f"2ª Revisão: {r2_count}/{total_temas}")
    st.progress(r3_count / total_temas if total_temas > 0 else 0, text=f"3ª Revisão: {r3_count}/{total_temas}")
    
    # Mini score display
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Nota Estimada", f"{nota}%")
    with col_b:
        st.metric("Meta", f"{meta}%")

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    nome = config.get("usuario", {}).get("nome", "Estudante")
    ano = config.get("usuario", {}).get("ano_estudo", 1)
    
    st.markdown(f"""
    ### 👤 {nome}
    **{ano}º Ano** • ENAMED 2027
    """)
    
    st.markdown("---")
    
    # Countdown
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.15) 100%);
         border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 1rem; text-align: center;">
        <div style="font-size: 2.5rem; font-weight: 800; color: #f59e0b;">{dias}</div>
        <div style="font-size: 0.85rem; color: #94a3b8;">dias até a prova</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f"""
    **Banca:** {config.get('metas', {}).get('banca_principal', 'ENAMED')}
    
    **Meta:** {meta}%
    """)
    
    st.markdown("---")
    
    st.markdown("##### 🔗 Navegação")
    st.page_link("pages/1_configuracoes.py", label="⚙️ Configurações")
    st.page_link("pages/2_calendario.py", label="📅 Calendário")
    st.page_link("pages/3_temas.py", label="📚 Temas")
    st.page_link("pages/4_estudo.py", label="📝 Registrar Estudo")
    st.page_link("pages/5_questoes.py", label="❓ Banco de Questões")
    st.page_link("pages/6_metricas.py", label="📊 Métricas")
    st.page_link("pages/7_revisao_final.py", label="🎯 Revisão Final")
    st.page_link("pages/8_cronograma.py", label="📆 Cronograma")
    st.page_link("pages/9_resolver_questoes.py", label="✏️ Resolver Questões")
    
    st.markdown("---")
    st.caption(f"Última atualização: {estudo.get('ultima_atualizacao', 'Nunca')[:10] if estudo.get('ultima_atualizacao') else 'Nunca'}")
