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
from core.metricas import SistemaMetricas, obter_estatisticas
from core.priorizador_enamed import PriorizadorENAMED
from utils.constants import CORES_DEGRADÊ

st.set_page_config(
    page_title="Métricas - Plataforma de Estudos",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Métricas e Relatórios")
st.markdown("---")

# Carregar dados
estudo = carregar_estudo()
config = carregar_config()
pesos = carregar_pesos()

metricas = SistemaMetricas()
priorizador = PriorizadorENAMED()
stats = obter_estatisticas()

# Métricas principais
st.header("📈 Visão Geral")

col1, col2, col3, col4 = st.columns(4)

with col1:
    nota = stats["nota_estimada"]
    setinha = stats["setinha"]
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: {setinha['cor']}20; border-radius: 10px;">
        <h1 style="margin: 0; color: {setinha['cor']}">{nota['nota_estimada']}%</h1>
        <p style="margin: 5px 0; font-size: 2rem;">{setinha['icone']}</p>
        <p style="margin: 0; color: #666;">Nota Estimada</p>
        <p style="margin: 0; font-size: 0.8rem; color: #999;">Confiança: {nota['confianca']}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    media = stats["media_semanal"]
    cor = "#28a745" if media["no_ritmo"] else "#dc3545"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: {cor}20; border-radius: 10px;">
        <h1 style="margin: 0; color: {cor}">{int(media['media_necessaria'])}</h1>
        <p style="margin: 5px 0;">questões/semana</p>
        <p style="margin: 0; color: #666;">Necessárias</p>
        <p style="margin: 0; font-size: 0.8rem; color: #999;">{media['semanas_restantes']} semanas restantes</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: #17a2b820; border-radius: 10px;">
        <h1 style="margin: 0; color: #17a2b8">{stats['questoes_total']:,}</h1>
        <p style="margin: 5px 0;">questões feitas</p>
        <p style="margin: 0; color: #666;">Total</p>
        <p style="margin: 0; font-size: 0.8rem; color: #999;">Meta: 33.500</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    taxa = stats["taxa_acerto_geral"]
    cor_taxa = CORES_DEGRADÊ[int(min(24, taxa / 100 * 24))]
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: {cor_taxa}20; border-radius: 10px;">
        <h1 style="margin: 0; color: {cor_taxa}">{taxa:.1f}%</h1>
        <p style="margin: 5px 0;">de acerto</p>
        <p style="margin: 0; color: #666;">Taxa Geral</p>
        <p style="margin: 0; font-size: 0.8rem; color: #999;">Acertos: {stats['acertos_total']:,}</p>
    </div>
    """, unsafe_allow_html=True)

# Performance por área
st.markdown("---")
st.header("📊 Performance por Grande Área")

registro = estudo.get("registro_temas", {})

# Calcular estatísticas por área
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

# Criar tabela
dados_tabela = []
for area, estatisticas in stats_area.items():
    peso = pesos["pesos_areas"].get(area, 0) * 100
    
    if estatisticas["questoes"] > 0:
        taxa = estatisticas["acertos"] / estatisticas["questoes"] * 100
    else:
        taxa = 0
    
    # Cor baseada na taxa
    cor_idx = int(min(24, taxa / 100 * 24))
    
    dados_tabela.append({
        "Área": area,
        "Peso ENAMED": f"{peso:.1f}%",
        "Temas Estudados": estatisticas["temas"],
        "Questões": estatisticas["questoes"],
        "Taxa de Acerto": f"{taxa:.1f}%",
        "Status": "✅" if taxa >= 70 else ("⚠️" if taxa >= 50 else "❌")
    })

df = pd.DataFrame(dados_tabela)
st.dataframe(df, use_container_width=True, hide_index=True)

# Gráfico de progresso
st.markdown("---")
st.header("📈 Progresso das Revisões")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Por Revisão")
    
    r1_count = sum(1 for d in registro.values() if d.get("r1"))
    r2_count = sum(1 for d in registro.values() if d.get("r2"))
    r3_count = sum(1 for d in registro.values() if d.get("r3"))
    total_temas = len(registro)
    
    if total_temas > 0:
        st.progress(r1_count / total_temas, text=f"1ª Revisão: {r1_count}/{total_temas}")
        st.progress(r2_count / total_temas, text=f"2ª Revisão: {r2_count}/{total_temas}")
        st.progress(r3_count / total_temas, text=f"3ª Revisão: {r3_count}/{total_temas}")
    else:
        st.info("Nenhum tema registrado ainda.")

with col2:
    st.subheader("Cobertura High-Yield")
    
    cobertura = priorizador.calcular_cobertura_high_yield()
    
    total_hy = cobertura["total"]["high_yield_total"]
    revisados_hy = cobertura["total"]["high_yield_revisados"]
    
    if total_hy > 0:
        st.progress(
            revisados_hy / total_hy,
            text=f"High-Yield: {revisados_hy}/{total_hy} ({cobertura['total']['percentual_cobertura']}%)"
        )
    
    # Por área
    for area, dados in cobertura["por_area"].items():
        if dados["total"] > 0:
            st.caption(f"{area}: {dados['revisados']}/{dados['total']}")

# Histórico
st.markdown("---")
st.header("📅 Histórico de Estudo")

# Simular histórico baseado nos registros
if registro:
    historico = []
    
    for tema, dados in registro.items():
        if dados.get("data_teoria"):
            historico.append({
                "data": dados["data_teoria"],
                "tipo": "Teoria",
                "tema": tema,
                "questoes": 0
            })
        
        for rev in ["r1", "r2", "r3"]:
            rev_dados = dados.get(rev, {})
            if rev_dados.get("data"):
                historico.append({
                    "data": rev_dados["data"],
                    "tipo": f"{rev.upper()}",
                    "tema": tema,
                    "questoes": rev_dados.get("questoes", 0)
                })
    
    if historico:
        # Ordenar por data
        historico.sort(key=lambda x: x["data"], reverse=True)
        
        # Mostrar últimos 10
        df_hist = pd.DataFrame(historico[:15])
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum histórico disponível.")
else:
    st.info("Comece a registrar seus estudos para ver o histórico.")

# Sidebar
with st.sidebar:
    st.header("🎯 Meta vs Atual")
    
    meta = config.get("metas", {}).get("nota_meta", 90)
    atual = stats["nota_estimada"]["nota_estimada"]
    
    diferenca = atual - meta
    
    if diferenca >= 0:
        st.success(f"✅ {diferenca:+.1f} pontos acima da meta!")
    else:
        st.warning(f"⚠️ {diferenca:.1f} pontos abaixo da meta")
    
    st.progress(min(1.0, atual / 100), text=f"Nota: {atual}%")
    st.caption(f"Meta: {meta}%")
    
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
    - 🔴 Crítico
    - 🟡 Atenção
    - 🟢 Bom
    """)

