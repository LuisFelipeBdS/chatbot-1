"""
Priorizador ENAMED - High-Yield / Low-Yield

Classifica e prioriza temas baseado nos pesos estratégicos do ENAMED.
"""

from typing import Dict, Any, List, Tuple
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.helpers import carregar_pesos, carregar_temas, carregar_estudo


class PriorizadorENAMED:
    """
    Prioriza temas baseado na estratégia ENAMED.
    
    Classifica temas em:
    - High-Yield: Temas com alta probabilidade de cobrança (prioridade máxima)
    - Normal: Temas regulares
    - Low-Yield: Temas de baixa cobrança (podem ser depriorizados)
    """
    
    def __init__(self):
        self.pesos = carregar_pesos()
        self.temas = carregar_temas()
        self.estudo = carregar_estudo()
    
    def classificar_tema(self, tema: str, grande_area: str) -> Dict[str, Any]:
        """
        Classifica um tema em High-Yield, Normal ou Low-Yield.
        """
        # Verificar High-Yield
        high_yield_lista = self.pesos.get("temas_high_yield", {}).get(grande_area, [])
        
        for hy in high_yield_lista:
            if hy.lower() in tema.lower() or tema.lower() in hy.lower():
                return {
                    "classificacao": "high_yield",
                    "cor": "#00CC00",  # Verde
                    "icone": "🔥",
                    "multiplicador": self.pesos["multiplicadores"]["high_yield"],
                    "descricao": "Tema com alta probabilidade de cobrança no ENAMED"
                }
        
        # Verificar Low-Yield
        low_yield_lista = self.pesos.get("temas_low_yield", [])
        
        for ly in low_yield_lista:
            if ly.lower() in tema.lower():
                return {
                    "classificacao": "low_yield",
                    "cor": "#999999",  # Cinza
                    "icone": "📉",
                    "multiplicador": self.pesos["multiplicadores"]["low_yield"],
                    "descricao": "Tema com baixa probabilidade de cobrança - pode deprioritizar"
                }
        
        # Normal
        return {
            "classificacao": "normal",
            "cor": "#FFCC00",  # Amarelo
            "icone": "📖",
            "multiplicador": self.pesos["multiplicadores"]["normal"],
            "descricao": "Tema regular"
        }
    
    def listar_high_yield_por_area(self, grande_area: str) -> List[str]:
        """
        Lista todos os temas High-Yield de uma grande área.
        """
        return self.pesos.get("temas_high_yield", {}).get(grande_area, [])
    
    def listar_todos_high_yield(self) -> Dict[str, List[str]]:
        """
        Lista todos os temas High-Yield organizados por área.
        """
        return self.pesos.get("temas_high_yield", {})
    
    def calcular_cobertura_high_yield(self) -> Dict[str, Any]:
        """
        Calcula a cobertura de temas High-Yield no estudo atual.
        
        Retorna estatísticas de quantos temas HY foram revisados.
        """
        registro = self.estudo.get("registro_temas", {})
        
        resultado = {
            "por_area": {},
            "total": {
                "high_yield_total": 0,
                "high_yield_revisados": 0,
                "percentual_cobertura": 0
            }
        }
        
        for area, temas_hy in self.pesos.get("temas_high_yield", {}).items():
            revisados = 0
            
            for tema_hy in temas_hy:
                # Verificar se existe no registro
                for tema_key, dados in registro.items():
                    if tema_hy.lower() in tema_key.lower():
                        if dados.get("r1") or dados.get("r2") or dados.get("r3"):
                            revisados += 1
                            break
            
            total = len(temas_hy)
            percentual = (revisados / total * 100) if total > 0 else 0
            
            resultado["por_area"][area] = {
                "total": total,
                "revisados": revisados,
                "percentual": round(percentual, 1)
            }
            
            resultado["total"]["high_yield_total"] += total
            resultado["total"]["high_yield_revisados"] += revisados
        
        if resultado["total"]["high_yield_total"] > 0:
            resultado["total"]["percentual_cobertura"] = round(
                resultado["total"]["high_yield_revisados"] / 
                resultado["total"]["high_yield_total"] * 100, 1
            )
        
        return resultado
    
    def obter_high_yield_pendentes(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de temas High-Yield que ainda não foram revisados.
        """
        registro = self.estudo.get("registro_temas", {})
        pendentes = []
        
        for area, temas_hy in self.pesos.get("temas_high_yield", {}).items():
            for tema_hy in temas_hy:
                revisado = False
                
                for tema_key, dados in registro.items():
                    if tema_hy.lower() in tema_key.lower():
                        if dados.get("r1") or dados.get("r2") or dados.get("r3"):
                            revisado = True
                            break
                
                if not revisado:
                    pendentes.append({
                        "tema": tema_hy,
                        "grande_area": area,
                        "peso_area": self.pesos["pesos_areas"].get(area, 0),
                        "urgencia": "alta"
                    })
        
        # Ordenar por peso da área (mais importante primeiro)
        pendentes.sort(key=lambda x: x["peso_area"], reverse=True)
        
        return pendentes
    
    def gerar_relatorio_prioridades(self) -> Dict[str, Any]:
        """
        Gera um relatório completo de prioridades.
        """
        todas_areas = self.temas.get("grandes_areas", {})
        
        relatorio = {
            "areas": {},
            "resumo": {
                "total_temas": 0,
                "high_yield": 0,
                "normal": 0,
                "low_yield": 0
            }
        }
        
        for area, dados in todas_areas.items():
            area_info = {
                "peso_enamed": self.pesos["pesos_areas"].get(area, 0),
                "temas": {
                    "high_yield": [],
                    "normal": [],
                    "low_yield": []
                }
            }
            
            for tema in dados.get("temas", []):
                classificacao = self.classificar_tema(tema["nome"], area)
                area_info["temas"][classificacao["classificacao"]].append({
                    "nome": tema["nome"],
                    **classificacao
                })
                
                relatorio["resumo"][classificacao["classificacao"]] += 1
                relatorio["resumo"]["total_temas"] += 1
            
            relatorio["areas"][area] = area_info
        
        return relatorio
    
    def obter_alertas_high_yield(self) -> List[Dict[str, Any]]:
        """
        Gera alertas para temas High-Yield críticos não revisados.
        """
        pendentes = self.obter_high_yield_pendentes()
        alertas = []
        
        for p in pendentes[:5]:  # Top 5 mais críticos
            alertas.append({
                "tipo": "high_yield_pendente",
                "tema": p["tema"],
                "area": p["grande_area"],
                "mensagem": f"⚠️ Tema High-Yield '{p['tema']}' ainda não foi revisado!",
                "prioridade": "alta"
            })
        
        return alertas


def classificar_tema(tema: str, grande_area: str) -> str:
    """
    Função de conveniência para classificar um tema.
    """
    prio = PriorizadorENAMED()
    resultado = prio.classificar_tema(tema, grande_area)
    return resultado["classificacao"]


def obter_alertas() -> List[Dict[str, Any]]:
    """
    Função de conveniência para obter alertas High-Yield.
    """
    prio = PriorizadorENAMED()
    return prio.obter_alertas_high_yield()

