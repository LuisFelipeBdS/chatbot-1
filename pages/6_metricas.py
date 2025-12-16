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
from utils.styles import (
    inject_css, render_main_header, render_metric_card, 
    render_metrics_row, render_progress_bar, render_score_display,
    render_section_card
)
from core.metricas import SistemaMetricas, obter_estatisticas
from core.priorizador_enamed import PriorizadorENAMED
from utils.constants import CORES_DEGRADÊ

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

metrics_html = render_metrics_row([
    render_metric_card(
        icon="📊",
        label="Nota Estimada",
        value=f"{nota}%",
        delta=f"{'↑' if delta_nota >= 0 else '↓'} {abs(delta_nota):.1f}% da meta",
        delta_type="positive" if delta_nota >= 0 else "negative",
        footer=f"Confiança: {stats['nota_estimada']['confianca']}",
        color="primary"
    ),
    render_metric_card(
        icon="✅",
        label="Questões Feitas",
        value=f"{stats['questoes_total']:,}",
        delta=f"Meta: 33.500",
        delta_type="neutral",
        footer=f"Acertos: {stats['acertos_total']:,}",
        color="success"
    ),
    render_metric_card(
        icon="🎯",
        label="Taxa de Acerto",
        value=f"{stats['taxa_acerto_geral']:.1f}%",
        delta="Ótimo!" if stats['taxa_acerto_geral'] >= 80 else ("Bom" if stats['taxa_acerto_geral'] >= 60 else "Melhorar"),
        delta_type="positive" if stats['taxa_acerto_geral'] >= 70 else "negative",
        footer=f"Meta: {meta}%",
        color="success" if stats['taxa_acerto_geral'] >= 70 else "warning"
    ),
    render_metric_card(
        icon="📈",
        label="Simulados",
        value=f"{stats.get('simulados', 0)}",
        delta="Realize simulados!",
        delta_type="neutral",
        footer="Recomendado: 3+",
        color="secondary"
    )
])

st.markdown(metrics_html, unsafe_allow_html=True)

# Performance por área
st.markdown("---")

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
    
    progress_html = ""
    for area, estatisticas in stats_area.items():
        peso = pesos["pesos_areas"].get(area, 0) * 100
        
        if estatisticas["questoes"] > 0:
            taxa = estatisticas["acertos"] / estatisticas["questoes"] * 100
        else:
            taxa = 0
        
        if taxa >= 80:
            cor = "success"
        elif taxa >= 60:
            cor = "warning"
        else:
            cor = "danger"
        
        progress_html += f"""
        <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 0.85rem; color: #cbd5e1;">{area}</span>
                <span style="font-size: 0.85rem; color: #64748b;">Peso: {peso:.0f}%</span>
            </div>
            {render_progress_bar(f"Taxa: {taxa:.0f}%", taxa, 100, cor, False)}
        </div>
        """
    
    st.markdown(
        render_section_card(
            titulo="Performance por Grande Área",
            icon="📈",
            conteudo=progress_html,
            icon_color="success"
        ),
        unsafe_allow_html=True
    )

with col2:
    total_temas = len(registro) if registro else 1
    r1_count = sum(1 for d in registro.values() if d.get("r1"))
    r2_count = sum(1 for d in registro.values() if d.get("r2"))
    r3_count = sum(1 for d in registro.values() if d.get("r3"))
    
    revision_html = f"""
    {render_progress_bar("1ª Revisão", r1_count, total_temas, "primary", False)}
    {render_progress_bar("2ª Revisão", r2_count, total_temas, "secondary", False)}
    {render_progress_bar("3ª Revisão", r3_count, total_temas, "success", False)}
    
    <div style="margin-top: 2rem;">
        {render_score_display(nota, "Nota Estimada ENAMED", delta_nota, meta)}
    </div>
    """
    
    st.markdown(
        render_section_card(
            titulo="Progresso das Revisões",
            icon="📝",
            conteudo=revision_html,
            icon_color="primary"
        ),
        unsafe_allow_html=True
    )

# Cobertura High-Yield
st.markdown("---")

cobertura = priorizador.calcular_cobertura_high_yield()

cobertura_html = ""
for area, dados in cobertura["por_area"].items():
    if dados["percentual"] >= 80:
        cor = "success"
    elif dados["percentual"] >= 50:
        cor = "warning"
    else:
        cor = "danger"
    
    cobertura_html += render_progress_bar(
        f"{area}",
        dados["revisados"],
        dados["total"],
        cor,
        True
    )

st.markdown(
    render_section_card(
        titulo="Cobertura High-Yield por Área",
        icon="🔥",
        conteudo=cobertura_html,
        icon_color="warning"
    ),
    unsafe_allow_html=True
)

# Histórico
st.markdown("---")

if registro:
    historico = []
    
    for tema, dados in registro.items():
        if dados.get("data_teoria"):
            historico.append({
                "Data": dados["data_teoria"],
                "Tipo": "Teoria",
                "Tema": tema[:30],
                "Questões": 0
            })
        
        for rev in ["r1", "r2", "r3"]:
            rev_dados = dados.get(rev, {})
            if rev_dados.get("data"):
                historico.append({
                    "Data": rev_dados["data"],
                    "Tipo": rev.upper(),
                    "Tema": tema[:30],
                    "Questões": rev_dados.get("questoes", 0)
                })
    
    if historico:
        historico.sort(key=lambda x: x["Data"], reverse=True)
        
        st.markdown(
            render_section_card(
                titulo="Histórico de Estudo",
                icon="📅",
                conteudo="",
                icon_color="primary"
            ),
            unsafe_allow_html=True
        )
        
        df_hist = pd.DataFrame(historico[:15])
        st.dataframe(df_hist, use_container_width=True, hide_index=True)

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
    
    st.markdown("""
    ### 📖 Interpretação
    
    **Setinhas:**
    - ⬇️⬇️ Muito abaixo
    - ⬇️ Abaixo
    - ➡️ Esperado
    - ⬆️ Acima
    - ⬆️⬆️ Muito acima
    
    **Cores:**
    - 🔴 Crítico (<60%)
    - 🟡 Atenção (60-80%)
    - 🟢 Bom (>80%)
    """)
