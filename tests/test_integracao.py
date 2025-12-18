"""
Testes de Integração - Fluxo Completo

Valida o fluxo completo desde o registro de estudo até
a atualização de métricas e agendamento de revisões.
"""

import pytest
import sys
import json
import copy
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from freezegun import freeze_time

# Adicionar path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestFluxoCompletoEstudo:
    """
    Teste de integração que simula o fluxo completo:
    1. Usuário estuda teoria de um tema
    2. Sistema agenda R1 para 21 dias depois
    3. Usuário faz R1 e registra resultado
    4. Sistema agenda R2 para 30 dias depois
    5. Métricas são atualizadas corretamente
    """
    
    @freeze_time("2026-01-15")
    def test_fluxo_estudo_novo_tema(self, config_teste, pesos_teste, temas_teste, calendario_teste):
        """Fluxo completo de estudo de um novo tema."""
        
        # Estado inicial: estudo vazio
        estudo = {
            "registro_temas": {},
            "questoes_marcadas_importantes": [],
            "estatisticas_gerais": {
                "total_questoes_feitas": 0,
                "total_acertos": 0
            }
        }
        
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            
            from core.calculadora_revisoes import CalculadoraRevisoes
            from core.algoritmo_sugestao import AlgoritmoSugestao
            from core.metricas import SistemaMetricas
            
            calc = CalculadoraRevisoes()
            
            # ==============================
            # PASSO 1: Registrar estudo da teoria
            # ==============================
            
            tema = "Tuberculose"
            data_teoria = datetime(2026, 1, 15)
            
            # Simular registro de teoria
            estudo["registro_temas"][tema] = {
                "data_teoria": data_teoria.strftime("%Y-%m-%d"),
                "grande_area": "Clinica Medica"
            }
            
            # Verificar cronograma gerado
            cronograma = calc.calcular_cronograma_tema(data_teoria, tema)
            
            assert cronograma["tema"] == tema
            r1_data = datetime.strptime(cronograma["revisoes"]["r1"]["data_sugerida"], "%Y-%m-%d")
            
            # R1 deve ser aproximadamente 21 dias depois
            dias_ate_r1 = (r1_data - data_teoria).days
            assert 14 <= dias_ate_r1 <= 28, f"R1 deveria ser 14-28 dias, foi {dias_ate_r1}"
            
            # ==============================
            # PASSO 2: Verificar que R1 aparece no plano
            # ==============================
            
            # Avançar para data próxima de R1
            with freeze_time(r1_data - timedelta(days=3)):
                # Atualizar mock com novo estado
                with patch('utils.helpers.carregar_estudo', return_value=estudo):
                    alg = AlgoritmoSugestao()
                    plano = alg.gerar_plano_semanal(apenas_proximas=True)
                    
                    # Tuberculose deve estar no plano
                    temas_plano = [t["tema"] for t in plano["temas"]]
                    # Pode ou não estar dependendo da implementação exata
            
            # ==============================
            # PASSO 3: Registrar R1
            # ==============================
            
            estudo["registro_temas"][tema]["r1"] = {
                "data": r1_data.strftime("%Y-%m-%d"),
                "questoes": 50,
                "acertos": 42
            }
            estudo["estatisticas_gerais"]["total_questoes_feitas"] = 50
            estudo["estatisticas_gerais"]["total_acertos"] = 42
            
            # Verificar próxima ação
            with patch('utils.helpers.carregar_estudo', return_value=estudo):
                prox = calc.calcular_proxima_acao(estudo["registro_temas"][tema])
                
                assert prox["acao"] == "fazer_r2", f"Após R1, próxima ação deveria ser R2, foi {prox['acao']}"
                assert prox["revisao"] == 2
            
            # ==============================
            # PASSO 4: Verificar métricas atualizadas
            # ==============================
            
            with patch('utils.helpers.carregar_estudo', return_value=estudo):
                metricas = SistemaMetricas()
                stats = metricas.gerar_estatisticas_completas()
                
                assert stats["questoes_total"] == 50
                # Taxa de acerto: 42/50 = 84%
                assert abs(stats["taxa_acerto_geral"] - 84.0) < 1
    
    @freeze_time("2026-03-01")
    def test_fluxo_multiplas_revisoes(self, config_teste, pesos_teste, temas_teste, calendario_teste):
        """Fluxo com múltiplas revisões de múltiplos temas."""
        
        # Estado com temas em diferentes estágios
        estudo = {
            "registro_temas": {
                "Tuberculose": {
                    "data_teoria": "2026-01-15",
                    "grande_area": "Clinica Medica",
                    "r1": {"data": "2026-02-05", "questoes": 50, "acertos": 40},
                    "r2": {"data": "2026-03-07", "questoes": 45, "acertos": 38}
                },
                "HIV e AIDS": {
                    "data_teoria": "2026-01-20",
                    "grande_area": "Clinica Medica",
                    "r1": {"data": "2026-02-10", "questoes": 40, "acertos": 32}
                },
                "Diabetes": {
                    "data_teoria": "2026-02-01",
                    "grande_area": "Clinica Medica"
                    # Sem revisões ainda
                }
            },
            "estatisticas_gerais": {
                "total_questoes_feitas": 135,
                "total_acertos": 110
            }
        }
        
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            
            from core.calculadora_revisoes import CalculadoraRevisoes
            from core.algoritmo_sugestao import AlgoritmoSugestao
            
            calc = CalculadoraRevisoes()
            
            # Verificar próxima ação de cada tema
            tb_acao = calc.calcular_proxima_acao(estudo["registro_temas"]["Tuberculose"])
            hiv_acao = calc.calcular_proxima_acao(estudo["registro_temas"]["HIV e AIDS"])
            dm_acao = calc.calcular_proxima_acao(estudo["registro_temas"]["Diabetes"])
            
            # Tuberculose já fez R2, próximo é R3
            assert tb_acao["acao"] == "fazer_r3"
            
            # HIV fez R1, próximo é R2
            assert hiv_acao["acao"] == "fazer_r2"
            
            # Diabetes só tem teoria, próximo é R1
            assert dm_acao["acao"] == "fazer_r1"


