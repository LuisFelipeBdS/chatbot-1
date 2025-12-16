"""
Estilos e Componentes Visuais Customizados

Módulo com CSS extensivo e funções para criar componentes visuais
bonitos no Streamlit, aproximando do mockup HTML.
"""

# CSS Global - Injetar em todas as páginas
GLOBAL_CSS = """
<style>
    /* ===== IMPORTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* ===== VARIÁVEIS ===== */
    :root {
        --primary: #3b82f6;
        --primary-dark: #2563eb;
        --secondary: #0ea5e9;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --dark: #0f172a;
        --dark-soft: #1e293b;
        --gray-700: #334155;
        --gray-600: #475569;
        --gray-500: #64748b;
        --gray-400: #94a3b8;
        --gray-300: #cbd5e1;
        --white: #f8fafc;
    }
    
    /* ===== BASE ===== */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ===== HEADER ===== */
    .main-title {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
        letter-spacing: -0.5px;
    }
    
    .main-subtitle {
        font-size: 0.95rem;
        color: var(--gray-400);
        margin-bottom: 1.5rem;
    }
    
    /* ===== METRIC CARDS ===== */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, var(--dark-soft) 0%, #1a2744 100%);
        border-radius: 16px;
        padding: 1.25rem;
        border: 1px solid rgba(255,255,255,0.05);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-radius: 16px 16px 0 0;
    }
    
    .metric-card.primary::before { background: linear-gradient(90deg, #3b82f6, #8b5cf6); }
    .metric-card.success::before { background: linear-gradient(90deg, #10b981, #059669); }
    .metric-card.warning::before { background: linear-gradient(90deg, #f59e0b, #d97706); }
    .metric-card.danger::before { background: linear-gradient(90deg, #ef4444, #dc2626); }
    
    .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: var(--gray-400);
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: var(--white);
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-delta {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
    }
    
    .metric-delta.positive {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
    }
    
    .metric-delta.negative {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
    }
    
    .metric-delta.neutral {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
    }
    
    .metric-footer {
        margin-top: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px solid rgba(255,255,255,0.05);
        font-size: 0.75rem;
        color: var(--gray-500);
    }
    
    /* ===== SECTION CARDS ===== */
    .section-card {
        background: var(--dark-soft);
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.05);
        overflow: hidden;
        margin-bottom: 1.5rem;
    }
    
    .section-header {
        padding: 1rem 1.25rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    
    .section-icon.primary { background: rgba(59, 130, 246, 0.15); }
    .section-icon.success { background: rgba(16, 185, 129, 0.15); }
    .section-icon.warning { background: rgba(245, 158, 11, 0.15); }
    .section-icon.danger { background: rgba(239, 68, 68, 0.15); }
    
    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--white);
    }
    
    .section-body {
        padding: 1.25rem;
    }
    
    /* ===== ROTATION CARD ===== */
    .rotation-card {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        margin-bottom: 1.5rem;
    }
    
    .rotation-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.2);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    
    .rotation-title {
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .rotation-period {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 1.25rem;
    }
    
    .rotation-progress-container {
        margin-bottom: 1.25rem;
    }
    
    .rotation-progress-header {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    
    .rotation-progress-bar {
        height: 8px;
        background: rgba(255,255,255,0.2);
        border-radius: 4px;
        overflow: hidden;
    }
    
    .rotation-progress-fill {
        height: 100%;
        background: white;
        border-radius: 4px;
    }
    
    .rotation-topics-title {
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        opacity: 0.9;
    }
    
    .topic-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    .topic-tag {
        background: rgba(255,255,255,0.15);
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .topic-tag.high-yield {
        background: rgba(251, 191, 36, 0.3);
        border: 1px solid rgba(251, 191, 36, 0.5);
    }
    
    /* ===== ALERTS ===== */
    .alert-item {
        display: flex;
        gap: 12px;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        border-left: 4px solid;
    }
    
    .alert-item.warning {
        background: rgba(245, 158, 11, 0.1);
        border-left-color: #f59e0b;
    }
    
    .alert-item.danger {
        background: rgba(239, 68, 68, 0.1);
        border-left-color: #ef4444;
    }
    
    .alert-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    
    .alert-item.warning .alert-icon { background: rgba(245, 158, 11, 0.2); }
    .alert-item.danger .alert-icon { background: rgba(239, 68, 68, 0.2); }
    
    .alert-content h4 {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--white);
        margin-bottom: 2px;
    }
    
    .alert-content p {
        font-size: 0.8rem;
        color: var(--gray-400);
        margin: 0;
    }
    
    /* ===== STATUS BADGES ===== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-badge.overdue {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
    }
    
    .status-badge.available {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
    }
    
    .status-badge.pending {
        background: rgba(59, 130, 246, 0.15);
        color: #3b82f6;
    }
    
    .status-badge.done {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
    }
    
    /* ===== HIGH-YIELD BADGE ===== */
    .hy-badge {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* ===== PROGRESS BARS ===== */
    .custom-progress {
        margin-bottom: 1rem;
    }
    
    .custom-progress-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
    }
    
    .custom-progress-label {
        font-size: 0.85rem;
        color: var(--gray-300);
        font-weight: 500;
    }
    
    .custom-progress-value {
        font-size: 0.85rem;
        color: var(--gray-400);
        font-weight: 600;
    }
    
    .custom-progress-bar {
        height: 10px;
        background: rgba(255,255,255,0.1);
        border-radius: 5px;
        overflow: hidden;
    }
    
    .custom-progress-fill {
        height: 100%;
        border-radius: 5px;
        transition: width 0.5s ease;
    }
    
    .custom-progress-fill.primary { background: linear-gradient(90deg, #3b82f6, #8b5cf6); }
    .custom-progress-fill.success { background: linear-gradient(90deg, #10b981, #059669); }
    .custom-progress-fill.warning { background: linear-gradient(90deg, #f59e0b, #d97706); }
    .custom-progress-fill.danger { background: linear-gradient(90deg, #ef4444, #dc2626); }
    .custom-progress-fill.secondary { background: linear-gradient(90deg, #0ea5e9, #0284c7); }
    
    /* ===== TABLES ===== */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .custom-table th {
        text-align: left;
        padding: 12px 16px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--gray-400);
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .custom-table td {
        padding: 14px 16px;
        font-size: 0.9rem;
        color: var(--gray-300);
        border-bottom: 1px solid rgba(255,255,255,0.03);
    }
    
    .custom-table tr:hover td {
        background: rgba(255,255,255,0.02);
    }
    
    /* ===== COUNTDOWN ===== */
    .countdown-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.15) 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        display: inline-flex;
        align-items: center;
        gap: 1rem;
    }
    
    .countdown-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #f59e0b;
        line-height: 1;
    }
    
    .countdown-label {
        font-size: 0.85rem;
        color: var(--gray-300);
        line-height: 1.3;
    }
    
    /* ===== SCORE DISPLAY ===== */
    .score-display {
        text-align: center;
        padding: 2rem;
    }
    
    .score-value {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .score-label {
        font-size: 1rem;
        color: var(--gray-400);
        margin-bottom: 1rem;
    }
    
    .score-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        font-size: 1.1rem;
    }
    
    .score-indicator.positive { color: #10b981; }
    .score-indicator.negative { color: #ef4444; }
    
    /* ===== SIDEBAR ENHANCEMENTS ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--white) !important;
    }
    
    /* ===== DATAFRAME STYLING ===== */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: var(--dark-soft) !important;
        border-radius: 10px !important;
    }
    
    /* ===== DIVIDER ===== */
    hr {
        border: none;
        height: 1px;
        background: rgba(255,255,255,0.05);
        margin: 1.5rem 0;
    }
    
    /* ===== HIDE STREAMLIT ELEMENTS ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""


def inject_css():
    """Injeta o CSS global na página."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_main_header(titulo: str, subtitulo: str = ""):
    """Renderiza o cabeçalho principal da página."""
    html = f'''
    <div class="main-title">{titulo}</div>
    <div class="main-subtitle">{subtitulo}</div>
    '''
    return html


