"""
Calculadora de Revisões - Distributed Practice

Implementa o algoritmo de espaçamento de revisões baseado na metodologia
SuperPlanner/FluidMed.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import carregar_config, carregar_pesos
from utils.constants import (
    INTERVALOS_REVISAO,
    DISTRIBUICAO_REVISOES
)


class CalculadoraRevisoes:
    """
    Calcula as datas de revisão usando Distributed Practice.
    
    O intervalo entre revisões diminui conforme a prova se aproxima,
    mantendo o princípio do espaçamento para maximizar retenção.
    """
    
    def __init__(self):
        self.config = carregar_config()
        self.pesos = carregar_pesos()
        self.data_prova = datetime.strptime(
            self.config.get("usuario", {}).get("data_prova_estimada", "2027-11-15"),
            "%Y-%m-%d"
        )
    
    def calcular_fator_proximidade(self, data_atual: datetime = None) -> float:
        """
        Calcula o fator de ajuste baseado na proximidade da prova.
        
        Quanto mais perto da prova, menor o intervalo entre revisões.
        Retorna um valor entre 0.3 (muito perto) e 1.0 (longe).
        """
        if data_atual is None:
            data_atual = datetime.now()
        
        dias_ate_prova = (self.data_prova - data_atual).days
        
        # Se faltam mais de 300 dias, fator = 1.0 (intervalos normais)
        # Se faltam menos de 60 dias, fator = 0.3 (intervalos reduzidos)
        if dias_ate_prova >= 300:
            return 1.0
        elif dias_ate_prova <= 60:
            return 0.3
        else:
            # Interpolação linear entre 1.0 e 0.3
            return 0.3 + (dias_ate_prova - 60) / (300 - 60) * 0.7
    
    def calcular_intervalo_teoria_r1(self, data_teoria: datetime) -> int:
        """
        Calcula o intervalo entre teoria e primeira revisão.
        
        No início do ano: ~21 dias
        No final do ano: ~7 dias
        """
        fator = self.calcular_fator_proximidade(data_teoria)
        
        intervalo_max = INTERVALOS_REVISAO["teoria_para_r1_inicio_ano"]  # 21
        intervalo_min = INTERVALOS_REVISAO["teoria_para_r1_fim_ano"]      # 7
        
        intervalo = int(intervalo_min + (intervalo_max - intervalo_min) * fator)
        return max(intervalo_min, intervalo)
    
    def calcular_intervalo_entre_revisoes(self, data_revisao: datetime, numero_revisao: int) -> int:
        """
        Calcula o intervalo entre revisões consecutivas.
        
        R1 -> R2: ~30 dias (ajustado pelo fator de proximidade)
        R2 -> R3: ~30 dias (ajustado pelo fator de proximidade)
        """
        fator = self.calcular_fator_proximidade(data_revisao)
        
        if numero_revisao == 1:  # R1 -> R2
            intervalo_base = INTERVALOS_REVISAO["r1_para_r2"]
        else:  # R2 -> R3
            intervalo_base = INTERVALOS_REVISAO["r2_para_r3"]
        
        intervalo = int(intervalo_base * fator)
        return max(7, intervalo)  # Mínimo de 7 dias entre revisões
    
    def calcular_cronograma_tema(
        self, 
        data_teoria: datetime,
        tema: str = None
    ) -> Dict[str, Any]:
        """
        Calcula o cronograma completo de revisões para um tema.
        
        Retorna as datas recomendadas para cada revisão e o status atual.
        """
        cronograma = {
            "tema": tema,
            "data_teoria": data_teoria.strftime("%Y-%m-%d"),
            "revisoes": {}
        }
        
        # Primeira revisão
        intervalo_r1 = self.calcular_intervalo_teoria_r1(data_teoria)
        data_r1 = data_teoria + timedelta(days=intervalo_r1)
        cronograma["revisoes"]["r1"] = {
            "data_sugerida": data_r1.strftime("%Y-%m-%d"),
            "intervalo_dias": intervalo_r1,
            "percentual_questoes": DISTRIBUICAO_REVISOES["primeira"]
        }
        
        # Segunda revisão
        intervalo_r2 = self.calcular_intervalo_entre_revisoes(data_r1, 1)
        data_r2 = data_r1 + timedelta(days=intervalo_r2)
        cronograma["revisoes"]["r2"] = {
            "data_sugerida": data_r2.strftime("%Y-%m-%d"),
            "intervalo_dias": intervalo_r2,
            "percentual_questoes": DISTRIBUICAO_REVISOES["segunda"]
        }
        
        # Terceira revisão
        intervalo_r3 = self.calcular_intervalo_entre_revisoes(data_r2, 2)
        data_r3 = data_r2 + timedelta(days=intervalo_r3)
        cronograma["revisoes"]["r3"] = {
            "data_sugerida": data_r3.strftime("%Y-%m-%d"),
            "intervalo_dias": intervalo_r3,
            "percentual_questoes": DISTRIBUICAO_REVISOES["terceira"]
        }
        
        # Verificar se R3 não ultrapassa a data limite (14 dias antes da prova)
        data_limite = self.data_prova - timedelta(days=14)
        if data_r3 > data_limite:
            # Ajustar para não ultrapassar
            cronograma["revisoes"]["r3"]["data_sugerida"] = data_limite.strftime("%Y-%m-%d")
            cronograma["revisoes"]["r3"]["ajustado"] = True
        
        return cronograma
    
    def verificar_status_revisao(
        self,
        data_sugerida: str,
        data_realizada: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verifica o status de uma revisão.
        
        Retorna:
        - "pendente": ainda não chegou a data
        - "disponivel": data chegou, mas não foi feita
        - "atrasada": passou da data e não foi feita
        - "concluida": revisão realizada
        """
        hoje = datetime.now()
        data_sug = datetime.strptime(data_sugerida, "%Y-%m-%d")
        
        if data_realizada:
            data_real = datetime.strptime(data_realizada, "%Y-%m-%d")
            dias_diferenca = (data_real - data_sug).days
            
            return {
                "status": "concluida",
                "data_realizada": data_realizada,
                "dias_diferenca": dias_diferenca,
                "no_prazo": abs(dias_diferenca) <= 7
            }
        
        dias_ate_sugerida = (data_sug - hoje).days
        
        if dias_ate_sugerida > 7:
            return {
                "status": "pendente",
                "dias_restantes": dias_ate_sugerida
            }
        elif dias_ate_sugerida >= -7:
            return {
                "status": "disponivel",
                "dias_restantes": dias_ate_sugerida,
                "urgencia": "normal" if dias_ate_sugerida >= 0 else "alta"
            }
        else:
            return {
                "status": "atrasada",
                "dias_atraso": abs(dias_ate_sugerida),
                "urgencia": "critica" if abs(dias_ate_sugerida) > 14 else "alta"
            }
    
    def calcular_proxima_acao(
        self,
        registro_tema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determina qual é a próxima ação para um tema baseado no registro atual.
        
        registro_tema deve conter:
        - data_teoria
        - r1: {data, questoes, acertos} ou None
        - r2: {data, questoes, acertos} ou None
        - r3: {data, questoes, acertos} ou None
        """
        if not registro_tema.get("data_teoria"):
            return {
                "acao": "ver_teoria",
                "descricao": "Assistir aula/estudar teoria"
            }
        
        data_teoria = datetime.strptime(registro_tema["data_teoria"], "%Y-%m-%d")
        cronograma = self.calcular_cronograma_tema(data_teoria)
        
        # Verificar cada revisão em ordem
        for rev_num, rev_key in enumerate(["r1", "r2", "r3"], 1):
            rev_dados = registro_tema.get(rev_key)
            
            if not rev_dados or not rev_dados.get("data"):
                # Revisão não realizada
                data_sugerida = cronograma["revisoes"][rev_key]["data_sugerida"]
                status = self.verificar_status_revisao(data_sugerida)
                
                return {
                    "acao": f"fazer_{rev_key}",
                    "revisao": rev_num,
                    "data_sugerida": data_sugerida,
                    "status": status["status"],
                    "percentual_questoes": cronograma["revisoes"][rev_key]["percentual_questoes"],
                    "descricao": f"Fazer {rev_num}ª revisão"
                }
        
        # Todas as revisões feitas - aguardar revisão final
        return {
            "acao": "aguardar_revisao_final",
            "descricao": "Revisões completas. Aguardar revisão final pré-prova."
        }
    
    def gerar_relatorio_pendencias(
        self,
        registro_estudo: Dict[str, Any],
        apenas_proximas: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Gera um relatório de todas as pendências de revisão.
        
        Args:
            registro_estudo: Dados do estudo
            apenas_proximas: Se True, filtra apenas revisões próximas (7 dias)
        
        Retorna lista ordenada por urgência.
        """
        pendencias = []
        
        for tema_key, tema_dados in registro_estudo.get("registro_temas", {}).items():
            proxima = self.calcular_proxima_acao(tema_dados)
            
            if proxima["acao"] not in ["aguardar_revisao_final", "ver_teoria"]:
                urgencia_score = 0
                incluir = True
                
                if proxima.get("status") == "atrasada":
                    urgencia_score = 100
                elif proxima.get("status") == "disponivel":
                    urgencia_score = 50
                elif proxima.get("status") == "pendente":
                    dias = proxima.get("dias_restantes", 30)
                    urgencia_score = max(0, 30 - dias)
                    
                    # Se apenas_proximas, ignorar revisões muito distantes
                    if apenas_proximas and dias > 7:
                        incluir = False
                
                if incluir:
                    pendencias.append({
                        "tema": tema_key,
                        "acao": proxima["acao"],
                        "descricao": proxima["descricao"],
                        "status": proxima.get("status", "pendente"),
                        "data_sugerida": proxima.get("data_sugerida"),
                        "urgencia_score": urgencia_score,
                        "dias_restantes": proxima.get("dias_restantes", 0)
                    })
        
        # Ordenar por data sugerida (mais próxima primeiro)
        def sort_key(x):
            if x.get("data_sugerida"):
                return x["data_sugerida"]
            return "9999-99-99"
        
        pendencias.sort(key=sort_key)
        
        return pendencias


def calcular_datas_revisao(data_teoria: str, tema: str = None) -> Dict[str, Any]:
    """
    Função de conveniência para calcular datas de revisão.
    """
    calc = CalculadoraRevisoes()
    data = datetime.strptime(data_teoria, "%Y-%m-%d")
    return calc.calcular_cronograma_tema(data, tema)


def obter_proxima_acao(registro_tema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Função de conveniência para obter próxima ação de um tema.
    """
    calc = CalculadoraRevisoes()
    return calc.calcular_proxima_acao(registro_tema)

