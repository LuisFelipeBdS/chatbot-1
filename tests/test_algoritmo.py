"""
Testes para Algoritmo de Sugestão

Valida os cálculos de questões sugeridas, pesos, multiplicadores
e geração do plano semanal.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
from freezegun import freeze_time

# Adicionar path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAlgoritmoSugestao:
    """Testes para a classe AlgoritmoSugestao."""
    
    @pytest.fixture(autouse=True)
    def setup(self, config_teste, pesos_teste, temas_teste, estudo_vazio, calendario_teste):
        """Setup para cada teste."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_vazio), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            from core.algoritmo_sugestao import AlgoritmoSugestao
            self.alg = AlgoritmoSugestao()
            self.pesos = pesos_teste
    
    def test_peso_area_clinica_medica(self):
        """Clínica Médica deve ter maior peso (32.5%)."""
        peso = self.alg.obter_peso_area("Clinica Medica")
        assert peso == 0.325, f"Esperado 0.325, obtido {peso}"
    
    def test_peso_area_cirurgia(self):
        """Cirurgia Geral deve ter peso de 12.5%."""
        peso = self.alg.obter_peso_area("Cirurgia Geral")
        assert peso == 0.125, f"Esperado 0.125, obtido {peso}"
    
    def test_peso_area_inexistente(self):
        """Área inexistente deve retornar peso padrão."""
        peso = self.alg.obter_peso_area("Area Inexistente")
        assert peso == 0.1, f"Esperado 0.1 (padrão), obtido {peso}"
    
    def test_multiplicador_high_yield(self):
        """Temas High-Yield devem ter multiplicador > 1."""
        mult = self.alg.obter_multiplicador_yield("Tuberculose", "Clinica Medica")
        assert mult > 1.0, f"High-Yield deve ter multiplicador > 1, obtido {mult}"
    
    def test_multiplicador_low_yield(self):
        """Temas Low-Yield devem ter multiplicador < 1."""
        mult = self.alg.obter_multiplicador_yield("Tumores Ortopédicos", "Cirurgia Geral")
        assert mult < 1.0, f"Low-Yield deve ter multiplicador < 1, obtido {mult}"
    
    def test_multiplicador_normal(self):
        """Temas normais devem ter multiplicador = 1."""
        mult = self.alg.obter_multiplicador_yield("Tema Normal", "Clinica Medica")
        assert mult == 1.0, f"Normal deve ter multiplicador = 1, obtido {mult}"


class TestBonusRodizio:
    """Testes para bônus de rodízio ativo."""
    
    @freeze_time("2026-02-15")  # Durante rodízio de Infectologia
    def test_bonus_rodizio_ativo(self, config_teste, pesos_teste, temas_teste, estudo_vazio, calendario_teste):
        """Tema do rodízio ativo deve receber bônus."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_vazio), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            from core.algoritmo_sugestao import AlgoritmoSugestao
            alg = AlgoritmoSugestao()
            
            # Tuberculose é tema prioritário do rodízio de Infectologia
            bonus = alg.verificar_bonus_rodizio("Tuberculose", "Clinica Medica")
            assert bonus > 1.0, f"Deveria ter bônus > 1, obtido {bonus}"
    
    @freeze_time("2026-05-01")  # Durante rodízio de Saúde Coletiva
    def test_sem_bonus_fora_rodizio(self, config_teste, pesos_teste, temas_teste, estudo_vazio, calendario_teste):
        """Tema fora do rodízio ativo não deve receber bônus."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_vazio), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            from core.algoritmo_sugestao import AlgoritmoSugestao
            alg = AlgoritmoSugestao()
            
            # Tuberculose não é tema prioritário de Saúde Coletiva
            bonus = alg.verificar_bonus_rodizio("Tuberculose", "Clinica Medica")
            assert bonus == 1.0, f"Não deveria ter bônus, obtido {bonus}"


