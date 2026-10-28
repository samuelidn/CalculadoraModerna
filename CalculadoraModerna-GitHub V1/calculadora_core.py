"""
Módulo Core da Calculadora Moderna
Contém a lógica matemática pura, o avaliador seguro baseado em AST,
o gerenciador de histórico com persistência em JSON e o gerenciador de sons.
"""

import ast
import json
import math
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


# =============================================================================
# 1. Avaliador Matemático Seguro (AST-based)
# =============================================================================

class MathEvaluationError(Exception):
    """Exceção customizada para erros matemáticos compreensíveis pelo usuário."""
    pass


class SafeMathEvaluator:
    """
    Avaliador de expressões matemáticas seguro usando a árvore sintática abstrata (AST) do Python.
    Não utiliza eval() irrestrito, impedindo execução de código arbitrário.
    Suporta precedência matemática padrão, parênteses, funções científicas e modo DEG/RAD.
    """

    def __init__(self, angle_mode: str = "DEG"):
        # "DEG" (graus) ou "RAD" (radianos)
        self.angle_mode = angle_mode.upper()

    def set_angle_mode(self, mode: str):
        mode_upper = mode.upper()
        if mode_upper in ("DEG", "RAD"):
            self.angle_mode = mode_upper
        else:
            raise ValueError("Modo de ângulo deve ser 'DEG' ou 'RAD'")

    def toggle_angle_mode(self) -> str:
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
        return self.angle_mode

    # Funções trigonométricas com suporte ao modo DEG/RAD
    def _sin(self, x: float) -> float:
        val = math.radians(x) if self.angle_mode == "DEG" else x
        res = math.sin(val)
        return 0.0 if abs(res) < 1e-15 else res

    def _cos(self, x: float) -> float:
        val = math.radians(x) if self.angle_mode == "DEG" else x
        res = math.cos(val)
        return 0.0 if abs(res) < 1e-15 else res

    def _tan(self, x: float) -> float:
        val = math.radians(x) if self.angle_mode == "DEG" else x
        cos_val = math.cos(val)
        if abs(cos_val) < 1e-15:
            raise MathEvaluationError("Tangente indefinida para este ângulo")
        res = math.tan(val)
        return 0.0 if abs(res) < 1e-15 else res

    def _asin(self, x: float) -> float:
        if not (-1.0 <= x <= 1.0):
            raise MathEvaluationError("Domínio do arco-seno deve estar entre -1 e 1")
        res = math.asin(x)
        return math.degrees(res) if self.angle_mode == "DEG" else res

    def _acos(self, x: float) -> float:
        if not (-1.0 <= x <= 1.0):
            raise MathEvaluationError("Domínio do arco-cosseno deve estar entre -1 e 1")
        res = math.acos(x)
        return math.degrees(res) if self.angle_mode == "DEG" else res

    def _atan(self, x: float) -> float:
        res = math.atan(x)
        return math.degrees(res) if self.angle_mode == "DEG" else res

    def _sqrt(self, x: float) -> float:
        if x < 0:
            raise MathEvaluationError("Raiz quadrada de número negativo")
        return math.sqrt(x)

    def _log10(self, x: float) -> float:
        if x <= 0:
            raise MathEvaluationError("Logaritmo definido apenas para valores maiores que zero")
        return math.log10(x)

    def _ln(self, x: float) -> float:
        if x <= 0:
            raise MathEvaluationError("Logaritmo natural definido apenas para valores maiores que zero")
        return math.log(x)

    def _factorial(self, x: Union[int, float]) -> int:
        if isinstance(x, float):
            if not x.is_integer():
                raise MathEvaluationError("Fatorial definido apenas para inteiros não-negativos")
        if x < 0:
            raise MathEvaluationError("Fatorial definido apenas para inteiros não-negativos")
        if x > 170:
            raise MathEvaluationError("Valor muito grande para cálculo de fatorial")
        return math.factorial(int(x))

    def _eval_node(self, node: ast.AST) -> Union[int, float]:
        """Avalia recursivamente nós permitidos da AST."""
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise MathEvaluationError("Constante não numérica não permitida")

        # Variáveis permitidas: pi e e
        if isinstance(node, ast.Name):
            if node.id in ("pi", "PI", "π"):
                return math.pi
            if node.id in ("e", "E"):
                return math.e
            raise MathEvaluationError(f"Símbolo não reconhecido: '{node.id}'")

        # Operadores unários (+x, -x)
        if isinstance(node, ast.UnaryOp):
            val = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +val
            if isinstance(node.op, ast.USub):
                return -val
            raise MathEvaluationError("Operador unário não suportado")

        # Operadores binários (+, -, *, /, %, ^, **)
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)

            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise MathEvaluationError("Divisão por zero")
                return left / right
            if isinstance(node.op, ast.Mod):
                if right == 0:
                    raise MathEvaluationError("Divisão por zero em módulo")
                return left % right
            if isinstance(node.op, (ast.Pow, ast.BitXor)):
                # Suporta tanto ^ quanto ** para potência
                try:
                    res = left ** right
                    if isinstance(res, complex):
                        raise MathEvaluationError("Resultado complexo não suportado")
                    return res
                except OverflowError:
                    raise MathEvaluationError("Resultado de potenciação muito grande")

            raise MathEvaluationError("Operação binária não suportada")

        # Funções matemáticas autorizadas
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise MathEvaluationError("Chamada de função inválida")

            func_name = node.func.id.lower()
            args = [self._eval_node(arg) for arg in node.args]

            allowed_functions = {
                "sqrt": (self._sqrt, 1),
                "raiz": (self._sqrt, 1),
                "sin": (self._sin, 1),
                "sen": (self._sin, 1),
                "cos": (self._cos, 1),
                "tan": (self._tan, 1),
                "tg": (self._tan, 1),
                "asin": (self._asin, 1),
                "arcsen": (self._asin, 1),
                "acos": (self._acos, 1),
                "arccos": (self._acos, 1),
                "atan": (self._atan, 1),
                "arctg": (self._atan, 1),
                "log": (self._log10, 1),
                "log10": (self._log10, 1),
                "ln": (self._ln, 1),
                "fact": (self._factorial, 1),
                "fat": (self._factorial, 1),
                "abs": (abs, 1),
            }

            if func_name not in allowed_functions:
                raise MathEvaluationError(f"Função matemática não permitida: '{func_name}'")

            fn, expected_args = allowed_functions[func_name]
            if len(args) != expected_args:
                raise MathEvaluationError(f"A função '{func_name}' espera {expected_args} argumento(s)")

            return fn(args[0])

        raise MathEvaluationError("Expressão contém elementos não permitidos")

    def evaluate(self, expr: str) -> float:
        """
        Avalia com segurança uma expressão matemática em string.
        Trata símbolos amigáveis como ×, ÷, π, √, ^.
        """
        if not expr or not expr.strip():
            return 0.0

        sanitized = expr.strip()
        # Normalização de símbolos
        sanitized = sanitized.replace("×", "*").replace("÷", "/")
        sanitized = sanitized.replace("π", "pi")
        sanitized = sanitized.replace("√", "sqrt")
        sanitized = sanitized.replace("²", "^2").replace("³", "^3")
        sanitized = sanitized.replace(",", ".")

        # Suporte amigável para fatorial no formato "5!" -> "fact(5)"
        # e porcentagem simples "20%" -> "(20/100)"
        import re
        # Tratamento de porcentagens independentes (ex: 50% ou 200 * 10%, mas não 10 % 3 que é módulo)
        sanitized = re.sub(r'(\d+(?:\.\d+)?)\s*%(?!\s*\d)', r'(\1/100)', sanitized)

        # Tratamento de n! para fact(n)
        sanitized = re.sub(r'(\d+(?:\.\d+)?)\s*!', r'fact(\1)', sanitized)

        try:
            tree = ast.parse(sanitized, mode="eval")
        except SyntaxError:
            raise MathEvaluationError("Erro de sintaxe na expressão")

        result = self._eval_node(tree)
        if math.isnan(result) or math.isinf(result):
            raise MathEvaluationError("Resultado numérico inválido ou infinito")
        return float(result)


