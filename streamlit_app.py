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

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .alert-high-yield {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 5px 5px 0;
    }
    .progress-good { color: #28a745; }
    .progress-warning { color: #ffc107; }
    .progress-danger { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<p class="main-header">🏥 Plataforma de Estudos para Residência Médica</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Método baseado em Distributed Practice | Foco: ENAMED</p>', unsafe_allow_html=True)

# Verificar se está configurado
if not is_configurado():
    st.warning("""
    ### ⚠️ Configure o sistema para começar!
    
    Acesse a página de **Configurações** no menu lateral para definir:
    - Seus dados pessoais
    - Meta de nota
    - Diagnóstico inicial
    - Modo de estudo
    """)
    
    st.info("👈 Clique em **Configurações** no menu lateral para começar.")
    st.stop()

# Carregar dados
config = carregar_config()
estudo = carregar_estudo()
calendario = carregar_calendario()
pesos = carregar_pesos()

# Instanciar classes
metricas = SistemaMetricas()
priorizador = PriorizadorENAMED()
algoritmo = AlgoritmoSugestao()

# Linha superior - Métricas principais
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

stats = obter_estatisticas()

with col1:
    nota = stats["nota_estimada"]["nota_estimada"]
    meta = config.get("metas", {}).get("nota_meta", 90)
    delta = nota - meta
    
    st.metric(
        "📊 Nota Estimada",
        f"{nota}%",
        delta=f"{delta:+.1f}% da meta",
        delta_color="normal" if delta >= 0 else "inverse"
    )
    st.caption(f"Meta: {meta}% | Confiança: {stats['nota_estimada']['confianca']}")

with col2:
    media = stats["media_semanal"]
    
    st.metric(
        "📝 Questões/Semana Necessárias",
        f"{int(media['media_necessaria'])}",
        delta="No ritmo ✓" if media["no_ritmo"] else "Acelerar!",
        delta_color="normal" if media["no_ritmo"] else "inverse"
    )
    st.caption(f"Semanas restantes: {media['semanas_restantes']}")

with col3:
    st.metric(
        "✅ Total de Questões",
        f"{stats['questoes_total']:,}",
        delta=f"{stats['taxa_acerto_geral']:.1f}% acerto"
    )
    st.caption(f"Meta 2 anos: 33.500")

with col4:
    data_prova = config.get("usuario", {}).get("data_prova_estimada", "2027-11-15")
    dias = calcular_dias_ate_prova(data_prova)
    
    st.metric(
        "📅 Dias até a Prova",
        f"{dias}",
        delta=f"{dias // 7} semanas"
    )
    st.caption(f"Data: {datetime.strptime(data_prova, '%Y-%m-%d').strftime('%d/%m/%Y')}")

# Rodízio Atual
st.markdown("---")
rodizio = obter_rodizio_atual(calendario)

if rodizio:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"🏥 Rodízio Atual: {rodizio['rodizio']}")
        
        inicio = datetime.strptime(rodizio["inicio"], "%Y-%m-%d")
        fim = datetime.strptime(rodizio["fim"], "%Y-%m-%d")
        hoje = datetime.now()
        
        progresso = min(1.0, (hoje - inicio).days / (fim - inicio).days)
        
        st.progress(progresso, text=f"Progresso: {int(progresso * 100)}%")
        
        st.markdown(f"""
        **Período:** {inicio.strftime('%d/%m/%Y')} - {fim.strftime('%d/%m/%Y')}
        
        **Grande Área:** {rodizio['grande_area_principal']} 
        (Peso ENAMED: {pesos['pesos_areas'].get(rodizio['grande_area_principal'], 0) * 100:.1f}%)
        """)
    
    with col2:
        st.markdown("**🔥 Temas High-Yield do Rodízio:**")
        high_yield = pesos.get("temas_high_yield", {}).get(rodizio["grande_area_principal"], [])
        
        for tema in high_yield[:5]:
            st.markdown(f"• {tema}")
else:
    st.info("📅 Nenhum rodízio ativo no momento.")

# Alertas High-Yield
st.markdown("---")
st.subheader("⚠️ Alertas High-Yield")

alertas = obter_alertas()

if alertas:
    for alerta in alertas[:3]:
        st.markdown(f"""
        <div class="alert-high-yield">
            {alerta['mensagem']}<br>
            <small>Área: {alerta['area']}</small>
        </div>
        """, unsafe_allow_html=True)
else:
    st.success("✅ Todos os temas High-Yield prioritários estão em dia!")

# Plano da Semana
st.markdown("---")
st.subheader("📋 Plano da Semana")

plano = obter_plano_semanal()

if plano["temas"]:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Tabela de tarefas
        dados_tabela = []
        for t in plano["temas"][:7]:
            status_emoji = {
                "atrasada": "🔴",
                "disponivel": "🟡",
                "pendente": "🟢"
            }.get(t.get("status", "pendente"), "⚪")
            
            high_yield_emoji = "🔥" if t.get("is_high_yield") else ""
            
            dados_tabela.append({
                "Status": status_emoji,
                "Tema": f"{t['tema']} {high_yield_emoji}",
                "Área": t["grande_area"],
                "Revisão": f"{t['revisao']}ª",
                "Questões": t["questoes"]
            })
        
        df = pd.DataFrame(dados_tabela)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with col2:
        st.metric("Total Sugerido", f"{plano['total_sugerido']} questões")
        st.metric("Meta Semanal", f"{plano['meta_questoes']} questões")
        
        diferenca = plano['total_sugerido'] - plano['meta_questoes']
        if diferenca > 100:
            st.warning("⚠️ Acumulado alto. Priorize os atrasados!")
        elif diferenca < -100:
            st.success("✅ Abaixo da meta. Bom ritmo!")
else:
    st.info("📝 Nenhuma tarefa pendente. Registre seus estudos na página de Estudo.")

# Cobertura High-Yield
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Cobertura High-Yield por Área")
    
    cobertura = priorizador.calcular_cobertura_high_yield()
    
    for area, dados in cobertura["por_area"].items():
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.progress(dados["percentual"] / 100, text=f"{area}")
        with col_b:
            st.caption(f"{dados['revisados']}/{dados['total']} ({dados['percentual']}%)")

with col2:
    st.subheader("📈 Performance por Revisão")
    
    # Estatísticas por revisão (simulado)
    registro = estudo.get("registro_temas", {})
    
    r1_total, r1_acertos = 0, 0
    r2_total, r2_acertos = 0, 0
    r3_total, r3_acertos = 0, 0
    
    for tema, dados in registro.items():
        if dados.get("r1", {}).get("questoes"):
            r1_total += dados["r1"]["questoes"]
            r1_acertos += dados["r1"].get("acertos", 0)
        if dados.get("r2", {}).get("questoes"):
            r2_total += dados["r2"]["questoes"]
            r2_acertos += dados["r2"].get("acertos", 0)
        if dados.get("r3", {}).get("questoes"):
            r3_total += dados["r3"]["questoes"]
            r3_acertos += dados["r3"].get("acertos", 0)
    
    if r1_total > 0:
        st.metric("1ª Revisão", f"{(r1_acertos/r1_total*100):.1f}%", f"{r1_total} questões")
    else:
        st.metric("1ª Revisão", "---", "Nenhuma ainda")
    
    if r2_total > 0:
        st.metric("2ª Revisão", f"{(r2_acertos/r2_total*100):.1f}%", f"{r2_total} questões")
    else:
        st.metric("2ª Revisão", "---", "Nenhuma ainda")
    
    if r3_total > 0:
        st.metric("3ª Revisão", f"{(r3_acertos/r3_total*100):.1f}%", f"{r3_total} questões")
    else:
        st.metric("3ª Revisão", "---", "Nenhuma ainda")

# Sidebar
with st.sidebar:
    st.header("👤 Informações")
    
    nome = config.get("usuario", {}).get("nome", "Estudante")
    ano = config.get("usuario", {}).get("ano_estudo", 1)
    
    st.markdown(f"""
    **Nome:** {nome}
    
    **Ano de Estudo:** {ano}º ano
    
    **Banca:** {config.get('metas', {}).get('banca_principal', 'ENAMED')}
    
    **Meta:** {config.get('metas', {}).get('nota_meta', 90)}%
    """)
    
    st.markdown("---")
    
    st.header("🔗 Navegação Rápida")
    st.page_link("pages/1_configuracoes.py", label="⚙️ Configurações")
    st.page_link("pages/2_calendario.py", label="📅 Calendário")
    st.page_link("pages/3_temas.py", label="📚 Temas")
    st.page_link("pages/4_estudo.py", label="📝 Registrar Estudo")
    st.page_link("pages/5_questoes.py", label="❓ Banco de Questões")
    st.page_link("pages/6_metricas.py", label="📊 Métricas")
    st.page_link("pages/7_revisao_final.py", label="🎯 Revisão Final")
    
    st.markdown("---")
    
    st.caption(f"Última atualização: {estudo.get('ultima_atualizacao', 'Nunca')[:10] if estudo.get('ultima_atualizacao') else 'Nunca'}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>📚 Plataforma de Estudos para Residência Médica</p>
    <p>Baseado em Distributed Practice e análise estratégica ENAMED</p>
</div>
""", unsafe_allow_html=True)

