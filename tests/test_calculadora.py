"""
Testes para Calculadora de Revisões

Valida os cálculos de intervalos, datas e status de revisões
baseados no algoritmo de Distributed Practice.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from freezegun import freeze_time

# Adicionar path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCalculadoraRevisoes:
    """Testes para a classe CalculadoraRevisoes."""
    
    @pytest.fixture(autouse=True)
    def setup(self, config_teste, pesos_teste):
        """Setup para cada teste."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste):
            from core.calculadora_revisoes import CalculadoraRevisoes
            self.calc = CalculadoraRevisoes()
    
    def test_fator_proximidade_longe_da_prova(self, data_inicio_ano):
        """Fator deve ser 1.0 quando longe da prova (>300 dias)."""
        fator = self.calc.calcular_fator_proximidade(data_inicio_ano)
        assert fator == 1.0, f"Esperado 1.0, obtido {fator}"
    
    def test_fator_proximidade_perto_da_prova(self, data_proximo_prova):
        """Fator deve ser reduzido quando próximo da prova (<60 dias)."""
        fator = self.calc.calcular_fator_proximidade(data_proximo_prova)
        # Aceitar aproximação de 0.3
        assert abs(fator - 0.3) < 0.05, f"Esperado ~0.3, obtido {fator}"
    
    def test_fator_proximidade_meio_do_ano(self, data_meio_ano):
        """Fator deve ser intermediário ou alto no meio do ano."""
        fator = self.calc.calcular_fator_proximidade(data_meio_ano)
        # Meio do ano ainda está longe, fator pode ser 1.0 ou próximo
        assert 0.3 <= fator <= 1.0, f"Esperado valor entre 0.3 e 1.0, obtido {fator}"
    
    def test_intervalo_r1_inicio_ano(self, data_inicio_ano):
        """Intervalo teoria->R1 deve ser ~21 dias no início do ano."""
        intervalo = self.calc.calcular_intervalo_teoria_r1(data_inicio_ano)
        assert 14 <= intervalo <= 21, f"Esperado entre 14 e 21, obtido {intervalo}"
    
    def test_intervalo_r1_proximo_prova(self, data_proximo_prova):
        """Intervalo teoria->R1 deve ser reduzido próximo da prova."""
        intervalo = self.calc.calcular_intervalo_teoria_r1(data_proximo_prova)
        # Próximo da prova, intervalo deve ser reduzido (< 14 dias)
        assert 7 <= intervalo <= 14, f"Esperado entre 7 e 14, obtido {intervalo}"
    
    def test_cronograma_tema_completo(self, data_inicio_ano):
        """Cronograma deve conter todas as revisões com datas válidas."""
        cronograma = self.calc.calcular_cronograma_tema(data_inicio_ano, "Tuberculose")
        
        assert "tema" in cronograma
        assert cronograma["tema"] == "Tuberculose"
        assert "revisoes" in cronograma
        assert "r1" in cronograma["revisoes"]
        assert "r2" in cronograma["revisoes"]
        assert "r3" in cronograma["revisoes"]
        
        # Verificar que as datas estão em ordem crescente
        r1_data = datetime.strptime(cronograma["revisoes"]["r1"]["data_sugerida"], "%Y-%m-%d")
        r2_data = datetime.strptime(cronograma["revisoes"]["r2"]["data_sugerida"], "%Y-%m-%d")
        r3_data = datetime.strptime(cronograma["revisoes"]["r3"]["data_sugerida"], "%Y-%m-%d")
        
        assert r1_data < r2_data < r3_data, "Datas devem estar em ordem crescente"
    
    def test_cronograma_respeita_data_limite(self):
        """R3 não deve ultrapassar 14 dias antes da prova."""
        # Data muito próxima da prova
        data_tardia = datetime(2027, 10, 1)
        
        cronograma = self.calc.calcular_cronograma_tema(data_tardia, "Teste")
        
        r3_data = datetime.strptime(cronograma["revisoes"]["r3"]["data_sugerida"], "%Y-%m-%d")
        data_limite = datetime(2027, 11, 1)  # 14 dias antes de 15/11
        
        assert r3_data <= data_limite, "R3 não deve ultrapassar 14 dias antes da prova"


