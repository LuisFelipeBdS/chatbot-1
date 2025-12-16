"""
Página de Registro de Estudos/Revisões
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import (
    carregar_estudo, salvar_estudo, carregar_temas,
    carregar_config, carregar_pesos
)
from core.calculadora_revisoes import CalculadoraRevisoes, calcular_datas_revisao
from core.algoritmo_sugestao import AlgoritmoSugestao
from core.priorizador_enamed import PriorizadorENAMED

st.set_page_config(
    page_title="Registro de Estudo - Plataforma de Estudos",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Registro de Estudos")
st.markdown("---")

# Carregar dados
estudo = carregar_estudo()
temas = carregar_temas()
config = carregar_config()
pesos = carregar_pesos()

calc_rev = CalculadoraRevisoes()
algoritmo = AlgoritmoSugestao()
priorizador = PriorizadorENAMED()

# Tabs
tab1, tab2, tab3 = st.tabs(["📖 Registrar Teoria", "📝 Registrar Revisão", "📋 Meus Registros"])

with tab1:
    st.header("Registrar Teoria Estudada")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Selecionar área
        area_teoria = st.selectbox(
            "Grande Área",
            options=list(temas.get("grandes_areas", {}).keys()),
            key="area_teoria"
        )
        
        # Selecionar tema
        temas_area = [t["nome"] for t in temas["grandes_areas"][area_teoria]["temas"]]
        tema_teoria = st.selectbox(
            "Tema",
            options=temas_area,
            key="tema_teoria"
        )
    
    with col2:
        data_teoria = st.date_input(
            "Data do Estudo da Teoria",
            value=date.today(),
            key="data_teoria"
        )
        
        # Mostrar classificação
        classif = priorizador.classificar_tema(tema_teoria, area_teoria)
        st.info(f"{classif['icone']} **{classif['classificacao'].replace('_', ' ').title()}**: {classif['descricao']}")
    
    # Preview do cronograma
    if st.checkbox("Ver cronograma de revisões sugerido", key="preview_teoria"):
        cronograma = calcular_datas_revisao(data_teoria.strftime("%Y-%m-%d"), tema_teoria)
        
        st.markdown("**Cronograma Sugerido:**")
        for rev, dados in cronograma["revisoes"].items():
            data_sug = datetime.strptime(dados["data_sugerida"], "%Y-%m-%d")
            st.markdown(f"- **{rev.upper()}**: {data_sug.strftime('%d/%m/%Y')} ({int(dados['percentual_questoes']*100)}% das questões)")
    
    if st.button("💾 Registrar Teoria", type="primary", key="btn_teoria"):
        registro = estudo.get("registro_temas", {})
        
        if tema_teoria not in registro:
            registro[tema_teoria] = {}
        
        registro[tema_teoria]["data_teoria"] = data_teoria.strftime("%Y-%m-%d")
        registro[tema_teoria]["grande_area"] = area_teoria
        
        estudo["registro_temas"] = registro
        salvar_estudo(estudo)
        
        st.success(f"✅ Teoria de '{tema_teoria}' registrada!")
        st.balloons()

with tab2:
    st.header("Registrar Revisão de Questões")
    
    # Filtrar temas com teoria registrada
    temas_com_teoria = [
        tema for tema, dados in estudo.get("registro_temas", {}).items()
        if dados.get("data_teoria")
    ]
    
    if not temas_com_teoria:
        st.warning("⚠️ Nenhum tema com teoria registrada. Registre a teoria primeiro.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            tema_revisao = st.selectbox(
                "Tema",
                options=temas_com_teoria,
                key="tema_revisao"
            )
            
            # Determinar qual revisão é a próxima
            registro_tema = estudo["registro_temas"].get(tema_revisao, {})
            
            proxima_rev = 1
            if registro_tema.get("r1", {}).get("data"):
                proxima_rev = 2
            if registro_tema.get("r2", {}).get("data"):
                proxima_rev = 3
            if registro_tema.get("r3", {}).get("data"):
                proxima_rev = 0  # Todas feitas
            
            if proxima_rev == 0:
                st.success("✅ Todas as 3 revisões concluídas para este tema!")
                numero_revisao = st.selectbox(
                    "Refazer Revisão",
                    options=[1, 2, 3],
                    key="num_rev"
                )
            else:
                st.info(f"📝 Próxima revisão: **{proxima_rev}ª Revisão**")
                numero_revisao = st.selectbox(
                    "Número da Revisão",
                    options=[proxima_rev],
                    index=0,
                    key="num_rev"
                )
        
        with col2:
            data_revisao = st.date_input(
                "Data da Revisão",
                value=date.today(),
                key="data_revisao"
            )
            
            # Calcular sugestão de questões
            area = registro_tema.get("grande_area", "Clinica Medica")
            sugestao = algoritmo.calcular_sugestao_tema(tema_revisao, area, numero_revisao, tema_revisao)
            
            st.info(f"💡 Sugestão: **{sugestao['questoes_sugeridas']} questões**")
        
        col3, col4 = st.columns(2)
        
        with col3:
            questoes_feitas = st.number_input(
                "Questões Feitas",
                min_value=1,
                max_value=1000,
                value=sugestao['questoes_sugeridas'],
                key="questoes_feitas"
            )
        
        with col4:
            acertos = st.number_input(
                "Acertos",
                min_value=0,
                max_value=questoes_feitas,
                value=int(questoes_feitas * 0.7),
                key="acertos"
            )
        
        # Mostrar porcentagem
        if questoes_feitas > 0:
            porcentagem = (acertos / questoes_feitas) * 100
            
            if porcentagem >= 80:
                st.success(f"📊 Taxa de acerto: **{porcentagem:.1f}%** - Excelente!")
            elif porcentagem >= 60:
                st.info(f"📊 Taxa de acerto: **{porcentagem:.1f}%** - Bom!")
            else:
                st.warning(f"📊 Taxa de acerto: **{porcentagem:.1f}%** - Precisa revisar mais!")
        
        if st.button("💾 Registrar Revisão", type="primary", key="btn_revisao"):
            registro = estudo.get("registro_temas", {})
            
            rev_key = f"r{numero_revisao}"
            
            registro[tema_revisao][rev_key] = {
                "data": data_revisao.strftime("%Y-%m-%d"),
                "questoes": questoes_feitas,
                "acertos": acertos
            }
            
            # Atualizar estatísticas gerais
            stats = estudo.get("estatisticas_gerais", {})
            stats["total_questoes_feitas"] = stats.get("total_questoes_feitas", 0) + questoes_feitas
            stats["total_acertos"] = stats.get("total_acertos", 0) + acertos
            
            estudo["registro_temas"] = registro
            estudo["estatisticas_gerais"] = stats
            salvar_estudo(estudo)
            
            st.success(f"✅ {numero_revisao}ª revisão de '{tema_revisao}' registrada!")
            st.balloons()

with tab3:
    st.header("Meus Registros de Estudo")
    
    registro = estudo.get("registro_temas", {})
    
    if not registro:
        st.info("📝 Nenhum registro ainda. Comece registrando uma teoria!")
    else:
        # Preparar dados
        dados_tabela = []
        
        for tema, dados in registro.items():
            r1 = dados.get("r1", {})
            r2 = dados.get("r2", {})
            r3 = dados.get("r3", {})
            
            def calc_perc(rev_dados):
                if rev_dados.get("questoes"):
                    return f"{(rev_dados.get('acertos', 0) / rev_dados['questoes'] * 100):.0f}%"
                return "---"
            
            dados_tabela.append({
                "Tema": tema[:40] + "..." if len(tema) > 40 else tema,
                "Área": dados.get("grande_area", "---")[:15],
                "Teoria": dados.get("data_teoria", "---")[:10],
                "R1 Data": r1.get("data", "---")[:10] if r1 else "---",
                "R1 %": calc_perc(r1),
                "R2 Data": r2.get("data", "---")[:10] if r2 else "---",
                "R2 %": calc_perc(r2),
                "R3 Data": r3.get("data", "---")[:10] if r3 else "---",
                "R3 %": calc_perc(r3)
            })
        
        df = pd.DataFrame(dados_tabela)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Estatísticas
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Temas Registrados", len(registro))
        
        with col2:
            r1_feitas = sum(1 for d in registro.values() if d.get("r1"))
            st.metric("1ª Revisões", r1_feitas)
        
        with col3:
            r2_feitas = sum(1 for d in registro.values() if d.get("r2"))
            st.metric("2ª Revisões", r2_feitas)
        
        with col4:
            r3_feitas = sum(1 for d in registro.values() if d.get("r3"))
            st.metric("3ª Revisões", r3_feitas)

# Sidebar
with st.sidebar:
    st.header("📊 Resumo do Dia")
    
    stats = estudo.get("estatisticas_gerais", {})
    
    st.metric("Total de Questões", stats.get("total_questoes_feitas", 0))
    
    if stats.get("total_questoes_feitas", 0) > 0:
        taxa = stats.get("total_acertos", 0) / stats["total_questoes_feitas"] * 100
        st.metric("Taxa de Acerto Geral", f"{taxa:.1f}%")
    
    st.markdown("---")
    
    st.markdown("""
    ### 📖 Como Funciona
    
    1. **Registre a Teoria** quando assistir uma aula
    2. **Aguarde o intervalo** sugerido (Distributed Practice)
    3. **Faça as questões** e registre a revisão
    4. **Repita** para R2 e R3
    
    ---
    
    ### ⏰ Intervalos
    
    - Teoria → R1: ~21 dias
    - R1 → R2: ~30 dias
    - R2 → R3: ~30 dias
    
    *Intervalos diminuem perto da prova*
    """)

