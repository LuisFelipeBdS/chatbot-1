"""
Página de Métricas e Relatórios
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import carregar_estudo, carregar_config, carregar_pesos
from utils.styles import inject_css, render_main_header
from core.metricas import SistemaMetricas, obter_estatisticas
from core.priorizador_enamed import PriorizadorENAMED

st.set_page_config(
    page_title="Métricas - Plataforma de Estudos",
    page_icon="📊",
    layout="wide"
)

# Injetar CSS
inject_css()

# Header
st.markdown(
    render_main_header("📊 Métricas e Relatórios", "Acompanhe sua evolução"),
    unsafe_allow_html=True
)

# Carregar dados
estudo = carregar_estudo()
config = carregar_config()
pesos = carregar_pesos()

metricas = SistemaMetricas()
priorizador = PriorizadorENAMED()
stats = obter_estatisticas()

# Métricas principais
nota = stats["nota_estimada"]["nota_estimada"]
meta = config.get("metas", {}).get("nota_meta", 90)
delta_nota = nota - meta

# Usando colunas nativas do Streamlit com st.metric
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 Nota Estimada",
        value=f"{nota}%",
        delta=f"{delta_nota:+.1f}% da meta",
        delta_color="normal" if delta_nota >= 0 else "inverse"
    )
    st.caption(f"Confiança: {stats['nota_estimada']['confianca']}")

with col2:
    st.metric(
        label="✅ Questões Feitas",
        value=f"{stats['questoes_total']:,}",
        delta=f"Acertos: {stats['acertos_total']:,}"
    )
    st.caption("Meta 2 anos: 33.500")

with col3:
    st.metric(
        label="🎯 Taxa de Acerto",
        value=f"{stats['taxa_acerto_geral']:.1f}%",
        delta="Ótimo!" if stats['taxa_acerto_geral'] >= 80 else ("Bom" if stats['taxa_acerto_geral'] >= 60 else "Melhorar"),
        delta_color="normal" if stats['taxa_acerto_geral'] >= 70 else "inverse"
    )
    st.caption(f"Meta: {meta}%")

with col4:
    st.metric(
        label="📈 Simulados",
        value=f"{stats.get('simulados', 0)}",
        delta="Realize simulados!"
    )
    st.caption("Recomendado: 3+")

# Performance por área
st.markdown("---")
st.subheader("📈 Performance por Grande Área")

col1, col2 = st.columns(2)

with col1:
    registro = estudo.get("registro_temas", {})
    
    stats_area = {}
    for area in pesos["pesos_areas"].keys():
        stats_area[area] = {"questoes": 0, "acertos": 0, "temas": 0}
    
    for tema, dados in registro.items():
        area = dados.get("grande_area", "Clinica Medica")
        
        if area in stats_area:
            stats_area[area]["temas"] += 1
            
            for rev in ["r1", "r2", "r3"]:
                rev_dados = dados.get(rev, {})
                if rev_dados.get("questoes"):
                    stats_area[area]["questoes"] += rev_dados["questoes"]
                    stats_area[area]["acertos"] += rev_dados.get("acertos", 0)
    
    for area, estatisticas in stats_area.items():
        peso = pesos["pesos_areas"].get(area, 0) * 100
        
        if estatisticas["questoes"] > 0:
            taxa = estatisticas["acertos"] / estatisticas["questoes"] * 100
        else:
            taxa = 0
        
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.progress(min(1.0, taxa / 100), text=f"{area}")
        with col_b:
            cor = "🟢" if taxa >= 80 else ("🟡" if taxa >= 60 else "🔴")
            st.markdown(f"{cor} **{taxa:.0f}%**")

with col2:
    st.markdown("**📝 Progresso das Revisões**")
    
    total_temas = len(registro) if registro else 1
    r1_count = sum(1 for d in registro.values() if d.get("r1"))
    r2_count = sum(1 for d in registro.values() if d.get("r2"))
    r3_count = sum(1 for d in registro.values() if d.get("r3"))
    
    st.progress(r1_count / total_temas if total_temas > 0 else 0, text=f"1ª Revisão: {r1_count}/{total_temas}")
    st.progress(r2_count / total_temas if total_temas > 0 else 0, text=f"2ª Revisão: {r2_count}/{total_temas}")
    st.progress(r3_count / total_temas if total_temas > 0 else 0, text=f"3ª Revisão: {r3_count}/{total_temas}")
    
    st.markdown("---")
    
    # Score display
    st.markdown(f"""
    <div style="text-align: center; padding: 1.5rem; background: rgba(59, 130, 246, 0.1); border-radius: 12px;">
        <div style="font-size: 3rem; font-weight: 800; color: #3b82f6;">{nota:.1f}%</div>
        <div style="color: #94a3b8;">Nota Estimada ENAMED</div>
        <div style="margin-top: 0.5rem; color: {'#10b981' if delta_nota >= 0 else '#ef4444'};">
            {'⬆️' if delta_nota >= 0 else '⬇️'} {abs(delta_nota):.1f}% {'acima' if delta_nota >= 0 else 'abaixo'} da meta
        </div>
    </div>
    """, unsafe_allow_html=True)

# Cobertura High-Yield
st.markdown("---")
st.subheader("🔥 Cobertura High-Yield por Área")

cobertura = priorizador.calcular_cobertura_high_yield()

cols = st.columns(3)
col_idx = 0

for area, dados in cobertura["por_area"].items():
    with cols[col_idx % 3]:
        perc = dados["percentual"]
        cor = "🟢" if perc >= 80 else ("🟡" if perc >= 50 else "🔴")
        
        st.markdown(f"**{area}**")
        st.progress(perc / 100, text=f"{cor} {dados['revisados']}/{dados['total']} ({perc:.0f}%)")
    
    col_idx += 1

# Histórico
st.markdown("---")
st.subheader("📅 Histórico de Estudo")

if registro:
    historico = []
    
    for tema, dados in registro.items():
        if dados.get("data_teoria"):
            historico.append({
                "Data": dados["data_teoria"],
                "Tipo": "📖 Teoria",
                "Tema": tema[:35] + "..." if len(tema) > 35 else tema,
                "Questões": "-"
            })
        
        for rev in ["r1", "r2", "r3"]:
            rev_dados = dados.get(rev, {})
            if rev_dados.get("data"):
                historico.append({
                    "Data": rev_dados["data"],
                    "Tipo": f"📝 {rev.upper()}",
                    "Tema": tema[:35] + "..." if len(tema) > 35 else tema,
                    "Questões": rev_dados.get("questoes", 0)
                })
    
    if historico:
        historico.sort(key=lambda x: x["Data"], reverse=True)
        df_hist = pd.DataFrame(historico[:15])
        st.dataframe(df_hist, width="stretch", hide_index=True)
    else:
        st.info("📝 Nenhum registro ainda. Comece a estudar!")
else:
    st.info("📝 Nenhum registro de estudo ainda.")

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 Meta vs Atual")
    
    diferenca = nota - meta
    
    if diferenca >= 0:
        st.success(f"✅ {diferenca:+.1f} pontos acima!")
    else:
        st.warning(f"⚠️ {diferenca:.1f} pontos abaixo")
    
    st.progress(min(1.0, nota / 100))
    st.caption(f"Nota: {nota}% | Meta: {meta}%")
    
    st.markdown("---")
    
    # Resumo rápido
    st.markdown("### 📊 Resumo")
    st.metric("Temas Estudados", len(registro))
    st.metric("Questões Total", stats['questoes_total'])
    
    st.markdown("---")
    
    st.markdown("""
    ### 📖 Interpretação
    
    **Cores:**
    - 🟢 Bom (≥80%)
    - 🟡 Atenção (60-80%)
    - 🔴 Crítico (<60%)
    """)
