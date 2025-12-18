"""
Testes de Smoke - Validação com Dados Reais

Estes testes verificam se o sistema funciona corretamente
com os arquivos JSON reais (sem mocks), garantindo que
a estrutura de dados em produção é compatível com o código.
"""

import pytest
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


class TestCarregamentoDadosReais:
    """Testes para verificar que os JSONs reais carregam corretamente."""
    
    def test_carregar_config_real(self):
        """Verifica que config.json carrega e tem campos obrigatórios."""
        from utils.helpers import carregar_config
        
        config = carregar_config()
        
        # Campos obrigatórios
        assert "usuario" in config, "config.json deve ter campo 'usuario'"
        assert "metas" in config, "config.json deve ter campo 'metas'"
        assert "diagnostico_inicial" in config, "config.json deve ter campo 'diagnostico_inicial'"
        assert "rotina" in config, "config.json deve ter campo 'rotina'"
        
        # Estrutura de rotina
        rotina = config["rotina"]
        assert "dias_disponiveis" in rotina
        assert "horas_por_dia" in rotina
        assert "questoes_por_hora" in rotina
    
    def test_carregar_estudo_real(self):
        """Verifica que estudo.json carrega e tem estrutura correta."""
        from utils.helpers import carregar_estudo
        
        estudo = carregar_estudo()
        
        assert "registro_temas" in estudo
        assert "estatisticas_gerais" in estudo
        assert isinstance(estudo["registro_temas"], dict)
    
    def test_carregar_pesos_real(self):
        """Verifica que pesos_enamed.json carrega corretamente."""
        from utils.helpers import carregar_pesos
        
        pesos = carregar_pesos()
        
        assert "pesos_areas" in pesos
        assert "temas_high_yield" in pesos
        assert "multiplicadores" in pesos
        
        # Verificar que todas as áreas têm peso
        areas_esperadas = [
            "Clinica Medica", "Saude Coletiva", "Pediatria",
            "Ginecologia e Obstetricia", "Cirurgia Geral", "Saude Mental"
        ]
        for area in areas_esperadas:
            assert area in pesos["pesos_areas"], f"Área '{area}' ausente em pesos_areas"
    
    def test_carregar_temas_real(self):
        """Verifica que temas.json carrega corretamente."""
        from utils.helpers import carregar_temas
        
        temas = carregar_temas()
        
        assert "grandes_areas" in temas
        assert len(temas["grandes_areas"]) > 0
        
        # Verificar estrutura de um tema
        for area, dados in temas["grandes_areas"].items():
            assert "temas" in dados, f"Área '{area}' sem lista de temas"
            assert len(dados["temas"]) > 0, f"Área '{area}' sem temas"
    
    def test_carregar_calendario_real(self):
        """Verifica que calendario.json carrega corretamente."""
        from utils.helpers import carregar_calendario
        
        calendario = carregar_calendario()
        
        assert "ano_1" in calendario
        assert "2026" in calendario["ano_1"]
        
        # Verificar estrutura de rodízio
        rodizios = calendario["ano_1"]["2026"]
        assert len(rodizios) > 0
        
        for rodizio in rodizios:
            assert "rodizio" in rodizio
            assert "inicio" in rodizio
            assert "fim" in rodizio


class TestInstanciacaoClassesReais:
    """Testes para verificar que as classes instanciam com dados reais."""
    
    def test_sistema_metricas_instancia(self):
        """Verifica que SistemaMetricas instancia com dados reais."""
        from core.metricas import SistemaMetricas
        
        metricas = SistemaMetricas()
        
        assert metricas.config is not None
        assert metricas.pesos is not None
        assert metricas.estudo is not None
    
    def test_algoritmo_sugestao_instancia(self):
        """Verifica que AlgoritmoSugestao instancia com dados reais."""
        from core.algoritmo_sugestao import AlgoritmoSugestao
        
        algoritmo = AlgoritmoSugestao()
        
        assert algoritmo.config is not None
        assert algoritmo.pesos is not None
        assert algoritmo.temas is not None
    
    def test_calculadora_revisoes_instancia(self):
        """Verifica que CalculadoraRevisoes instancia com dados reais."""
        from core.calculadora_revisoes import CalculadoraRevisoes
        
        calc = CalculadoraRevisoes()
        
        assert calc.config is not None
        assert calc.pesos is not None
        assert calc.data_prova is not None