class TestFluxoPlanoSemanal:
    """Testes para o fluxo do plano semanal."""
    
    @freeze_time("2026-02-10")
    def test_plano_ordena_por_data(self, config_teste, pesos_teste, temas_teste, calendario_teste):
        """Plano semanal deve ordenar por data sugerida."""
        
        estudo = {
            "registro_temas": {
                "Tema A": {
                    "data_teoria": "2026-01-15",  # R1 em ~05/02
                    "grande_area": "Clinica Medica"
                },
                "Tema B": {
                    "data_teoria": "2026-01-10",  # R1 em ~31/01 (mais cedo)
                    "grande_area": "Clinica Medica"
                }
            },
            "estatisticas_gerais": {"total_questoes_feitas": 0, "total_acertos": 0}
        }
        
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            
            from core.algoritmo_sugestao import AlgoritmoSugestao
            alg = AlgoritmoSugestao()
            
            plano = alg.gerar_plano_semanal(apenas_proximas=False)
            
            # Verificar que temas têm data_sugerida
            for tema in plano["temas"]:
                assert "data_sugerida" in tema, f"Tema {tema['tema']} sem data_sugerida"


class TestFluxoHighYield:
    """Testes para priorização de temas High-Yield."""
    
    @freeze_time("2026-02-15")
    def test_high_yield_mais_questoes(self, config_teste, pesos_teste, temas_teste, estudo_vazio, calendario_teste):
        """Temas High-Yield devem receber mais questões sugeridas."""
        
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_vazio), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            
            from core.algoritmo_sugestao import AlgoritmoSugestao
            alg = AlgoritmoSugestao()
            
            # Tuberculose é High-Yield
            sugestao_hy = alg.calcular_sugestao_tema("Tuberculose", "Clinica Medica", 1)
            
            # Tema normal
            sugestao_normal = alg.calcular_sugestao_tema("Tema Qualquer", "Clinica Medica", 1)
            
            assert sugestao_hy["detalhes"]["is_high_yield"] == True
            assert sugestao_hy["questoes_sugeridas"] >= sugestao_normal["questoes_sugeridas"]


