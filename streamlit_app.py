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
from utils.styles import (
    inject_css, render_main_header, render_metric_card,
    render_metrics_row, render_rotation_card, render_no_rotation,
    render_alert, render_section_card, render_progress_bar,
    render_countdown, render_score_display, render_status_badge,
    render_hy_badge
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
    st.markdown("""
    <div class="section-card">
        <div class="section-body" style="text-align: center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚙️</div>
            <h2 style="color: #f8fafc; margin-bottom: 1rem;">Configure o sistema para começar!</h2>
            <p style="color: #94a3b8; margin-bottom: 1.5rem;">
                Acesse a página de <strong>Configurações</strong> no menu lateral para definir:
            </p>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; color: #cbd5e1;">
                <span>📋 Seus dados pessoais</span>
                <span>🎯 Meta de nota</span>
                <span>📊 Diagnóstico inicial</span>
                <span>⚡ Modo de estudo</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("👈 Clique em **configuracoes** no menu lateral para começar.")
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

# Obter estatísticas
stats = obter_estatisticas()
data_prova = config.get("usuario", {}).get("data_prova_estimada", "2027-11-15")
dias = calcular_dias_ate_prova(data_prova)
meta = config.get("metas", {}).get("nota_meta", 90)

# ============================================
# MÉTRICAS PRINCIPAIS
# ============================================

nota = stats["nota_estimada"]["nota_estimada"]
delta_nota = nota - meta
delta_type_nota = "positive" if delta_nota >= 0 else "negative"

media = stats["media_semanal"]
delta_type_media = "positive" if media["no_ritmo"] else "negative"

metrics_html = render_metrics_row([
    render_metric_card(
        icon="📊",
        label="Nota Estimada",
        value=f"{nota}%",
        delta=f"{'↑' if delta_nota >= 0 else '↓'} {abs(delta_nota):.1f}% da meta",
        delta_type=delta_type_nota,
        footer=f"Meta: {meta}% | Confiança: {stats['nota_estimada']['confianca']}",
        color="primary"
    ),
    render_metric_card(
        icon="📝",
        label="Questões/Semana",
        value=f"{int(media['media_necessaria'])}",
        delta="✓ No ritmo" if media["no_ritmo"] else "↑ Acelerar!",
        delta_type=delta_type_media,
        footer=f"Semanas restantes: {media['semanas_restantes']}",
        color="success" if media["no_ritmo"] else "warning"
    ),
    render_metric_card(
        icon="✅",
        label="Total de Questões",
        value=f"{stats['questoes_total']:,}",
        delta=f"↑ {stats['taxa_acerto_geral']:.1f}% acerto",
        delta_type="positive" if stats['taxa_acerto_geral'] >= 70 else "neutral",
        footer="Meta 2 anos: 33.500",
        color="success"
    ),
    render_metric_card(
        icon="📅",
        label="Dias até a Prova",
        value=f"{dias}",
        delta=f"≈ {dias // 7} semanas",
        delta_type="neutral",
        footer=f"Data: {datetime.strptime(data_prova, '%Y-%m-%d').strftime('%d/%m/%Y')}",
        color="warning" if dias < 180 else "primary"
    )
])

st.markdown(metrics_html, unsafe_allow_html=True)

# ============================================
# RODÍZIO ATUAL + ALERTAS
# ============================================

col1, col2 = st.columns([3, 2])

with col1:
    rodizio = obter_rodizio_atual(calendario)
    
    if rodizio:
        inicio = datetime.strptime(rodizio["inicio"], "%Y-%m-%d")
        fim = datetime.strptime(rodizio["fim"], "%Y-%m-%d")
        hoje = datetime.now()
        
        progresso = max(0, min(1.0, (hoje - inicio).days / (fim - inicio).days))
        
        high_yield = pesos.get("temas_high_yield", {}).get(rodizio["grande_area_principal"], [])
        outros = rodizio.get("temas_prioritarios", [])
        outros_filtrados = [t for t in outros if t not in high_yield]
        
        st.markdown(
            render_rotation_card(
                nome=rodizio['rodizio'],
                periodo=f"{inicio.strftime('%d/%m/%Y')} - {fim.strftime('%d/%m/%Y')} • {(fim - inicio).days // 7} semanas",
                progresso=progresso,
                temas_hy=high_yield[:5],
                outros_temas=outros_filtrados
            ),
            unsafe_allow_html=True
        )
    else:
        st.markdown(render_no_rotation(), unsafe_allow_html=True)

with col2:
    alertas = obter_alertas()
    
    alertas_html = ""
    if alertas:
        for alerta in alertas[:4]:
            alertas_html += render_alert(
                titulo=alerta['tema'],
                descricao=f"Área: {alerta['area']}",
                tipo="danger" if "não revisado" in alerta.get('mensagem', '') else "warning",
                icon="🔴" if "não revisado" in alerta.get('mensagem', '') else "🟡"
            )
    else:
        alertas_html = '''
        <div style="text-align: center; padding: 2rem; color: #10b981;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
            <div>Todos os temas High-Yield prioritários estão em dia!</div>
        </div>
        '''
    
    st.markdown(
        render_section_card(
            titulo="Alertas High-Yield",
            icon="⚠️",
            conteudo=alertas_html,
            icon_color="warning"
        ),
        unsafe_allow_html=True
    )

# ============================================
# PLANO DA SEMANA
# ============================================

plano = obter_plano_semanal()

if plano["temas"]:
    # Construir tabela HTML
    table_rows = ""
    for t in plano["temas"][:7]:
        status_html = render_status_badge(t.get("status", "pendente"))
        hy_html = render_hy_badge() if t.get("is_high_yield") else ""
        
        table_rows += f'''
        <tr>
            <td>{status_html}</td>
            <td>{t['tema']} {hy_html}</td>
            <td>{t['grande_area']}</td>
            <td>{t['revisao']}ª Revisão</td>
            <td style="font-weight: 700; color: #3b82f6;">{t['questoes']}</td>
        </tr>
        '''
    
    table_html = f'''
    <table class="custom-table">
        <thead>
            <tr>
                <th>Status</th>
                <th>Tema</th>
                <th>Área</th>
                <th>Revisão</th>
                <th>Questões</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    '''
    
    # Resumo lateral
    summary_html = f'''
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        <div style="background: rgba(59, 130, 246, 0.1); padding: 1rem; border-radius: 12px; text-align: center;">
            <div style="font-size: 1.5rem; font-weight: 800; color: #3b82f6;">{plano['total_sugerido']}</div>
            <div style="font-size: 0.8rem; color: #94a3b8;">Sugerido</div>
        </div>
        <div style="background: rgba(16, 185, 129, 0.1); padding: 1rem; border-radius: 12px; text-align: center;">
            <div style="font-size: 1.5rem; font-weight: 800; color: #10b981;">{plano['meta_questoes']}</div>
            <div style="font-size: 0.8rem; color: #94a3b8;">Meta Semanal</div>
        </div>
    </div>
    '''
    
    st.markdown(
        render_section_card(
            titulo="Plano da Semana",
            icon="📋",
            conteudo=table_html + "<div style='margin-top: 1.5rem;'>" + summary_html + "</div>",
            icon_color="primary"
        ),
        unsafe_allow_html=True
    )
else:
    st.markdown(
        render_section_card(
            titulo="Plano da Semana",
            icon="📋",
            conteudo='''
            <div style="text-align: center; padding: 2rem; color: #64748b;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
                <div>Nenhuma tarefa pendente. Registre seus estudos na página de Estudo.</div>
            </div>
            ''',
            icon_color="primary"
        ),
        unsafe_allow_html=True
    )

# ============================================
# COBERTURA E PERFORMANCE
# ============================================

col1, col2 = st.columns(2)

with col1:
    cobertura = priorizador.calcular_cobertura_high_yield()
    
    progress_html = ""
    for area, dados in cobertura["por_area"].items():
        # Determinar cor baseada na porcentagem
        if dados["percentual"] >= 80:
            cor = "success"
        elif dados["percentual"] >= 50:
            cor = "warning"
        else:
            cor = "danger"
        
        progress_html += render_progress_bar(
            label=area,
            value=dados["revisados"],
            max_value=dados["total"],
            color=cor,
            show_percentage=True
        )
    
    st.markdown(
        render_section_card(
            titulo="Cobertura High-Yield por Área",
            icon="🔥",
            conteudo=progress_html,
            icon_color="warning"
        ),
        unsafe_allow_html=True
    )

with col2:
    registro = estudo.get("registro_temas", {})
    
    # Contar revisões
    total_temas = len(registro) if registro else 1
    r1_count = sum(1 for d in registro.values() if d.get("r1"))
    r2_count = sum(1 for d in registro.values() if d.get("r2"))
    r3_count = sum(1 for d in registro.values() if d.get("r3"))
    
    revision_html = f"""
    {render_progress_bar("1ª Revisão", r1_count, total_temas, "primary", False)}
    {render_progress_bar("2ª Revisão", r2_count, total_temas, "secondary", False)}
    {render_progress_bar("3ª Revisão", r3_count, total_temas, "success", False)}
    
    <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05);">
        {render_score_display(
            score=nota,
            label="Nota Estimada ENAMED",
            delta=delta_nota,
            meta=meta
        )}
    </div>
    """
    
    st.markdown(
        render_section_card(
            titulo="Progresso das Revisões",
            icon="📈",
            conteudo=revision_html,
            icon_color="success"
        ),
        unsafe_allow_html=True
    )

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    nome = config.get("usuario", {}).get("nome", "Estudante")
    ano = config.get("usuario", {}).get("ano_estudo", 1)
    
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); 
             border-radius: 50%; margin: 0 auto 1rem; display: flex; align-items: center; 
             justify-content: center; font-size: 1.5rem; font-weight: 700; color: white;">
            {nome[:2].upper() if nome else "US"}
        </div>
        <div style="font-weight: 700; color: #f8fafc; font-size: 1.1rem;">{nome}</div>
        <div style="color: #64748b; font-size: 0.85rem;">{ano}º Ano • ENAMED 2027</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Countdown
    st.markdown(render_countdown(dias), unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f"""
    <div style="font-size: 0.85rem; color: #94a3b8;">
        <div style="margin-bottom: 0.5rem;"><strong style="color: #f8fafc;">Banca:</strong> {config.get('metas', {}).get('banca_principal', 'ENAMED')}</div>
        <div style="margin-bottom: 0.5rem;"><strong style="color: #f8fafc;">Meta:</strong> {meta}%</div>
        <div><strong style="color: #f8fafc;">Modo:</strong> Focado no Resultado</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("##### 🔗 Navegação")
    st.page_link("pages/1_configuracoes.py", label="⚙️ Configurações")
    st.page_link("pages/2_calendario.py", label="📅 Calendário")
    st.page_link("pages/3_temas.py", label="📚 Temas")
    st.page_link("pages/4_estudo.py", label="📝 Registrar Estudo")
    st.page_link("pages/5_questoes.py", label="❓ Banco de Questões")
    st.page_link("pages/6_metricas.py", label="📊 Métricas")
    st.page_link("pages/7_revisao_final.py", label="🎯 Revisão Final")
    
    st.markdown("---")
    st.caption(f"Última atualização: {estudo.get('ultima_atualizacao', 'Nunca')[:10] if estudo.get('ultima_atualizacao') else 'Nunca'}")
