"""
Constantes globais da aplicação de estudos para residência médica.
"""

from datetime import timedelta

# Intervalos de revisão (Distributed Practice)
INTERVALOS_REVISAO = {
    "teoria_para_r1_inicio_ano": 21,  # dias
    "teoria_para_r1_fim_ano": 7,      # dias (diminui conforme aproxima da prova)
    "r1_para_r2": 30,                  # dias
    "r2_para_r3": 30,                  # dias
    "r3_para_final": 7,                # dias mínimos antes da prova
}

# Distribuição de questões por revisão
DISTRIBUICAO_REVISOES = {
    "primeira": 0.57,
    "segunda": 0.25,
    "terceira": 0.18
}

# Distribuição trimestral esperada
DISTRIBUICAO_TRIMESTRAL = {
    "jan_mar": 0.08,
    "abr_jun": 0.27,
    "jul_set": 0.28,
    "out_dez": 0.36
}

# Meta de questões
META_QUESTOES_2_ANOS = 33500
META_QUESTOES_SEMANA = 320

# Multiplicadores de prioridade
MULTIPLICADORES = {
    "high_yield": 1.5,
    "normal": 1.0,
    "low_yield": 0.5
}

# Bonus para temas do rodízio atual
BONUS_RODIZIO_ATUAL = 1.2

# Níveis de performance (setinhas)
NIVEIS_PERFORMANCE = {
    "muito_abaixo": {"min": 0, "max": 40, "icone": "⬇️⬇️", "cor": "#FF0000"},
    "abaixo": {"min": 40, "max": 55, "icone": "⬇️", "cor": "#FF6600"},
    "esperado": {"min": 55, "max": 70, "icone": "➡️", "cor": "#FFCC00"},
    "acima": {"min": 70, "max": 85, "icone": "⬆️", "cor": "#99CC00"},
    "muito_acima": {"min": 85, "max": 100, "icone": "⬆️⬆️", "cor": "#00CC00"}
}

# Cores para o degradê (25 tons do vermelho ao verde)
CORES_DEGRADÊ = [
    "#FF0000", "#FF1A00", "#FF3300", "#FF4D00", "#FF6600",
    "#FF8000", "#FF9900", "#FFB300", "#FFCC00", "#FFE600",
    "#FFFF00", "#E6FF00", "#CCFF00", "#B3FF00", "#99FF00",
    "#80FF00", "#66FF00", "#4DFF00", "#33FF00", "#1AFF00",
    "#00FF00", "#00E600", "#00CC00", "#00B300", "#009900"
]

# Níveis de prioridade (bolinhas)
NIVEIS_PRIORIDADE = {
    "vazia": "○",
    "quarto": "◔",
    "metade": "◑",
    "tres_quartos": "◕",
    "cheia": "●"
}

# Grandes áreas
GRANDES_AREAS = [
    "Clinica Medica",
    "Saude Coletiva",
    "Pediatria",
    "Ginecologia e Obstetricia",
    "Cirurgia Geral",
    "Saude Mental"
]

# Modos de estudo
MODOS_ESTUDO = {
    "focado_resultado": "Focado no Resultado",
    "focado_quantidade": "Focado na Quantidade"
}

# Margens de estudo
MARGENS_ESTUDO = {
    "reduzido": "Estudo Reduzido",
    "equilibrado": "Estudo Equilibrado",
    "rigoroso": "Estudo Rigoroso"
}

# Fator de ajuste por margem
FATOR_MARGEM = {
    "reduzido": 0.8,
    "equilibrado": 1.0,
    "rigoroso": 1.2
}