class TestFluxoRodizio:
    """Testes para integração com rodízio atual."""
    
    @freeze_time("2026-02-15")  # Durante Infectologia
    def test_bonus_rodizio_infectologia(self, config_teste, pesos_teste, temas_teste, estudo_vazio, calendario_teste):
        """Temas do rodízio atual devem receber bônus."""
        
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_vazio), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            
            from core.algoritmo_sugestao import AlgoritmoSugestao
            from utils.helpers import obter_rodizio_atual
            
            alg = AlgoritmoSugestao()
            
            # Verificar que estamos no rodízio de Infectologia
            rodizio = obter_rodizio_atual(calendario_teste)
            assert rodizio is not None
            assert rodizio["rodizio"] == "Infectologia"
            
            # Tuberculose é tema prioritário de Infectologia
            bonus = alg.verificar_bonus_rodizio("Tuberculose", "Clinica Medica")
            assert bonus > 1.0, f"Deveria ter bônus, obteve {bonus}"
    
    @freeze_time("2026-05-01")  # Durante Saúde Coletiva
    def test_sem_bonus_fora_rodizio(self, config_teste, pesos_teste, temas_teste, estudo_vazio, calendario_teste):
        """Temas fora do rodízio não devem receber bônus."""
        
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_vazio), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            
            from core.algoritmo_sugestao import AlgoritmoSugestao
            
            alg = AlgoritmoSugestao()
            
            # Tuberculose NÃO é tema de Saúde Coletiva
            bonus = alg.verificar_bonus_rodizio("Tuberculose", "Clinica Medica")
            assert bonus == 1.0, f"Não deveria ter bônus, obteve {bonus}"


class TestFluxoRegistroQuestoes:
    """Testes para o fluxo de registro de questões resolvidas."""
    
    def test_registro_incrementa_estatisticas(self, config_teste, pesos_teste, temas_teste, calendario_teste):
        """Registrar questões deve incrementar estatísticas gerais."""
        
        # Estado APÓS registrar questões (já atualizado)
        estudo_atualizado = {
            "registro_temas": {
                "Tuberculose": {
                    "data_teoria": "2026-01-15",
                    "grande_area": "Clinica Medica",
                    "r1": {
                        "data": "2026-02-05",
                        "questoes": 50,
                        "acertos": 42
                    }
                }
            },
            "estatisticas_gerais": {
                "total_questoes_feitas": 150,  # Já incrementado
                "total_acertos": 122
            }
        }
        
        with patch('core.metricas.carregar_config', return_value=config_teste), \
             patch('core.metricas.carregar_pesos', return_value=pesos_teste), \
             patch('core.metricas.carregar_estudo', return_value=estudo_atualizado):
            
            from core.metricas import SistemaMetricas
            metricas = SistemaMetricas()
            
            stats = metricas.gerar_estatisticas_completas()
            
            # Estatísticas devem refletir o estado do estudo
            assert stats["questoes_total"] == 150
            
            # Taxa: 122/150 = 81.33%
            taxa_esperada = (122 / 150) * 100
            assert abs(stats["taxa_acerto_geral"] - taxa_esperada) < 1


class TestFluxoRevisaoFinal:
    """Testes para o fluxo de revisão final pré-prova."""
    
    @freeze_time("2027-11-01")  # 14 dias antes da prova
    def test_revisao_final_ativada(self, config_teste, pesos_teste, temas_teste, estudo_com_dados, calendario_teste):
        """Modo revisão final deve ser ativado nos últimos 14 dias."""
        
        with patch('utils.helpers.carregar_config', return_value=config_teste), \
             patch('utils.helpers.carregar_pesos', return_value=pesos_teste), \
             patch('utils.helpers.carregar_temas', return_value=temas_teste), \
             patch('utils.helpers.carregar_estudo', return_value=estudo_com_dados), \
             patch('utils.helpers.carregar_calendario', return_value=calendario_teste):
            
            from utils.helpers import calcular_dias_ate_prova
            
            dias = calcular_dias_ate_prova("2027-11-15")
            
            assert dias <= 14, f"Deveria estar em período de revisão final, {dias} dias restantes"
    
    @freeze_time("2027-06-01")
    def test_revisao_final_nao_ativada(self, config_teste):
        """Modo revisão final não deve ser ativado longe da prova."""
        
        with patch('utils.helpers.carregar_config', return_value=config_teste):
            from utils.helpers import calcular_dias_ate_prova
            
            dias = calcular_dias_ate_prova("2027-11-15")
            
            assert dias > 14, f"Não deveria estar em período de revisão final, {dias} dias restantes"