def render_metric_card(
    icon: str,
    label: str,
    value: str,
    delta: str = "",
    delta_type: str = "neutral",  # positive, negative, neutral
    footer: str = "",
    color: str = "primary"  # primary, success, warning, danger
) -> str:
    """Renderiza um card de métrica estilizado."""
    
    delta_html = ""
    if delta:
        delta_html = f'<div class="metric-delta {delta_type}">{delta}</div>'
    
    footer_html = ""
    if footer:
        footer_html = f'<div class="metric-footer">{footer}</div>'
    
    return f'''
    <div class="metric-card {color}">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
        {footer_html}
    </div>
    '''


def render_metrics_row(metrics: list) -> str:
    """Renderiza uma linha de cards de métricas."""
    cards_html = "".join(metrics)
    return f'<div class="metric-container">{cards_html}</div>'


def render_rotation_card(
    nome: str,
    periodo: str,
    progresso: float,
    temas_hy: list,
    outros_temas: list = None
) -> str:
    """Renderiza o card de rodízio atual."""
    
    temas_html = ""
    for tema in temas_hy:
        temas_html += f'<span class="topic-tag high-yield">🔥 {tema}</span>'
    
    if outros_temas:
        for tema in outros_temas[:3]:
            temas_html += f'<span class="topic-tag">{tema}</span>'
    
    progresso_pct = int(progresso * 100)
    
    return f'''
    <div class="rotation-card">
        <div class="rotation-badge">🏥 RODÍZIO ATUAL</div>
        <div class="rotation-title">{nome}</div>
        <div class="rotation-period">{periodo}</div>
        
        <div class="rotation-progress-container">
            <div class="rotation-progress-header">
                <span>Progresso</span>
                <span>{progresso_pct}%</span>
            </div>
            <div class="rotation-progress-bar">
                <div class="rotation-progress-fill" style="width: {progresso_pct}%"></div>
            </div>
        </div>
        
        <div class="rotation-topics-title">🔥 Temas High-Yield do Rodízio</div>
        <div class="topic-tags">
            {temas_html}
        </div>
    </div>
    '''


