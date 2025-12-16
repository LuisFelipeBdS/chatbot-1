"""
Página de Calendário Acadêmico
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import (
    carregar_calendario, carregar_config, carregar_pesos,
    obter_rodizio_atual, salvar_json
)

st.set_page_config(
    page_title="Calendário - Plataforma de Estudos",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Calendário Acadêmico")
st.markdown("---")

# Carregar dados
calendario = carregar_calendario()
config = carregar_config()
pesos = carregar_pesos()

# Verificar rodízio atual
rodizio_atual = obter_rodizio_atual(calendario)

# Mostrar rodízio atual
if rodizio_atual:
    st.success(f"""
    ### 🏥 Rodízio Atual: **{rodizio_atual['rodizio']}**
    
    📆 Período: {rodizio_atual['inicio']} até {rodizio_atual['fim']}
    
    📚 Grande Área: {rodizio_atual['grande_area_principal']}
    """)
    
    st.markdown("**Temas Prioritários para este rodízio:**")
    cols = st.columns(3)
    for i, tema in enumerate(rodizio_atual.get("temas_prioritarios", [])):
        cols[i % 3].markdown(f"• {tema}")
else:
    st.info("📅 Nenhum rodízio ativo no momento. Configure seu calendário abaixo.")

st.markdown("---")

# Tabs para cada ano
tab1, tab2 = st.tabs(["📆 Ano 1 (2026)", "📆 Ano 2 (2027)"])

with tab1:
    st.header("Rodízios do 5º Ano - 9º e 10º Períodos")
    
    rodizios_ano1 = calendario.get("ano_1", {}).get("2026", [])
    
    if rodizios_ano1:
        # Criar DataFrame para visualização
        dados_tabela = []
        for r in rodizios_ano1:
            inicio = datetime.strptime(r["inicio"], "%Y-%m-%d")
            fim = datetime.strptime(r["fim"], "%Y-%m-%d")
            duracao = (fim - inicio).days + 1
            
            dados_tabela.append({
                "Rodízio": r["rodizio"],
                "Início": inicio.strftime("%d/%m/%Y"),
                "Fim": fim.strftime("%d/%m/%Y"),
                "Duração": f"{duracao} dias",
                "Grande Área": r["grande_area_principal"],
                "Qtd Temas": len(r.get("temas_prioritarios", []))
            })
        
        df = pd.DataFrame(dados_tabela)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Timeline visual
        st.markdown("### 📊 Timeline do Ano")
        
        for i, r in enumerate(rodizios_ano1):
            inicio = datetime.strptime(r["inicio"], "%Y-%m-%d")
            fim = datetime.strptime(r["fim"], "%Y-%m-%d")
            
            # Calcular progresso se estiver no período
            hoje = datetime.now()
            if inicio <= hoje <= fim:
                progresso = (hoje - inicio).days / (fim - inicio).days
                status = "🟢 Em andamento"
            elif hoje > fim:
                progresso = 1.0
                status = "✅ Concluído"
            else:
                progresso = 0.0
                status = "⏳ Pendente"
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{r['rodizio']}** - {status}")
                st.progress(progresso)
            with col2:
                st.caption(f"{inicio.strftime('%d/%m')} - {fim.strftime('%d/%m')}")
        
        # Expandir detalhes de cada rodízio
        st.markdown("### 📝 Detalhes por Rodízio")
        
        for r in rodizios_ano1:
            with st.expander(f"🏥 {r['rodizio']} - {r['grande_area_principal']}"):
                st.markdown(f"""
                **Período:** {r['inicio']} até {r['fim']}
                
                **Grande Área Principal:** {r['grande_area_principal']}
                
                **Peso ENAMED:** {pesos['pesos_areas'].get(r['grande_area_principal'], 0) * 100:.1f}%
                
                **Temas Prioritários para estudo:**
                """)
                
                # Mostrar temas em colunas
                temas = r.get("temas_prioritarios", [])
                cols = st.columns(2)
                for i, tema in enumerate(temas):
                    # Verificar se é high-yield
                    high_yield_temas = pesos.get("temas_high_yield", {}).get(r['grande_area_principal'], [])
                    is_high_yield = any(t.lower() in tema.lower() for t in high_yield_temas)
                    
                    icon = "🔥" if is_high_yield else "📖"
                    cols[i % 2].markdown(f"{icon} {tema}")
    else:
        st.warning("Nenhum rodízio cadastrado para 2026.")

with tab2:
    st.header("Rodízios do 6º Ano - 11º e 12º Períodos")
    
    rodizios_ano2 = calendario.get("ano_2", {}).get("2027", [])
    
    if rodizios_ano2:
        # Similar ao ano 1
        dados_tabela = []
        for r in rodizios_ano2:
            inicio = datetime.strptime(r["inicio"], "%Y-%m-%d")
            fim = datetime.strptime(r["fim"], "%Y-%m-%d")
            duracao = (fim - inicio).days + 1
            
            dados_tabela.append({
                "Rodízio": r["rodizio"],
                "Início": inicio.strftime("%d/%m/%Y"),
                "Fim": fim.strftime("%d/%m/%Y"),
                "Duração": f"{duracao} dias",
                "Grande Área": r["grande_area_principal"]
            })
        
        df = pd.DataFrame(dados_tabela)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("""
        📅 **Rodízios de 2027 ainda não cadastrados.**
        
        Você poderá adicionar os rodízios do segundo ano quando tiver o calendário disponível.
        """)
        
        # Formulário para adicionar rodízios
        st.markdown("### ➕ Adicionar Rodízio")
        
        with st.form("novo_rodizio"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome_rodizio = st.text_input("Nome do Rodízio")
                grande_area = st.selectbox(
                    "Grande Área",
                    options=[
                        "Clinica Medica",
                        "Saude Coletiva",
                        "Pediatria",
                        "Ginecologia e Obstetricia",
                        "Cirurgia Geral",
                        "Saude Mental"
                    ]
                )
            
            with col2:
                data_inicio = st.date_input("Data de Início", value=date(2027, 1, 15))
                data_fim = st.date_input("Data de Fim", value=date(2027, 3, 15))
            
            temas_prioritarios = st.text_area(
                "Temas Prioritários (um por linha)",
                placeholder="Exemplo:\nTuberculose\nHIV\nPneumonias"
            )
            
            submitted = st.form_submit_button("Adicionar Rodízio", type="primary")
            
            if submitted and nome_rodizio:
                novo_rodizio = {
                    "rodizio": nome_rodizio,
                    "inicio": data_inicio.strftime("%Y-%m-%d"),
                    "fim": data_fim.strftime("%Y-%m-%d"),
                    "temas_prioritarios": [t.strip() for t in temas_prioritarios.split("\n") if t.strip()],
                    "grande_area_principal": grande_area
                }
                
                if "2027" not in calendario.get("ano_2", {}):
                    calendario["ano_2"]["2027"] = []
                
                calendario["ano_2"]["2027"].append(novo_rodizio)
                salvar_json("calendario.json", calendario)
                
                st.success(f"✅ Rodízio '{nome_rodizio}' adicionado com sucesso!")
                st.rerun()

# Sidebar com estatísticas
with st.sidebar:
    st.header("📊 Estatísticas")
    
    total_rodizios = len(rodizios_ano1) + len(rodizios_ano2)
    st.metric("Total de Rodízios", total_rodizios)
    
    if rodizio_atual:
        dias_restantes_rodizio = (
            datetime.strptime(rodizio_atual["fim"], "%Y-%m-%d") - datetime.now()
        ).days
        st.metric("Dias até fim do rodízio atual", max(0, dias_restantes_rodizio))
    
    st.markdown("---")
    st.markdown("""
    ### 💡 Dica
    
    Durante cada rodízio, priorize os temas 
    relacionados para aproveitar a prática clínica.
    
    O sistema aplica um **bônus de 20%** 
    para questões do rodízio atual!
    """)
    
    st.markdown("---")
    st.markdown("### 🔥 Temas High-Yield")
    
    if rodizio_atual:
        area = rodizio_atual.get("grande_area_principal", "")
        high_yield = pesos.get("temas_high_yield", {}).get(area, [])
        
        if high_yield:
            for tema in high_yield[:5]:
                st.markdown(f"• {tema}")