class TestMetodosComDadosReais:
    """Testes para verificar que métodos funcionam com dados reais."""
    
    def test_gerar_estatisticas_completas(self):
        """Verifica que gerar_estatisticas_completas funciona."""
        from core.metricas import SistemaMetricas
        
        metricas = SistemaMetricas()
        stats = metricas.gerar_estatisticas_completas()
        
        # Campos obrigatórios no retorno
        assert "nota_estimada" in stats
        assert "taxa_acerto_geral" in stats
        assert "questoes_total" in stats
        assert "media_semanal" in stats
        
        # nota_estimada é um dict contendo nota_estimada, confianca, etc.
        nota_info = stats["nota_estimada"]
        assert isinstance(nota_info, dict)
        assert "nota_estimada" in nota_info
        assert isinstance(nota_info["nota_estimada"], (int, float))
        assert 0 <= nota_info["nota_estimada"] <= 100
    
    def test_calcular_nota_estimada(self):
        """Verifica que calcular_nota_estimada funciona."""
        from core.metricas import SistemaMetricas
        
        metricas = SistemaMetricas()
        resultado = metricas.calcular_nota_estimada()
        
        assert "nota_estimada" in resultado
        assert "confianca" in resultado
        assert resultado["confianca"] in ["baixa", "media", "alta"]
    
    def test_calcular_setinha(self):
        """Verifica que calcular_setinha funciona."""
        from core.metricas import SistemaMetricas
        
        metricas = SistemaMetricas()
        seta = metricas.calcular_setinha(75)
        
        assert "nivel" in seta
        assert "icone" in seta
        assert "cor" in seta
    
    def test_gerar_sugestao_questoes(self):
        """Verifica que sugestão de questões funciona."""
        from core.algoritmo_sugestao import calcular_questoes_tema
        
        # Função no nível do módulo, não método da classe
        sugestao = calcular_questoes_tema("Tuberculose", "Clinica Medica")
        
        assert isinstance(sugestao, int)
        assert sugestao >= 0


class TestConsistenciaEntreArquivos:
    """Testes para verificar consistência entre diferentes JSONs."""
    
    def test_areas_consistentes(self):
        """Verifica que as áreas são consistentes entre pesos e temas."""
        from utils.helpers import carregar_pesos, carregar_temas
        
        pesos = carregar_pesos()
        temas = carregar_temas()
        
        areas_pesos = set(pesos["pesos_areas"].keys())
        areas_temas = set(temas["grandes_areas"].keys())
        
        # Verificar sobreposição (pode haver diferenças de nomenclatura)
        # Pelo menos as principais áreas devem estar em ambos
        areas_principais = ["Clinica Medica", "Cirurgia Geral", "Pediatria"]
        for area in areas_principais:
            assert area in areas_pesos, f"Área '{area}' ausente em pesos"
            assert area in areas_temas, f"Área '{area}' ausente em temas"
    
    def test_temas_high_yield_existem(self):
        """Verifica que temas high_yield em pesos existem em temas.json."""
        from utils.helpers import carregar_pesos, carregar_temas
        
        pesos = carregar_pesos()
        temas = carregar_temas()
        
        # Coletar todos os nomes de temas
        todos_temas = set()
        for area, dados in temas["grandes_areas"].items():
            for tema in dados["temas"]:
                todos_temas.add(tema["nome"])
        
        # Verificar que pelo menos alguns temas HY existem
        temas_hy_encontrados = 0
        for area, lista_hy in pesos.get("temas_high_yield", {}).items():
            for tema_hy in lista_hy:
                if tema_hy in todos_temas:
                    temas_hy_encontrados += 1
        
        # Pelo menos 25% dos temas HY devem existir (alguns têm nomes ligeiramente diferentes)
        total_hy = sum(len(v) for v in pesos.get("temas_high_yield", {}).values())
        assert temas_hy_encontrados >= total_hy * 0.25, \
            f"Apenas {temas_hy_encontrados}/{total_hy} temas HY encontrados em temas.json"

