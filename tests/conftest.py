"""
Configuração e Fixtures para Testes

Fixtures compartilhadas entre todos os testes.
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Adicionar o diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Diretório de fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def config_teste():
    """Configuração de teste com data de prova fixa."""
    return {
        "usuario": {
            "nome": "Estudante Teste",
            "ano_estudo": 1,
            "data_prova_estimada": "2027-11-15"
        },
        "metas": {
            "nota_meta": 90,
            "questoes_semana_meta": 320,
            "banca_principal": "ENAMED"
        },
        "modo_estudo": {
            "tipo": "focado_resultado",
            "margem": "equilibrado"
        },
        "diagnostico_inicial": {
            "clinica_medica": 60,
            "saude_coletiva": 70,
            "pediatria": 65,
            "ginecologia_obstetricia": 50,
            "cirurgia_geral": 55,
            "saude_mental": 60
        },
        "rotina": {
            "dias_disponiveis": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"],
            "horas_por_dia": 3,
            "horario_preferido": "Noite",
            "questoes_por_hora": 15
        }
    }


@pytest.fixture
def estudo_vazio():
    """Registro de estudo vazio."""
    return {
        "registro_temas": {},
        "questoes_marcadas_importantes": [],
        "estatisticas_gerais": {
            "total_questoes_feitas": 0,
            "total_acertos": 0,
            "simulados_realizados": 0
        },
        "ultima_atualizacao": None
    }


@pytest.fixture
def estudo_com_dados():
    """Registro de estudo com dados de teste."""
    with open(FIXTURES_DIR / "estudo_teste.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def questoes_teste():
    """Questões de teste."""
    with open(FIXTURES_DIR / "questoes_teste.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def pesos_teste():
    """Pesos ENAMED para teste."""
    return {
        "pesos_areas": {
            "Clinica Medica": 0.325,
            "Saude Coletiva": 0.225,
            "Pediatria": 0.175,
            "Ginecologia e Obstetricia": 0.175,
            "Cirurgia Geral": 0.125,
            "Saude Mental": 0.075
        },
        "temas_high_yield": {
            "Clinica Medica": ["Tuberculose", "HIV e AIDS", "Diabetes", "Hipertensão"],
            "Cirurgia Geral": ["ABCDE do Trauma", "Abdome Agudo Inflamatório"],
            "Pediatria": ["Imunizações", "Sala de Parto"],
            "Ginecologia e Obstetricia": ["Pré-natal", "Síndromes Hipertensivas"]
        },
        "temas_low_yield": ["Tumores Ortopédicos", "Medicina Fetal"]
    }


@pytest.fixture
def temas_teste():
    """Temas de teste simplificados."""
    return {
        "grandes_areas": {
            "Clinica Medica": {
                "temas": [
                    {"nome": "Tuberculose", "high_yield": True},
                    {"nome": "HIV e AIDS", "high_yield": True},
                    {"nome": "Diabetes", "high_yield": True}
                ]
            },
            "Cirurgia Geral": {
                "temas": [
                    {"nome": "ABCDE do Trauma", "high_yield": True},
                    {"nome": "Hérnias", "high_yield": True}
                ]
            },
            "Pediatria": {
                "temas": [
                    {"nome": "Imunizações", "high_yield": True},
                    {"nome": "Sala de Parto", "high_yield": True}
                ]
            },
            "Ginecologia e Obstetricia": {
                "temas": [
                    {"nome": "Pré-natal", "high_yield": True},
                    {"nome": "Síndromes Hipertensivas", "high_yield": True}
                ]
            }
        }
    }


@pytest.fixture
def calendario_teste():
    """Calendário de rodízios de teste."""
    return {
        "ano_1": {
            "2026": [
                {
                    "rodizio": "Infectologia",
                    "inicio": "2026-02-09",
                    "fim": "2026-03-29",
                    "temas_prioritarios": ["Tuberculose", "HIV e AIDS"],
                    "grande_area_principal": "Clinica Medica"
                },
                {
                    "rodizio": "Saúde Coletiva",
                    "inicio": "2026-03-30",
                    "fim": "2026-05-17",
                    "temas_prioritarios": ["Princípios do SUS", "Ética Médica"],
                    "grande_area_principal": "Saude Coletiva"
                }
            ]
        }
    }


@pytest.fixture
def data_inicio_ano():
    """Data de início do ano de estudos."""
    return datetime(2026, 1, 15)


@pytest.fixture
def data_meio_ano():
    """Data no meio do ano de estudos."""
    return datetime(2026, 6, 15)


@pytest.fixture
def data_proximo_prova():
    """Data próxima à prova (60 dias antes)."""
    return datetime(2027, 9, 15)


@pytest.fixture
def mock_carregar_config(config_teste):
    """Mock para carregar_config."""
    with patch('utils.helpers.carregar_config', return_value=config_teste):
        yield config_teste


@pytest.fixture
def mock_carregar_estudo(estudo_com_dados):
    """Mock para carregar_estudo."""
    with patch('utils.helpers.carregar_estudo', return_value=estudo_com_dados):
        yield estudo_com_dados


@pytest.fixture
def mock_carregar_pesos(pesos_teste):
    """Mock para carregar_pesos."""
    with patch('utils.helpers.carregar_pesos', return_value=pesos_teste):
        yield pesos_teste


@pytest.fixture
def mock_carregar_temas(temas_teste):
    """Mock para carregar_temas."""
    with patch('utils.helpers.carregar_temas', return_value=temas_teste):
        yield temas_teste


@pytest.fixture
def mock_all_data(config_teste, estudo_com_dados, pesos_teste, temas_teste, calendario_teste):
    """Mock para todos os dados de uma vez."""
    with patch('utils.helpers.carregar_config', return_value=config_teste), \
         patch('utils.helpers.carregar_estudo', return_value=estudo_com_dados), \
         patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
         patch('utils.helpers.carregar_temas', return_value=temas_teste), \
         patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
        yield {
            "config": config_teste,
            "estudo": estudo_com_dados,
            "pesos": pesos_teste,
            "temas": temas_teste,
            "calendario": calendario_teste
        }

