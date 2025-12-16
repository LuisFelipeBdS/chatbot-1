"""
Algoritmo de Sugestão de Questões

Calcula o número ideal de questões por tema considerando:
- Peso da grande área no ENAMED
- Classificação High-Yield/Low-Yield
- Performance do aluno nas revisões
- Sincronização com rodízio atual
- Distância até a prova
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import (
    carregar_config, carregar_pesos, carregar_temas,
    carregar_estudo, carregar_calendario, obter_rodizio_atual,
    calcular_semanas_ate_prova
)
from utils.constants import (
    MULTIPLICADORES, BONUS_RODIZIO_ATUAL, FATOR_MARGEM,
    META_QUESTOES_SEMANA, DISTRIBUICAO_REVISOES
)


class AlgoritmoSugestao:
    """
    Motor de cálculo para sugestão de questões por tema.
    
    Implementa a fórmula:
    questoes_tema = base * peso_area * multiplicador_yield * fator_performance * bonus_rodizio
    """
    
    def __init__(self):
        self.config = carregar_config()
        self.pesos = carregar_pesos()
        self.temas = carregar_temas()
        self.estudo = carregar_estudo()
        self.calendario = carregar_calendario()
        
        # Configurações do usuário
        self.nota_meta = self.config.get("metas", {}).get("nota_meta", 90)
        self.questoes_semana = self.config.get("metas", {}).get("questoes_semana_meta", META_QUESTOES_SEMANA)
        self.margem = self.config.get("modo_estudo", {}).get("margem", "equilibrado")
        self.modo = self.config.get("modo_estudo", {}).get("tipo", "focado_resultado")
        
        # Data da prova
        self.data_prova = self.config.get("usuario", {}).get("data_prova_estimada", "2027-11-15")
    
    def obter_peso_area(self, grande_area: str) -> float:
        """Retorna o peso da grande área no ENAMED."""
        return self.pesos.get("pesos_areas", {}).get(grande_area, 0.1)
    
    def obter_multiplicador_yield(self, tema: str, grande_area: str) -> float:
        """
        Retorna o multiplicador baseado na classificação High/Low Yield.
        """
        # Verificar se é high-yield
        high_yield_temas = self.pesos.get("temas_high_yield", {}).get(grande_area, [])
        
        for hy_tema in high_yield_temas:
            if hy_tema.lower() in tema.lower() or tema.lower() in hy_tema.lower():
                return MULTIPLICADORES["high_yield"]
        
        # Verificar se é low-yield
        low_yield_temas = self.pesos.get("temas_low_yield", [])
        
        for ly_tema in low_yield_temas:
            if ly_tema.lower() in tema.lower():
                return MULTIPLICADORES["low_yield"]
        
        return MULTIPLICADORES["normal"]
    
    def calcular_fator_performance(
        self, 
        tema_key: str,
        numero_revisao: int
    ) -> float:
        """
        Calcula o fator de ajuste baseado na performance anterior.
        
        - Performance baixa (< 60%): aumenta questões (fator > 1)
        - Performance média (60-80%): mantém (fator = 1)
        - Performance alta (> 80%): reduz questões (fator < 1)
        """
        registro_tema = self.estudo.get("registro_temas", {}).get(tema_key, {})
        
        if numero_revisao == 1:
            # Usar diagnóstico inicial
            diag = self.config.get("diagnostico_inicial", {})
            # Pegar média do diagnóstico
            valores = [v for v in diag.values() if v is not None]
            performance = sum(valores) / len(valores) if valores else 50
        else:
            # Usar performance da revisão anterior
            rev_anterior = f"r{numero_revisao - 1}"
            dados_rev = registro_tema.get(rev_anterior, {})
            
            if dados_rev.get("questoes") and dados_rev.get("acertos"):
                performance = (dados_rev["acertos"] / dados_rev["questoes"]) * 100
            else:
                performance = 50  # Assumir média se não houver dados
        
        # Calcular fator
        if performance < 50:
            return 1.5  # Aumentar bastante
        elif performance < 60:
            return 1.3
        elif performance < 70:
            return 1.1
        elif performance < 80:
            return 1.0
        elif performance < 90:
            return 0.9
        else:
            return 0.7  # Reduzir para temas dominados
    
    def verificar_bonus_rodizio(self, tema: str, grande_area: str) -> float:
        """
        Verifica se o tema está relacionado ao rodízio atual.
        Retorna o bônus de 20% se estiver.
        """
        rodizio_atual = obter_rodizio_atual(self.calendario)
        
        if not rodizio_atual:
            return 1.0
        
        # Verificar se a grande área corresponde
        if rodizio_atual.get("grande_area_principal") == grande_area:
            return BONUS_RODIZIO_ATUAL
        
        # Verificar se o tema está na lista de prioritários do rodízio
        temas_prioritarios = rodizio_atual.get("temas_prioritarios", [])
        for tp in temas_prioritarios:
            if tp.lower() in tema.lower() or tema.lower() in tp.lower():
                return BONUS_RODIZIO_ATUAL
        
        return 1.0
    
    def calcular_base_questoes(self) -> int:
        """
        Calcula a base de questões por tema baseado no modo de estudo.
        """
        semanas = calcular_semanas_ate_prova(self.data_prova)
        
        if self.modo == "focado_resultado":
            # Calcular baseado na meta de nota
            # Fórmula simplificada: quanto maior a meta, mais questões
            fator_meta = (self.nota_meta - 60) / 30  # 0 a 1.33 para metas de 60-100%
            base = int(50 * (1 + fator_meta))
        else:
            # Focado na quantidade - usar meta definida
            total_temas = sum(
                len(area["temas"]) 
                for area in self.temas.get("grandes_areas", {}).values()
            )
            if total_temas > 0:
                base = int(self.questoes_semana / (total_temas / 10))  # Distribuir
            else:
                base = 50
        
        # Aplicar fator de margem
        base = int(base * FATOR_MARGEM.get(self.margem, 1.0))
        
        return max(20, base)  # Mínimo de 20 questões
    
    def calcular_sugestao_tema(
        self,
        tema: str,
        grande_area: str,
        numero_revisao: int = 1,
        tema_key: str = None
    ) -> Dict[str, Any]:
        """
        Calcula a sugestão de questões para um tema específico.
        
        Retorna:
        - questoes_sugeridas: número de questões
        - detalhes: breakdown dos fatores
        """
        base = self.calcular_base_questoes()
        peso_area = self.obter_peso_area(grande_area)
        multiplicador_yield = self.obter_multiplicador_yield(tema, grande_area)
        fator_performance = self.calcular_fator_performance(tema_key or tema, numero_revisao)
        bonus_rodizio = self.verificar_bonus_rodizio(tema, grande_area)
        
        # Aplicar distribuição por revisão
        percentual_revisao = {
            1: DISTRIBUICAO_REVISOES["primeira"],
            2: DISTRIBUICAO_REVISOES["segunda"],
            3: DISTRIBUICAO_REVISOES["terceira"]
        }.get(numero_revisao, 0.33)
        
        # Fórmula principal
        questoes = base * peso_area * multiplicador_yield * fator_performance * bonus_rodizio
        questoes = int(questoes * (1 + percentual_revisao))  # Ajuste por revisão
        
        # Limites
        questoes = max(10, min(500, questoes))
        
        return {
            "questoes_sugeridas": questoes,
            "detalhes": {
                "base": base,
                "peso_area": peso_area,
                "multiplicador_yield": multiplicador_yield,
                "is_high_yield": multiplicador_yield > 1,
                "fator_performance": fator_performance,
                "bonus_rodizio": bonus_rodizio,
                "percentual_revisao": percentual_revisao,
                "numero_revisao": numero_revisao
            }
        }
    
    def gerar_plano_semanal(self, apenas_proximas: bool = True) -> Dict[str, Any]:
        """
        Gera um plano semanal de questões para os temas com revisão próxima.
        
        Args:
            apenas_proximas: Se True, mostra apenas revisões nos próximos 7 dias
        """
        from .calculadora_revisoes import CalculadoraRevisoes
        
        calc_rev = CalculadoraRevisoes()
        pendencias = calc_rev.gerar_relatorio_pendencias(self.estudo, apenas_proximas=apenas_proximas)
        
        plano = {
            "semana": datetime.now().strftime("%Y-W%W"),
            "meta_questoes": self.questoes_semana,
            "temas": [],
            "total_sugerido": 0
        }
        
        for pend in pendencias[:10]:  # Top 10 mais próximas
            tema_key = pend["tema"]
            
            # Encontrar dados do tema
            for area, dados in self.temas.get("grandes_areas", {}).items():
                for tema_info in dados.get("temas", []):
                    if tema_info["nome"] == tema_key or tema_key in tema_info["nome"]:
                        numero_rev = int(pend["acao"].split("_")[-1].replace("r", "")) if "r" in pend["acao"] else 1
                        
                        sugestao = self.calcular_sugestao_tema(
                            tema_info["nome"],
                            area,
                            numero_rev,
                            tema_key
                        )
                        
                        plano["temas"].append({
                            "tema": tema_key,
                            "grande_area": area,
                            "revisao": numero_rev,
                            "questoes": sugestao["questoes_sugeridas"],
                            "urgencia": pend["urgencia_score"],
                            "is_high_yield": sugestao["detalhes"]["is_high_yield"],
                            "status": pend["status"],
                            "data_sugerida": pend.get("data_sugerida"),
                            "dias_restantes": pend.get("dias_restantes", 0)
                        })
                        
                        plano["total_sugerido"] += sugestao["questoes_sugeridas"]
                        break
        
        # Ordenar por data sugerida (mais próxima primeiro)
        plano["temas"].sort(key=lambda x: x.get("data_sugerida") or "9999-99-99")
        
        return plano
    
    def calcular_prioridade_tema(self, tema: str, grande_area: str) -> float:
        """
        Calcula um score de prioridade de 0 a 1 para visualização (bolinhas).
        """
        sugestao = self.calcular_sugestao_tema(tema, grande_area)
        detalhes = sugestao["detalhes"]
        
        # Combinar fatores para gerar score
        score = 0.0
        
        # Peso da área contribui com até 0.3
        score += detalhes["peso_area"]
        
        # High-yield contribui com 0.2
        if detalhes["is_high_yield"]:
            score += 0.2
        
        # Performance baixa aumenta prioridade
        if detalhes["fator_performance"] > 1.2:
            score += 0.3
        elif detalhes["fator_performance"] > 1.0:
            score += 0.15
        
        # Bonus rodízio
        if detalhes["bonus_rodizio"] > 1:
            score += 0.2
        
        return min(1.0, score)


def calcular_questoes_tema(
    tema: str,
    grande_area: str,
    numero_revisao: int = 1
) -> int:
    """
    Função de conveniência para calcular questões de um tema.
    """
    alg = AlgoritmoSugestao()
    resultado = alg.calcular_sugestao_tema(tema, grande_area, numero_revisao)
    return resultado["questoes_sugeridas"]


def obter_plano_semanal() -> Dict[str, Any]:
    """
    Função de conveniência para obter plano semanal.
    """
    alg = AlgoritmoSugestao()
    return alg.gerar_plano_semanal()