def render_no_rotation() -> str:
    """Renderiza mensagem quando não há rodízio ativo."""
    return '''
    <div class="section-card">
        <div class="section-body" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📅</div>
            <div style="color: var(--gray-400);">Nenhum rodízio ativo no momento.</div>
        </div>
    </div>
    '''


def render_alert(
    titulo: str,
    descricao: str,
    tipo: str = "warning",  # warning, danger
    icon: str = "⚠️"
) -> str:
    """Renderiza um item de alerta."""
    return f'''
    <div class="alert-item {tipo}">
        <div class="alert-icon">{icon}</div>
        <div class="alert-content">
            <h4>{titulo}</h4>
            <p>{descricao}</p>
        </div>
    </div>
    '''


def render_section_card(
    titulo: str,
    icon: str,
    conteudo: str,
    icon_color: str = "primary"
) -> str:
    """Renderiza um card de seção."""
    return f'''
    <div class="section-card">
        <div class="section-header">
            <div class="section-icon {icon_color}">{icon}</div>
            <div class="section-title">{titulo}</div>
        </div>
        <div class="section-body">
            {conteudo}
        </div>
    </div>
    '''


def render_progress_bar(
    label: str,
    value: float,
    max_value: float = 100,
    color: str = "primary",
    show_percentage: bool = True
) -> str:
    """Renderiza uma barra de progresso customizada."""
    
    percentage = (value / max_value * 100) if max_value > 0 else 0
    
    value_text = f"{percentage:.0f}%" if show_percentage else f"{value}/{max_value}"
    
    return f'''
    <div class="custom-progress">
        <div class="custom-progress-header">
            <span class="custom-progress-label">{label}</span>
            <span class="custom-progress-value">{value_text}</span>
        </div>
        <div class="custom-progress-bar">
            <div class="custom-progress-fill {color}" style="width: {percentage}%"></div>
        </div>
    </div>
    '''


def render_countdown(dias: int) -> str:
    """Renderiza o box de contagem regressiva."""
    semanas = dias // 7
    return f'''
    <div class="countdown-box">
        <div class="countdown-number">{dias}</div>
        <div class="countdown-label">dias até<br>a prova</div>
    </div>
    '''


def render_score_display(
    score: float,
    label: str = "Nota Estimada",
    delta: float = None,
    meta: float = None
) -> str:
    """Renderiza display de nota/score."""
    
    indicator_html = ""
    if delta is not None:
        if delta >= 0:
            indicator_html = f'<div class="score-indicator positive">⬆️ +{delta:.1f} acima da meta</div>'
        else:
            indicator_html = f'<div class="score-indicator negative">⬇️ {delta:.1f} abaixo da meta</div>'
    
    return f'''
    <div class="score-display">
        <div class="score-value">{score:.1f}%</div>
        <div class="score-label">{label}</div>
        {indicator_html}
    </div>
    '''


def render_status_badge(status: str) -> str:
    """Renderiza badge de status."""
    configs = {
        "atrasada": ("🔴 Atrasado", "overdue"),
        "disponivel": ("🟡 Disponível", "available"),
        "pendente": ("🔵 Pendente", "pending"),
        "concluida": ("✅ Concluído", "done")
    }
    
    texto, classe = configs.get(status, ("⚪ -", "pending"))
    return f'<span class="status-badge {classe}">{texto}</span>'


def render_hy_badge() -> str:
    """Renderiza badge High-Yield."""
    return '<span class="hy-badge">HIGH-YIELD</span>'

