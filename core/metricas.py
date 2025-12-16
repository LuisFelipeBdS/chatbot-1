"""
Sistema de Métricas e Indicadores

Implementa:
- Setinhas de performance (5 níveis)
- Cores em degradê (25 tons)
- Bolinhas de prioridade
- Nota estimada
- Estatísticas gerais
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import (
    carregar_config, carregar_pesos, carregar_estudo,
    calcular_porcentagem_acerto
)
from utils.constants import (
    NIVEIS_PERFORMANCE, CORES_DEGRADÊ, NIVEIS_PRIORIDADE
)


class SistemaMetricas:
    """
    Sistema de métricas para acompanhamento de performance.
    """
    
    def __init__(self):
        self.config = carregar_config()
        self.pesos = carregar_pesos()
        self.estudo = carregar_estudo()
        self.nota_meta = self.config.get("metas", {}).get("nota_meta", 90)
    
    def calcular_setinha(self, porcentagem: float, meta_tema: float = None) -> Dict[str, Any]:
        """
        Calcula o nível de performance (setinha) baseado na porcentagem.
        
        A setinha é relativa à meta, não absoluta.
        """
        if meta_tema is None:
            meta_tema = self.nota_meta
        
        # Calcular diferença em relação à meta
        diferenca = porcentagem - meta_tema
        
        # Ajustar faixas baseado na meta
        if diferenca < -20:
            nivel = "muito_abaixo"
        elif diferenca < -10:
            nivel = "abaixo"
        elif diferenca < 5:
            nivel = "esperado"
        elif diferenca < 15:
            nivel = "acima"
        else:
            nivel = "muito_acima"
        
        dados_nivel = NIVEIS_PERFORMANCE[nivel]
        
        return {
            "nivel": nivel,
            "icone": dados_nivel["icone"],
            "cor": dados_nivel["cor"],
            "porcentagem": porcentagem,
            "diferenca_meta": diferenca,
            "descricao": self._descricao_setinha(nivel)
        }
    
    def _descricao_setinha(self, nivel: str) -> str:
        """Retorna descrição textual do nível."""
        descricoes = {
            "muito_abaixo": "Muito abaixo da expectativa - atenção redobrada",
            "abaixo": "Abaixo da expectativa - precisa melhorar",
            "esperado": "Dentro do esperado - continue assim",
            "acima": "Acima da expectativa - ótimo trabalho",
            "muito_acima": "Muito acima da expectativa - excelente!"
        }
        return descricoes.get(nivel, "")
    
    def obter_cor_performance(self, porcentagem: float) -> str:
        """
        Retorna a cor do degradê baseada na porcentagem.
        
        0-100% mapeado para índices 0-24 das cores.
        """
        indice = int(min(24, max(0, porcentagem / 100 * 24)))
        return CORES_DEGRADÊ[indice]
    
    def obter_cor_indice(self, porcentagem: float) -> int:
        """Retorna o índice da cor (0-24)."""
        return int(min(24, max(0, porcentagem / 100 * 24)))
    
    def calcular_bolinha_prioridade(self, score: float) -> Dict[str, Any]:
        """
        Calcula o símbolo de bolinha baseado no score de prioridade.
        
        score: 0.0 a 1.0
        """
        if score < 0.2:
            simbolo = NIVEIS_PRIORIDADE["vazia"]
            nivel = "vazia"
        elif score < 0.4:
            simbolo = NIVEIS_PRIORIDADE["quarto"]
            nivel = "quarto"
        elif score < 0.6:
            simbolo = NIVEIS_PRIORIDADE["metade"]
            nivel = "metade"
        elif score < 0.8:
            simbolo = NIVEIS_PRIORIDADE["tres_quartos"]
            nivel = "tres_quartos"
        else:
            simbolo = NIVEIS_PRIORIDADE["cheia"]
            nivel = "cheia"
        
        return {
            "simbolo": simbolo,
            "nivel": nivel,
            "score": score,
            "descricao": f"Prioridade: {int(score * 100)}%"
        }
    
    def calcular_nota_estimada(self) -> Dict[str, Any]:
        """
        Calcula a nota estimada baseada no desempenho atual.
        
        Considera:
        - Performance por grande área
        - Pesos do ENAMED
        - Cobertura de temas
        """
        registro = self.estudo.get("registro_temas", {})
        
        if not registro:
            # Usar diagnóstico inicial
            diag = self.config.get("diagnostico_inicial", {})
            valores = [v for v in diag.values() if v is not None]
            
            if valores:
                nota = sum(valores) / len(valores)
            else:
                nota = 50.0
            
            return {
                "nota_estimada": round(nota, 1),
                "confianca": "baixa",
                "fonte": "diagnostico_inicial",
                "detalhes": {}
            }
        
        # Calcular por área
        notas_area = {}
        pesos_areas = self.pesos.get("pesos_areas", {})
        
        for tema_key, dados in registro.items():
            # Identificar grande área (simplificado)
            grande_area = self._identificar_area(tema_key)
            
            if grande_area not in notas_area:
                notas_area[grande_area] = {"acertos": 0, "total": 0}
            
            # Somar todas as revisões
            for rev in ["r1", "r2", "r3"]:
                rev_dados = dados.get(rev, {})
                if rev_dados.get("questoes"):
                    notas_area[grande_area]["total"] += rev_dados["questoes"]
                    notas_area[grande_area]["acertos"] += rev_dados.get("acertos", 0)
        
        # Calcular nota ponderada
        nota_total = 0
        peso_total = 0
        detalhes = {}
        
        for area, stats in notas_area.items():
            if stats["total"] > 0:
                perc = (stats["acertos"] / stats["total"]) * 100
                peso = pesos_areas.get(area, 0.1)
                
                nota_total += perc * peso
                peso_total += peso
                
                detalhes[area] = {
                    "porcentagem": round(perc, 1),
                    "peso": peso,
                    "questoes": stats["total"]
                }
        
        nota_final = nota_total / peso_total if peso_total > 0 else 50.0
        
        # Determinar confiança
        total_questoes = sum(s["total"] for s in notas_area.values())
        if total_questoes < 500:
            confianca = "baixa"
        elif total_questoes < 2000:
            confianca = "media"
        else:
            confianca = "alta"
        
        return {
            "nota_estimada": round(nota_final, 1),
            "confianca": confianca,
            "fonte": "revisoes",
            "total_questoes": total_questoes,
            "detalhes": detalhes
        }
    
    def _identificar_area(self, tema_key: str) -> str:
        """Identifica a grande área de um tema (simplificado)."""
        # Mapeamento simplificado
        mapeamento = {
            "trauma": "Cirurgia Geral",
            "abdome": "Cirurgia Geral",
            "hérnia": "Cirurgia Geral",
            "diabetes": "Clinica Medica",
            "hipertensão": "Clinica Medica",
            "pneumonia": "Clinica Medica",
            "tuberculose": "Clinica Medica",
            "hiv": "Clinica Medica",
            "pré-natal": "Ginecologia e Obstetricia",
            "parto": "Ginecologia e Obstetricia",
            "eclâmpsia": "Ginecologia e Obstetricia",
            "puericultura": "Pediatria",
            "vacina": "Pediatria",
            "neonatal": "Pediatria",
            "sus": "Saude Coletiva",
            "ética": "Saude Coletiva",
            "óbito": "Saude Coletiva"
        }
        
        tema_lower = tema_key.lower()
        
        for palavra, area in mapeamento.items():
            if palavra in tema_lower:
                return area
        
        return "Clinica Medica"  # Default
    
    def calcular_media_questoes_semana(self) -> Dict[str, Any]:
        """
        Calcula a média de questões necessárias por semana para atingir a meta.
        """
        from utils.helpers import calcular_semanas_ate_prova
        
        data_prova = self.config.get("usuario", {}).get("data_prova_estimada", "2027-11-15")
        semanas = calcular_semanas_ate_prova(data_prova)
        
        stats = self.estudo.get("estatisticas_gerais", {})
        questoes_feitas = stats.get("total_questoes_feitas", 0)
        
        # Meta total (baseado na aluna referência)
        meta_total = 33500 if self.config.get("usuario", {}).get("ano_estudo", 1) == 1 else 16750
        questoes_restantes = max(0, meta_total - questoes_feitas)
        
        media_necessaria = questoes_restantes / semanas if semanas > 0 else 0
        
        return {
            "media_necessaria": round(media_necessaria, 0),
            "semanas_restantes": semanas,
            "questoes_feitas": questoes_feitas,
            "questoes_restantes": questoes_restantes,
            "meta_total": meta_total,
            "no_ritmo": media_necessaria <= self.config.get("metas", {}).get("questoes_semana_meta", 320)
        }
    
    def gerar_estatisticas_completas(self) -> Dict[str, Any]:
        """
        Gera estatísticas completas para o dashboard.
        """
        nota = self.calcular_nota_estimada()
        setinha = self.calcular_setinha(nota["nota_estimada"])
        media = self.calcular_media_questoes_semana()
        
        stats = self.estudo.get("estatisticas_gerais", {})
        
        return {
            "nota_estimada": nota,
            "setinha": setinha,
            "media_semanal": media,
            "questoes_total": stats.get("total_questoes_feitas", 0),
            "acertos_total": stats.get("total_acertos", 0),
            "taxa_acerto_geral": calcular_porcentagem_acerto(
                stats.get("total_acertos", 0),
                stats.get("total_questoes_feitas", 1)
            ),
            "simulados": stats.get("simulados_realizados", 0)
        }


def obter_estatisticas() -> Dict[str, Any]:
    """Função de conveniência para obter estatísticas."""
    metricas = SistemaMetricas()
    return metricas.gerar_estatisticas_completas()


def obter_nota_estimada() -> float:
    """Função de conveniência para obter nota estimada."""
    metricas = SistemaMetricas()
    return metricas.calcular_nota_estimada()["nota_estimada"]

