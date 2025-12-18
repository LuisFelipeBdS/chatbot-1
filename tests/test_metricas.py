"""
Testes para Sistema de Métricas

Valida os cálculos de nota estimada, taxa de acerto,
estatísticas gerais e indicadores de desempenho.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
from freezegun import freeze_time

# Adicionar path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSistemaMetricas:
    """Testes para a classe SistemaMetricas."""
    
    def test_nota_estimada_sem_dados(self, config_teste, estudo_vazio, pesos_teste, temas_teste):
        """Nota estimada deve usar diagnóstico inicial quando não há dados."""
        with patch('core.metricas.carregar_config', return_value=config_teste), \
             patch('core.metricas.carregar_estudo', return_value=estudo_vazio), \
             patch('core.metricas.carregar_pesos', return_value=pesos_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            resultado = metricas.calcular_nota_estimada()
            
            assert "nota_estimada" in resultado
            # Sem dados de revisão, usa diagnóstico inicial ou confiança baixa
            assert resultado["confianca"] == "baixa" or resultado["fonte"] == "diagnostico_inicial"
    
    def test_nota_estimada_com_dados(self, config_teste, estudo_com_dados, pesos_teste, temas_teste):
        """Nota estimada deve ser calculada corretamente com dados."""
        with patch('core.metricas.carregar_config', return_value=config_teste), \
             patch('core.metricas.carregar_estudo', return_value=estudo_com_dados), \
             patch('core.metricas.carregar_pesos', return_value=pesos_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            resultado = metricas.calcular_nota_estimada()
            
            assert "nota_estimada" in resultado
            assert 0 <= resultado["nota_estimada"] <= 100
            assert "confianca" in resultado


class TestTaxaAcerto:
    """Testes para cálculo de taxa de acerto via estatísticas."""
    
    def test_taxa_acerto_geral_via_estatisticas(self, config_teste, estudo_com_dados, pesos_teste, temas_teste):
        """Taxa de acerto geral via gerar_estatisticas_completas."""
        with patch('core.metricas.carregar_config', return_value=config_teste), \
             patch('core.metricas.carregar_estudo', return_value=estudo_com_dados), \
             patch('core.metricas.carregar_pesos', return_value=pesos_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            stats = metricas.gerar_estatisticas_completas()
            
            assert "taxa_acerto_geral" in stats
            # Dados de teste: 114 acertos / 135 questões = ~84.4%
            esperado = (114 / 135) * 100
            assert abs(stats["taxa_acerto_geral"] - esperado) < 1, \
                f"Esperado ~{esperado:.1f}%, obtido {stats['taxa_acerto_geral']:.1f}%"
    
    def test_taxa_acerto_sem_dados(self, config_teste, pesos_teste, temas_teste):
        """Taxa de acerto deve ser 0 sem dados de estatísticas."""
        # Estudo vazio com estatísticas zeradas
        estudo_sem_stats = {
            "registro_temas": {},
            "questoes_marcadas_importantes": [],
            "estatisticas_gerais": {
                "total_questoes_feitas": 0,
                "total_acertos": 0,
                "simulados_realizados": 0
            }
        }
        
        with patch('core.metricas.carregar_config', return_value=config_teste), \
             patch('core.metricas.carregar_estudo', return_value=estudo_sem_stats), \
             patch('core.metricas.carregar_pesos', return_value=pesos_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            stats = metricas.gerar_estatisticas_completas()
            
            assert stats["taxa_acerto_geral"] == 0, \
                f"Sem dados, taxa deveria ser 0, obtido {stats['taxa_acerto_geral']}"


class TestEstatisticasCompletas:
    """Testes para geração de estatísticas completas."""
    
    @freeze_time("2026-03-15")
    def test_estatisticas_completas_estrutura(self, config_teste, estudo_com_dados, pesos_teste, temas_teste):
        """Estatísticas completas devem ter estrutura correta."""
        with patch('core.metricas.carregar_config', return_value=config_teste), \
             patch('core.metricas.carregar_estudo', return_value=estudo_com_dados), \
             patch('core.metricas.carregar_pesos', return_value=pesos_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            stats = metricas.gerar_estatisticas_completas()
            
            assert "nota_estimada" in stats
            assert "taxa_acerto_geral" in stats
            assert "questoes_total" in stats
            assert "media_semanal" in stats
    
    @freeze_time("2026-03-15")
    def test_questoes_total(self, config_teste, estudo_com_dados, pesos_teste, temas_teste):
        """Total de questões deve corresponder aos dados de estatisticas_gerais."""
        with patch('core.metricas.carregar_config', return_value=config_teste), \
             patch('core.metricas.carregar_estudo', return_value=estudo_com_dados), \
             patch('core.metricas.carregar_pesos', return_value=pesos_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            stats = metricas.gerar_estatisticas_completas()
            
            # Dados de teste têm 135 questões em estatisticas_gerais
            assert stats["questoes_total"] == 135


class TestMediaSemanal:
    """Testes para cálculo de média semanal necessária."""
    
    @freeze_time("2026-03-15")
    def test_media_semanal_calculo(self, config_teste, estudo_com_dados, pesos_teste, temas_teste):
        """Média semanal deve ser calculada corretamente."""
        with patch('core.metricas.carregar_config', return_value=config_teste), \
             patch('core.metricas.carregar_estudo', return_value=estudo_com_dados), \
             patch('core.metricas.carregar_pesos', return_value=pesos_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            # Usar método correto
            media = metricas.calcular_media_questoes_semana()
            
            assert "media_necessaria" in media
            assert "semanas_restantes" in media
            assert "no_ritmo" in media
            assert media["media_necessaria"] >= 0
    
    @freeze_time("2027-11-01")  # Próximo da prova
    def test_media_semanal_proximo_prova(self, config_teste, estudo_vazio, pesos_teste, temas_teste):
        """Próximo da prova com poucas questões, média necessária deve ser alta."""
        with patch('core.metricas.carregar_config', return_value=config_teste), \
             patch('core.metricas.carregar_estudo', return_value=estudo_vazio), \
             patch('core.metricas.carregar_pesos', return_value=pesos_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            media = metricas.calcular_media_questoes_semana()
            
            # Com poucas semanas e zero questões, não está no ritmo
            assert media["no_ritmo"] == False


class TestSetinha:
    """Testes para indicadores visuais (setinhas)."""
    
    def test_setinha_acima_meta(self, config_teste, pesos_teste, temas_teste, estudo_vazio):
        """Setinha deve indicar 'acima' quando performance supera meta."""
        with patch('core.metricas.carregar_config', return_value=config_teste), \
             patch('core.metricas.carregar_estudo', return_value=estudo_vazio), \
             patch('core.metricas.carregar_pesos', return_value=pesos_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            # Meta é 90%, testar com 96%
            seta = metricas.calcular_setinha(96)
            
            assert seta["nivel"] in ["acima", "muito_acima"]
            assert seta["diferenca_meta"] > 0
    
    def test_setinha_abaixo_meta(self, config_teste, pesos_teste, temas_teste, estudo_vazio):
        """Setinha deve indicar 'abaixo' quando performance está abaixo da meta."""
        with patch('core.metricas.carregar_config', return_value=config_teste), \
             patch('core.metricas.carregar_estudo', return_value=estudo_vazio), \
             patch('core.metricas.carregar_pesos', return_value=pesos_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            # Meta é 90%, testar com 75%
            seta = metricas.calcular_setinha(75)
            
            assert seta["nivel"] in ["abaixo", "muito_abaixo"]
            assert seta["diferenca_meta"] < 0
    
    def test_setinha_estrutura(self, config_teste, pesos_teste, temas_teste, estudo_vazio):
        """Setinha deve retornar estrutura completa."""
        with patch('core.metricas.carregar_config', return_value=config_teste), \
             patch('core.metricas.carregar_estudo', return_value=estudo_vazio), \
             patch('core.metricas.carregar_pesos', return_value=pesos_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            seta = metricas.calcular_setinha(85)
            
            assert "nivel" in seta
            assert "icone" in seta
            assert "cor" in seta
            assert "porcentagem" in seta
            assert "diferenca_meta" in seta


class TestCorPerformance:
    """Testes para cores de performance."""
    
    def test_cor_performance_baixa(self, config_teste, pesos_teste, temas_teste, estudo_vazio):
        """Performance baixa deve ter cor de índice baixo."""
        with patch('core.metricas.carregar_config', return_value=config_teste), \
             patch('core.metricas.carregar_estudo', return_value=estudo_vazio), \
             patch('core.metricas.carregar_pesos', return_value=pesos_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            indice = metricas.obter_cor_indice(30)
            
            assert 0 <= indice <= 10, f"30% deveria ter índice baixo, obteve {indice}"
    
    def test_cor_performance_alta(self, config_teste, pesos_teste, temas_teste, estudo_vazio):
        """Performance alta deve ter cor de índice alto."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_vazio), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            indice = metricas.obter_cor_indice(95)
            
            assert 20 <= indice <= 24, f"95% deveria ter índice alto, obteve {indice}"


class TestBolinhaPrioridade:
    """Testes para bolinhas de prioridade."""
    
    def test_bolinha_prioridade_baixa(self, config_teste, pesos_teste, temas_teste, estudo_vazio):
        """Score baixo deve retornar bolinha vazia/quarto."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_vazio), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            bolinha = metricas.calcular_bolinha_prioridade(0.1)
            
            assert bolinha["nivel"] == "vazia"
    
    def test_bolinha_prioridade_alta(self, config_teste, pesos_teste, temas_teste, estudo_vazio):
        """Score alto deve retornar bolinha cheia."""
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_vazio), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste):
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            bolinha = metricas.calcular_bolinha_prioridade(0.9)
            
            assert bolinha["nivel"] == "cheia"