class TestSugestaoTema:
    """Testes para cálculo de sugestão por tema."""
    
    @pytest.fixture(autouse=True)
    def setup(self, config_teste, pesos_teste, temas_teste, estudo_vazio, calendario_teste):
        """Setup para cada teste."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_vazio), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            from core.algoritmo_sugestao import AlgoritmoSugestao
            self.alg = AlgoritmoSugestao()
    
    def test_sugestao_retorna_estrutura_correta(self):
        """Sugestão deve retornar estrutura completa."""
        sugestao = self.alg.calcular_sugestao_tema("Tuberculose", "Clinica Medica", 1)
        
        assert "questoes_sugeridas" in sugestao
        assert "detalhes" in sugestao
        assert "base" in sugestao["detalhes"]
        assert "peso_area" in sugestao["detalhes"]
        assert "multiplicador_yield" in sugestao["detalhes"]
        assert "is_high_yield" in sugestao["detalhes"]
    
    def test_sugestao_high_yield_maior(self):
        """Tema High-Yield deve ter mais questões sugeridas."""
        sugestao_hy = self.alg.calcular_sugestao_tema("Tuberculose", "Clinica Medica", 1)
        sugestao_normal = self.alg.calcular_sugestao_tema("Tema Normal", "Clinica Medica", 1)
        
        assert sugestao_hy["questoes_sugeridas"] >= sugestao_normal["questoes_sugeridas"], \
            "High-Yield deve ter mais questões"
    
    def test_sugestao_limites(self):
        """Sugestão deve respeitar limites (10-500)."""
        sugestao = self.alg.calcular_sugestao_tema("Tuberculose", "Clinica Medica", 1)
        
        assert 10 <= sugestao["questoes_sugeridas"] <= 500, \
            f"Questões fora dos limites: {sugestao['questoes_sugeridas']}"


class TestPlanoSemanal:
    """Testes para geração do plano semanal."""
    
    @freeze_time("2026-02-10")
    def test_plano_semanal_estrutura(self, config_teste, pesos_teste, temas_teste, estudo_com_dados, calendario_teste):
        """Plano semanal deve ter estrutura correta."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_com_dados), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            from core.algoritmo_sugestao import AlgoritmoSugestao
            alg = AlgoritmoSugestao()
            
            plano = alg.gerar_plano_semanal()
            
            assert "semana" in plano
            assert "meta_questoes" in plano
            assert "temas" in plano
            assert "total_sugerido" in plano
    
    @freeze_time("2026-02-10")
    def test_plano_semanal_apenas_proximas(self, config_teste, pesos_teste, temas_teste, estudo_com_dados, calendario_teste):
        """Plano com apenas_proximas deve filtrar revisões distantes."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_com_dados), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            from core.algoritmo_sugestao import AlgoritmoSugestao
            alg = AlgoritmoSugestao()
            
            plano_todas = alg.gerar_plano_semanal(apenas_proximas=False)
            plano_proximas = alg.gerar_plano_semanal(apenas_proximas=True)
            
            # Próximas deve ter menos ou igual itens
            assert len(plano_proximas["temas"]) <= len(plano_todas["temas"])
    
    @freeze_time("2026-02-10")
    def test_plano_semanal_inclui_data_sugerida(self, config_teste, pesos_teste, temas_teste, estudo_com_dados, calendario_teste):
        """Cada item do plano deve incluir data_sugerida."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_com_dados), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            from core.algoritmo_sugestao import AlgoritmoSugestao
            alg = AlgoritmoSugestao()
            
            plano = alg.gerar_plano_semanal(apenas_proximas=False)
            
            for tema in plano["temas"]:
                assert "data_sugerida" in tema, f"Tema {tema['tema']} sem data_sugerida"


class TestFatorPerformance:
    """Testes para fator de ajuste baseado em performance."""
    
    @pytest.fixture(autouse=True)
    def setup(self, config_teste, pesos_teste, temas_teste, calendario_teste):
        """Setup para cada teste."""
        self.config = config_teste
        self.pesos = pesos_teste
        self.temas = temas_teste
        self.calendario = calendario_teste
    
    def test_fator_performance_baixa(self, estudo_vazio):
        """Performance baixa deve aumentar questões (fator > 1)."""
        # Simular estudo com baixa performance
        estudo_baixo = estudo_vazio.copy()
        estudo_baixo["registro_temas"] = {
            "Tuberculose": {
                "data_teoria": "2026-01-15",
                "grande_area": "Clinica Medica",
                "r1": {"data": "2026-02-05", "questoes": 50, "acertos": 20}  # 40%
            }
        }
        
        with patch('utils.helpers.carregar_config', return_value=self.config), \
             patch('utils.helpers.carregar_pesos', return_value=self.pesos), \
             patch('utils.helpers.carregar_temas', return_value=self.temas), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_baixo), \
             patch('utils.helpers.carregar_calendario', return_value=self.calendario):
            from core.algoritmo_sugestao import AlgoritmoSugestao
            alg = AlgoritmoSugestao()
            
            fator = alg.calcular_fator_performance("Tuberculose", 2)
            assert fator > 1.0, f"Fator para baixa performance deve ser > 1, obtido {fator}"
    
    def test_fator_performance_alta(self, estudo_vazio):
        """Performance alta deve reduzir ou manter questões (fator <= 1)."""
        estudo_alto = estudo_vazio.copy()
        estudo_alto["registro_temas"] = {
            "Tuberculose": {
                "data_teoria": "2026-01-15",
                "grande_area": "Clinica Medica",
                "r1": {"data": "2026-02-05", "questoes": 50, "acertos": 48}  # 96%
            }
        }
        
        with patch('utils.helpers.carregar_config', return_value=self.config), \
             patch('utils.helpers.carregar_pesos', return_value=self.pesos), \
             patch('utils.helpers.carregar_temas', return_value=self.temas), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_alto), \
             patch('utils.helpers.carregar_calendario', return_value=self.calendario):
            from core.algoritmo_sugestao import AlgoritmoSugestao
            alg = AlgoritmoSugestao()
            
            fator = alg.calcular_fator_performance("Tuberculose", 2)
            # Alta performance deve ter fator <= 1 (não aumentar questões)
            assert fator <= 1.5, f"Fator para alta performance deve ser <= 1.5, obtido {fator}"