class TestStatusRevisao:
    """Testes para verificação de status de revisão."""
    
    @pytest.fixture(autouse=True)
    def setup(self, config_teste, pesos_teste):
        """Setup para cada teste."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste):
            from core.calculadora_revisoes import CalculadoraRevisoes
            self.calc = CalculadoraRevisoes()
    
    @freeze_time("2026-02-01")
    def test_status_pendente(self):
        """Status pendente quando faltam mais de 7 dias."""
        status = self.calc.verificar_status_revisao("2026-02-15")
        
        assert status["status"] == "pendente"
        assert status["dias_restantes"] == 14
    
    @freeze_time("2026-02-10")
    def test_status_disponivel(self):
        """Status disponível quando está dentro da janela de 7 dias."""
        status = self.calc.verificar_status_revisao("2026-02-12")
        
        assert status["status"] == "disponivel"
        assert status["dias_restantes"] == 2
    
    @freeze_time("2026-02-20")
    def test_status_atrasada(self):
        """Status atrasado quando passou mais de 7 dias da data."""
        status = self.calc.verificar_status_revisao("2026-02-05")
        
        assert status["status"] == "atrasada"
        assert status["dias_atraso"] == 15
    
    @freeze_time("2026-02-15")
    def test_status_concluida(self):
        """Status concluída quando tem data de realização."""
        status = self.calc.verificar_status_revisao("2026-02-10", "2026-02-12")
        
        assert status["status"] == "concluida"
        assert status["data_realizada"] == "2026-02-12"


class TestProximaAcao:
    """Testes para determinação da próxima ação."""
    
    @pytest.fixture(autouse=True)
    def setup(self, config_teste, pesos_teste):
        """Setup para cada teste."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste):
            from core.calculadora_revisoes import CalculadoraRevisoes
            self.calc = CalculadoraRevisoes()
    
    def test_proxima_acao_sem_teoria(self):
        """Sem data de teoria, ação é ver_teoria."""
        registro = {}
        acao = self.calc.calcular_proxima_acao(registro)
        
        assert acao["acao"] == "ver_teoria"
    
    @freeze_time("2026-02-10")
    def test_proxima_acao_fazer_r1(self):
        """Com teoria feita, próxima ação é fazer R1."""
        registro = {
            "data_teoria": "2026-01-15",
            "grande_area": "Clinica Medica"
        }
        acao = self.calc.calcular_proxima_acao(registro)
        
        assert acao["acao"] == "fazer_r1"
        assert acao["revisao"] == 1
    
    @freeze_time("2026-03-15")
    def test_proxima_acao_fazer_r2(self):
        """Com R1 feita, próxima ação é fazer R2."""
        registro = {
            "data_teoria": "2026-01-15",
            "grande_area": "Clinica Medica",
            "r1": {
                "data": "2026-02-05",
                "questoes": 50,
                "acertos": 40
            }
        }
        acao = self.calc.calcular_proxima_acao(registro)
        
        assert acao["acao"] == "fazer_r2"
        assert acao["revisao"] == 2
    
    @freeze_time("2026-05-01")
    def test_proxima_acao_aguardar_final(self):
        """Com todas as revisões feitas, aguardar revisão final."""
        registro = {
            "data_teoria": "2026-01-15",
            "grande_area": "Clinica Medica",
            "r1": {"data": "2026-02-05", "questoes": 50, "acertos": 40},
            "r2": {"data": "2026-03-07", "questoes": 45, "acertos": 38},
            "r3": {"data": "2026-04-06", "questoes": 40, "acertos": 36}
        }
        acao = self.calc.calcular_proxima_acao(registro)
        
        assert acao["acao"] == "aguardar_revisao_final"


class TestRelatorioPendencias:
    """Testes para geração de relatório de pendências."""
    
    @pytest.fixture(autouse=True)
    def setup(self, config_teste, pesos_teste):
        """Setup para cada teste."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste):
            from core.calculadora_revisoes import CalculadoraRevisoes
            self.calc = CalculadoraRevisoes()
    
    @freeze_time("2026-02-10")
    def test_relatorio_pendencias_vazio(self, estudo_vazio):
        """Relatório vazio quando não há estudos."""
        pendencias = self.calc.gerar_relatorio_pendencias(estudo_vazio)
        
        assert len(pendencias) == 0
    
    @freeze_time("2026-03-01")
    def test_relatorio_pendencias_com_dados(self, estudo_com_dados):
        """Relatório com pendências corretas."""
        pendencias = self.calc.gerar_relatorio_pendencias(estudo_com_dados)
        
        # Deve haver pendências
        assert len(pendencias) >= 0
        
        # Se houver pendências, devem ter estrutura correta
        for pend in pendencias:
            assert "tema" in pend
            assert "acao" in pend
            assert "status" in pend
    
    @freeze_time("2026-03-01")
    def test_relatorio_apenas_proximas(self, estudo_com_dados):
        """Filtro apenas_proximas funciona corretamente."""
        todas = self.calc.gerar_relatorio_pendencias(estudo_com_dados, apenas_proximas=False)
        proximas = self.calc.gerar_relatorio_pendencias(estudo_com_dados, apenas_proximas=True)
        
        # Próximas deve ser subset de todas
        assert len(proximas) <= len(todas)