# =============================================================================
# 2. Formatação Numérica Limpa
# =============================================================================

def format_number(val: Union[int, float]) -> str:
    """
    Formata números evitando artefatos de ponto flutuante (ex: 0.30000000000000004 -> 0.3).
    Remove o .0 quando o número é estritamente inteiro.
    """
    if isinstance(val, (int, float)):
        if math.isnan(val) or math.isinf(val):
            return "Erro"

        # Se for muito próximo de um inteiro
        if abs(val - round(val)) < 1e-11:
            return str(int(round(val)))

        # Limitação de precisão para evitar artefatos de floating point
        formatted = f"{val:.11g}"
        if "." in formatted:
            formatted = formatted.rstrip("0").rstrip(".")
        return formatted
    return str(val)


# =============================================================================
# 3. Gerenciador de Histórico com Persistência em JSON
# =============================================================================

class HistoryManager:
    """
    Gerencia estritamente os 5 cálculos mais recentes.
    Persiste localmente em %APPDATA%/CalculadoraModerna/historico.json no Windows
    ou na pasta de configuração do usuário no Linux/Mac.
    """
    MAX_ITEMS = 5

    def __init__(self, custom_path: Optional[Path] = None):
        self.file_path = custom_path or self._get_default_history_path()
        self.history: List[Dict[str, Any]] = []
        self.load_history()

    @staticmethod
    def _get_default_history_path() -> Path:
        """Determina o caminho seguro de persistência por sistema operacional."""
        if sys.platform == "win32":
            appdata = os.environ.get("APPDATA")
            base_dir = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        else:
            xdg_config = os.environ.get("XDG_CONFIG_HOME")
            base_dir = Path(xdg_config) if xdg_config else Path.home() / ".config"

        folder = base_dir / "CalculadoraModerna"
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Fallback para diretório pessoal caso não tenha permissão
            folder = Path.home() / ".CalculadoraModerna"
            folder.mkdir(parents=True, exist_ok=True)

        return folder / "historico.json"

    def load_history(self) -> List[Dict[str, Any]]:
        """Carrega o histórico salvo em arquivo JSON. Tolera falhas sem travar."""
        if not self.file_path.exists():
            self.history = []
            return self.history

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    # Garante apenas os 5 mais recentes
                    valid_items = []
                    for item in data[:self.MAX_ITEMS]:
                        if isinstance(item, dict) and "expression" in item and "result" in item:
                            valid_items.append({
                                "expression": str(item["expression"]),
                                "result": str(item["result"]),
                                "timestamp": item.get("timestamp", datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
                            })
                    self.history = valid_items
                else:
                    self.history = []
        except Exception:
            # Arquivo corrompido ou inacessível: não trava o app
            self.history = []

        return self.history

    def save_history(self):
        """Salva a lista dos 5 últimos cálculos em arquivo JSON."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.history[:self.MAX_ITEMS], f, ensure_ascii=False, indent=2)
        except Exception:
            # Falha de gravação não deve fechar o aplicativo
            pass

    def add_entry(self, expression: str, result: str) -> Dict[str, Any]:
        """Adiciona um cálculo e mantém estritamente os 5 mais recentes."""
        entry = {
            "expression": expression.strip(),
            "result": result.strip(),
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }
        self.history.insert(0, entry)
        if len(self.history) > self.MAX_ITEMS:
            self.history = self.history[:self.MAX_ITEMS]

        self.save_history()
        return entry

    def clear(self):
        """Limpa o histórico e atualiza a persistência."""
        self.history = []
        self.save_history()


# =============================================================================
# 4. Gerenciador de Sons Programáticos Não-Bloqueantes
# =============================================================================

class SoundManager:
    """
    Gera sons de feedback audível curtos e discretos programaticamente.
    Executa em threads secundárias daemon para não atrasar a interface gráfica.
    Possui opção de ativar/desativar e fallback para ambientes sem winsound.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled

    def _play_tone(self, frequency: int, duration_ms: int):
        if not self.enabled:
            return

        def tone_worker():
            try:
                if sys.platform == "win32":
                    import winsound
                    winsound.Beep(frequency, duration_ms)
                else:
                    # Em Linux ou Mac, tentativa de bell ou ignorar silenciosamente
                    pass
            except Exception:
                pass

        threading.Thread(target=tone_worker, daemon=True).start()

    def play_digit(self):
        """Som discreto e curto para clique em números."""
        self._play_tone(frequency=580, duration_ms=25)

    def play_operator(self):
        """Som para seleção de operadores matemáticos."""
        self._play_tone(frequency=720, duration_ms=35)

    def play_equals(self):
        """Som suave de confirmação de cálculo."""
        self._play_tone(frequency=880, duration_ms=50)

    def play_error(self):
        """Som de alerta para erro matemático."""
        self._play_tone(frequency=320, duration_ms=80)
