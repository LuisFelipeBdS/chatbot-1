"""
Funções auxiliares para a aplicação de estudos.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Diretório de dados
DATA_DIR = Path(__file__).parent.parent / "data"


def carregar_json(nome_arquivo: str) -> Dict[str, Any]:
    """Carrega um arquivo JSON do diretório de dados."""
    caminho = DATA_DIR / nome_arquivo
    if caminho.exists():
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def salvar_json(nome_arquivo: str, dados: Dict[str, Any]) -> None:
    """Salva dados em um arquivo JSON no diretório de dados."""
    caminho = DATA_DIR / nome_arquivo
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_config() -> Dict[str, Any]:
    """Carrega as configurações do usuário."""
    return carregar_json("config.json")


def salvar_config(config: Dict[str, Any]) -> None:
    """Salva as configurações do usuário."""
    salvar_json("config.json", config)


def carregar_estudo() -> Dict[str, Any]:
    """Carrega o registro de estudos."""
    return carregar_json("estudo.json")


def salvar_estudo(estudo: Dict[str, Any]) -> None:
    """Salva o registro de estudos."""
    estudo["ultima_atualizacao"] = datetime.now().isoformat()
    salvar_json("estudo.json", estudo)


def carregar_temas() -> Dict[str, Any]:
    """Carrega a lista de temas."""
    return carregar_json("temas.json")


def carregar_pesos() -> Dict[str, Any]:
    """Carrega os pesos do ENAMED."""
    return carregar_json("pesos_enamed.json")


def carregar_calendario() -> Dict[str, Any]:
    """Carrega o calendário acadêmico."""
    return carregar_json("calendario.json")


def carregar_questoes() -> Dict[str, Any]:
    """Carrega o banco de questões."""
    return carregar_json("questoes.json")


def salvar_questoes(questoes: Dict[str, Any]) -> None:
    """Salva o banco de questões."""
    questoes["ultima_importacao"] = datetime.now().isoformat()
    salvar_json("questoes.json", questoes)


def calcular_dias_ate_prova(data_prova: str) -> int:
    """Calcula quantos dias faltam até a prova."""
    prova = datetime.strptime(data_prova, "%Y-%m-%d")
    hoje = datetime.now()
    return (prova - hoje).days


def calcular_semanas_ate_prova(data_prova: str) -> int:
    """Calcula quantas semanas faltam até a prova."""
    dias = calcular_dias_ate_prova(data_prova)
    return max(1, dias // 7)


def obter_rodizio_atual(calendario: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Retorna o rodízio atual baseado na data."""
    hoje = datetime.now().date()
    
    for ano, rodizios in calendario.items():
        if isinstance(rodizios, dict):
            for ano_num, lista_rodizios in rodizios.items():
                for rodizio in lista_rodizios:
                    inicio = datetime.strptime(rodizio["inicio"], "%Y-%m-%d").date()
                    fim = datetime.strptime(rodizio["fim"], "%Y-%m-%d").date()
                    if inicio <= hoje <= fim:
                        return rodizio
    return None


def calcular_porcentagem_acerto(acertos: int, total: int) -> float:
    """Calcula a porcentagem de acerto."""
    if total == 0:
        return 0.0
    return round((acertos / total) * 100, 1)


def obter_cor_performance(porcentagem: float) -> str:
    """Retorna a cor baseada na porcentagem de acerto."""
    from .constants import CORES_DEGRADÊ
    
    # Mapear 0-100% para índice 0-24
    indice = int(min(24, max(0, porcentagem / 100 * 24)))
    return CORES_DEGRADÊ[indice]


def obter_nivel_performance(porcentagem: float) -> Dict[str, Any]:
    """Retorna o nível de performance baseado na porcentagem."""
    from .constants import NIVEIS_PERFORMANCE
    
    for nivel, dados in NIVEIS_PERFORMANCE.items():
        if dados["min"] <= porcentagem < dados["max"]:
            return {"nivel": nivel, **dados}
    
    # Se for 100%, retorna muito_acima
    return {"nivel": "muito_acima", **NIVEIS_PERFORMANCE["muito_acima"]}


def obter_prioridade_bolinha(score: float) -> str:
    """Retorna o símbolo de bolinha baseado no score de prioridade (0-1)."""
    from .constants import NIVEIS_PRIORIDADE
    
    if score < 0.2:
        return NIVEIS_PRIORIDADE["vazia"]
    elif score < 0.4:
        return NIVEIS_PRIORIDADE["quarto"]
    elif score < 0.6:
        return NIVEIS_PRIORIDADE["metade"]
    elif score < 0.8:
        return NIVEIS_PRIORIDADE["tres_quartos"]
    else:
        return NIVEIS_PRIORIDADE["cheia"]


def formatar_data(data_str: str) -> str:
    """Formata uma data ISO para formato brasileiro."""
    data = datetime.strptime(data_str, "%Y-%m-%d")
    return data.strftime("%d/%m/%Y")


def parse_data_br(data_str: str) -> datetime:
    """Parse de data no formato brasileiro."""
    return datetime.strptime(data_str, "%d/%m/%Y")


def is_configurado() -> bool:
    """Verifica se o sistema já foi configurado."""
    config = carregar_config()
    return config.get("configurado", False)

