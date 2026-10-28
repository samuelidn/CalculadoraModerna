/**
 * Python standalone calculator code with CustomTkinter & Tkinter fallback.
 * Version 2.0 - Scientific & Basic with AST safe evaluation and JSON persistence.
 */

export const PYTHON_CALCULATOR_CORE_CODE = `"""
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
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


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
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise MathEvaluationError("Constante não numérica não permitida")

        if isinstance(node, ast.Name):
            if node.id in ("pi", "PI", "π"):
                return math.pi
            if node.id in ("e", "E"):
                return math.e
            raise MathEvaluationError(f"Símbolo não reconhecido: '{node.id}'")

        if isinstance(node, ast.UnaryOp):
            val = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +val
            if isinstance(node.op, ast.USub):
                return -val
            raise MathEvaluationError("Operador unário não suportado")

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
                try:
                    res = left ** right
                    if isinstance(res, complex):
                        raise MathEvaluationError("Resultado complexo não suportado")
                    return res
                except OverflowError:
                    raise MathEvaluationError("Resultado de potenciação muito grande")

            raise MathEvaluationError("Operação binária não suportada")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise MathEvaluationError("Chamada de função inválida")

            func_name = node.func.id.lower()
            args = [self._eval_node(arg) for arg in node.args]

            allowed_functions = {
                "sqrt": (self._sqrt, 1),
                "sin": (self._sin, 1),
                "cos": (self._cos, 1),
                "tan": (self._tan, 1),
                "asin": (self._asin, 1),
                "acos": (self._acos, 1),
                "atan": (self._atan, 1),
                "log": (self._log10, 1),
                "log10": (self._log10, 1),
                "ln": (self._ln, 1),
                "fact": (self._factorial, 1),
                "abs": (abs, 1),
            }

            if func_name not in allowed_functions:
                raise MathEvaluationError(f"Função não permitida: '{func_name}'")

            fn, expected_args = allowed_functions[func_name]
            if len(args) != expected_args:
                raise MathEvaluationError(f"A função '{func_name}' espera {expected_args} argumento(s)")

            return fn(args[0])

        raise MathEvaluationError("Expressão contém elementos não permitidos")

    def evaluate(self, expr: str) -> float:
        if not expr or not expr.strip():
            return 0.0

        sanitized = expr.strip()
        sanitized = sanitized.replace("×", "*").replace("÷", "/")
        sanitized = sanitized.replace("π", "pi")
        sanitized = sanitized.replace("√", "sqrt")
        sanitized = sanitized.replace("²", "^2").replace("³", "^3")
        sanitized = sanitized.replace(",", ".")

        import re
        sanitized = re.sub(r'(\\d+(?:\\.\\d+)?)\\s*%(?!\\s*\\d)', r'(\\1/100)', sanitized)
        sanitized = re.sub(r'(\\d+(?:\\.\\d+)?)\\s*!', r'fact(\\1)', sanitized)

        try:
            tree = ast.parse(sanitized, mode="eval")
        except SyntaxError:
            raise MathEvaluationError("Erro de sintaxe na expressão")

        result = self._eval_node(tree)
        if math.isnan(result) or math.isinf(result):
            raise MathEvaluationError("Resultado numérico inválido")
        return float(result)


def format_number(val: Union[int, float]) -> str:
    if isinstance(val, (int, float)):
        if math.isnan(val) or math.isinf(val):
            return "Erro"
        if abs(val - round(val)) < 1e-11:
            return str(int(round(val)))
        formatted = f"{val:.11g}"
        if "." in formatted:
            formatted = formatted.rstrip("0").rstrip(".")
        return formatted
    return str(val)


class HistoryManager:
    MAX_ITEMS = 5

    def __init__(self, custom_path: Optional[Path] = None):
        self.file_path = custom_path or self._get_default_history_path()
        self.history: List[Dict[str, Any]] = []
        self.load_history()

    @staticmethod
    def _get_default_history_path() -> Path:
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
            folder = Path.home() / ".CalculadoraModerna"
            folder.mkdir(parents=True, exist_ok=True)

        return folder / "historico.json"

    def load_history(self) -> List[Dict[str, Any]]:
        if not self.file_path.exists():
            self.history = []
            return self.history

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
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
            self.history = []

        return self.history

    def save_history(self):
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.history[:self.MAX_ITEMS], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add_entry(self, expression: str, result: str) -> Dict[str, Any]:
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
        self.history = []
        self.save_history()


class SoundManager:
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
            except Exception:
                pass

        threading.Thread(target=tone_worker, daemon=True).start()

    def play_digit(self):
        self._play_tone(frequency=580, duration_ms=25)

    def play_operator(self):
        self._play_tone(frequency=720, duration_ms=35)

    def play_equals(self):
        self._play_tone(frequency=880, duration_ms=50)

    def play_error(self):
        self._play_tone(frequency=320, duration_ms=80)
`;

export const PYTHON_CALCULATOR_CODE = `"""
Calculadora Moderna em Python (Desktop)
Versão 2.0 - Científica & Básica

- Fundo preto profundo (#0A0A0E)
- Painéis em cinza escuro (#14161D / #1C1E26)
- Tipografia branca minimalista
- Laranja vibrante (#FF6B00) nas operações e ações principais
- Abertura maximizada automática e tela cheia com F11 / Esc
- Abas: Básica e Científica (sin, cos, tan, asin, acos, atan, ln, log, √, ^, x², n!, π, e, DEG/RAD)
- Avaliador seguro baseado em AST (zero eval inseguro)
- Histórico dos 5 últimos cálculos com data/hora e clique para reutilizar
- Persistência em JSON (%APPDATA%/CalculadoraModerna/historico.json)
- Sons programáticos e não-bloqueantes
"""

import math
import os
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

# Fallback automático: importa ou embute o core
try:
    from calculadora_core import (
        HistoryManager,
        MathEvaluationError,
        SafeMathEvaluator,
        SoundManager,
        format_number,
    )
except ImportError:
    pass

try:
    import customtkinter as ctk
    HAS_CUSTOMTKINTER = True
except ImportError:
    HAS_CUSTOMTKINTER = False


class CalculadoraModernaApp:
    def __init__(self):
        self.evaluator = SafeMathEvaluator(angle_mode="DEG")
        self.history_manager = HistoryManager()
        self.sound_manager = SoundManager(enabled=True)

        self.expressao_atual = "0"
        self.expressao_secundaria = ""
        self.aguardando_novo_numero = False
        self.is_fullscreen = False

        if HAS_CUSTOMTKINTER:
            self._init_customtkinter_app()
        else:
            self._init_standard_tkinter_app()

    def _init_customtkinter_app(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.root.title("Calculadora Moderna")
        self.root.configure(fg_color="#0A0A0E")
        self.root.geometry("1024x720")
        self.root.minsize(820, 620)

        self._aplicar_abertura_maximizada()

        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Escape>", self._on_escape_key)
        self.root.bind("<Key>", self._tratar_teclado)

        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(0, weight=1)

        calc_container = ctk.CTkFrame(self.root, fg_color="#121319", corner_radius=24)
        calc_container.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        calc_container.grid_columnconfigure(0, weight=1)
        calc_container.grid_rowconfigure(2, weight=1)

        top_bar = ctk.CTkFrame(calc_container, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 6))

        titulo = ctk.CTkLabel(
            top_bar,
            text="CALCULADORA MODERNA",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#A0A2B0"
        )
        titulo.pack(side="left")

        self.btn_som = ctk.CTkButton(
            top_bar,
            text="🔊 Som: Ativado",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#1E2029",
            hover_color="#2A2D3A",
            text_color="#FF6B00",
            width=110,
            height=28,
            corner_radius=10,
            command=self._toggle_som
        )
        self.btn_som.pack(side="right", padx=(8, 0))

        self.btn_copiar = ctk.CTkButton(
            top_bar,
            text="📋 Copiar",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#1E2029",
            hover_color="#2A2D3A",
            text_color="#FFFFFF",
            width=85,
            height=28,
            corner_radius=10,
            command=self.copiar_resultado
        )
        self.btn_copiar.pack(side="right")

        display_frame = ctk.CTkFrame(calc_container, fg_color="#181A22", corner_radius=18)
        display_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(6, 12))
        display_frame.grid_columnconfigure(0, weight=1)

        self.lbl_secundaria = ctk.CTkLabel(
            display_frame,
            text="",
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color="#7A7D8E",
            anchor="e"
        )
        self.lbl_secundaria.grid(row=0, column=0, sticky="ew", padx=20, pady=(12, 0))

        self.lbl_display = ctk.CTkLabel(
            display_frame,
            text="0",
            font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
            text_color="#FFFFFF",
            anchor="e"
        )
        self.lbl_display.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 14))

        self.tabview = ctk.CTkTabview(
            calc_container,
            fg_color="#14151C",
            segmented_button_fg_color="#1E2029",
            segmented_button_selected_color="#FF6B00",
            segmented_button_selected_hover_color="#E05E00",
            segmented_button_unselected_hover_color="#262835",
            corner_radius=18
        )
        self.tabview.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 16))

        tab_basica = self.tabview.add("Básica")
        tab_cientifica = self.tabview.add("Científica")

        self._montar_teclado_basico_ctk(tab_basica)
        self._montar_teclado_cientifico_ctk(tab_cientifica)
        self._montar_painel_historico_ctk()

        self.root.mainloop()

    def _montar_teclado_basico_ctk(self, parent):
        for r in range(5):
            parent.grid_rowconfigure(r, weight=1)
        for c in range(4):
            parent.grid_columnconfigure(c, weight=1)

        botoes = [
            ("C", 0, 0, "fn", self.limpar_tudo),
            ("±", 0, 1, "fn", self.alternar_sinal),
            ("%", 0, 2, "fn", self.inserir_porcentagem),
            ("÷", 0, 3, "op", lambda: self.inserir_operador(" ÷ ")),

            ("7", 1, 0, "num", lambda: self.inserir_texto("7")),
            ("8", 1, 1, "num", lambda: self.inserir_texto("8")),
            ("9", 1, 2, "num", lambda: self.inserir_texto("9")),
            ("×", 1, 3, "op", lambda: self.inserir_operador(" × ")),

            ("4", 2, 0, "num", lambda: self.inserir_texto("4")),
            ("5", 2, 1, "num", lambda: self.inserir_texto("5")),
            ("6", 2, 2, "num", lambda: self.inserir_texto("6")),
            ("-", 2, 3, "op", lambda: self.inserir_operador(" - ")),

            ("1", 3, 0, "num", lambda: self.inserir_texto("1")),
            ("2", 3, 1, "num", lambda: self.inserir_texto("2")),
            ("3", 3, 2, "num", lambda: self.inserir_texto("3")),
            ("+", 3, 3, "op", lambda: self.inserir_operador(" + ")),

            ("0", 4, 0, "num", lambda: self.inserir_texto("0")),
            (".", 4, 1, "num", self.inserir_ponto),
            ("⌫", 4, 2, "fn", self.apagar_ultimo),
            ("=", 4, 3, "eq", self.calcular),
        ]

        for texto, r, c, tipo, cmd in botoes:
            fg, hover, txt_cor = self._obter_cores_botao(tipo)
            btn = ctk.CTkButton(
                parent,
                text=texto,
                font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                fg_color=fg,
                hover_color=hover,
                text_color=txt_cor,
                corner_radius=14,
                command=cmd
            )
            btn.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

    def _montar_teclado_cientifico_ctk(self, parent):
        for r in range(6):
            parent.grid_rowconfigure(r, weight=1)
        for c in range(5):
            parent.grid_columnconfigure(c, weight=1)

        botoes = [
            (self.evaluator.angle_mode, 0, 0, "deg", self._toggle_deg_rad),
            ("(", 0, 1, "fn", lambda: self.inserir_texto("(")),
            (")", 0, 2, "fn", lambda: self.inserir_texto(")")),
            ("√", 0, 3, "fn", lambda: self.inserir_funcao("sqrt")),
            ("C", 0, 4, "fn", self.limpar_tudo),

            ("sin", 1, 0, "fn", lambda: self.inserir_funcao("sin")),
            ("cos", 1, 1, "fn", lambda: self.inserir_funcao("cos")),
            ("tan", 1, 2, "fn", lambda: self.inserir_funcao("tan")),
            ("x²", 1, 3, "fn", lambda: self.inserir_texto("²")),
            ("÷", 1, 4, "op", lambda: self.inserir_operador(" ÷ ")),

            ("asin", 2, 0, "fn", lambda: self.inserir_funcao("asin")),
            ("acos", 2, 1, "fn", lambda: self.inserir_funcao("acos")),
            ("atan", 2, 2, "fn", lambda: self.inserir_funcao("atan")),
            ("x^y", 2, 3, "fn", lambda: self.inserir_operador(" ^ ")),
            ("×", 2, 4, "op", lambda: self.inserir_operador(" × ")),

            ("ln", 3, 0, "fn", lambda: self.inserir_funcao("ln")),
            ("log", 3, 1, "fn", lambda: self.inserir_funcao("log")),
            ("7", 3, 2, "num", lambda: self.inserir_texto("7")),
            ("8", 3, 3, "num", lambda: self.inserir_texto("8")),
            ("-", 3, 4, "op", lambda: self.inserir_operador(" - ")),

            ("π", 4, 0, "fn", lambda: self.inserir_texto("π")),
            ("e", 4, 1, "fn", lambda: self.inserir_texto("e")),
            ("4", 4, 2, "num", lambda: self.inserir_texto("4")),
            ("5", 4, 3, "num", lambda: self.inserir_texto("5")),
            ("+", 4, 4, "op", lambda: self.inserir_operador(" + ")),

            ("n!", 5, 0, "fn", lambda: self.inserir_texto("!")),
            ("9", 5, 1, "num", lambda: self.inserir_texto("9")),
            ("6", 5, 2, "num", lambda: self.inserir_texto("6")),
            ("1", 5, 3, "num", lambda: self.inserir_texto("1")),
            ("2", 5, 4, "num", lambda: self.inserir_texto("2")),
        ]

        self.btn_deg_rad = None
        for texto, r, c, tipo, cmd in botoes:
            fg, hover, txt_cor = self._obter_cores_botao(tipo)
            btn = ctk.CTkButton(
                parent,
                text=texto,
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                fg_color=fg,
                hover_color=hover,
                text_color=txt_cor,
                corner_radius=12,
                command=cmd
            )
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            if tipo == "deg":
                self.btn_deg_rad = btn

        row_extra = ctk.CTkFrame(parent, fg_color="transparent")
        row_extra.grid(row=6, column=0, columnspan=5, sticky="nsew", pady=(4, 0))
        for i in range(5):
            row_extra.grid_columnconfigure(i, weight=1)

        botoes_extra = [
            ("3", 0, "num", lambda: self.inserir_texto("3")),
            ("0", 1, "num", lambda: self.inserir_texto("0")),
            (".", 2, "num", self.inserir_ponto),
            ("⌫", 3, "fn", self.apagar_ultimo),
            ("=", 4, "eq", self.calcular),
        ]

        for texto, col, tipo, cmd in botoes_extra:
            fg, hover, txt_cor = self._obter_cores_botao(tipo)
            btn = ctk.CTkButton(
                row_extra,
                text=texto,
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                fg_color=fg,
                hover_color=hover,
                text_color=txt_cor,
                corner_radius=12,
                command=cmd
            )
            btn.grid(row=0, column=col, padx=3, pady=2, sticky="nsew")

    def _montar_painel_historico_ctk(self):
        hist_container = ctk.CTkFrame(self.root, fg_color="#121319", corner_radius=24)
        hist_container.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)
        hist_container.grid_columnconfigure(0, weight=1)
        hist_container.grid_rowconfigure(1, weight=1)

        hist_header = ctk.CTkFrame(hist_container, fg_color="transparent")
        hist_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 12))

        hist_titulo = ctk.CTkLabel(
            hist_header,
            text="HISTÓRICO (5 ÚLTIMOS)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#A0A2B0"
        )
        hist_titulo.pack(side="left")

        btn_limpar = ctk.CTkButton(
            hist_header,
            text="🗑 Limpar",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#242633",
            hover_color="#36394A",
            text_color="#F87171",
            width=80,
            height=26,
            corner_radius=10,
            command=self.confirmar_limpar_historico
        )
        btn_limpar.pack(side="right")

        self.scroll_historico = ctk.CTkScrollableFrame(
            hist_container,
            fg_color="transparent",
            corner_radius=14
        )
        self.scroll_historico.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.scroll_historico.grid_columnconfigure(0, weight=1)

        self._renderizar_historico_ctk()

    def _renderizar_historico_ctk(self):
        for widget in self.scroll_historico.winfo_children():
            widget.destroy()

        historico = self.history_manager.history
        if not historico:
            vazio = ctk.CTkLabel(
                self.scroll_historico,
                text="Nenhum cálculo registrado ainda.\\n\\nOs últimos 5 cálculos salvos\\naparecerão aqui.",
                font=ctk.CTkFont(size=12),
                text_color="#636674",
                justify="center"
            )
            vazio.pack(fill="both", expand=True, pady=40)
            return

        for idx, item in enumerate(historico):
            card = ctk.CTkFrame(self.scroll_historico, fg_color="#181A24", corner_radius=14)
            card.pack(fill="x", padx=4, pady=6)
            card.grid_columnconfigure(0, weight=1)

            top_card = ctk.CTkFrame(card, fg_color="transparent")
            top_card.pack(fill="x", padx=14, pady=(8, 2))

            lbl_time = ctk.CTkLabel(
                top_card,
                text=f"🕒 {item.get('timestamp', '')}",
                font=ctk.CTkFont(size=10),
                text_color="#7E8294"
            )
            lbl_time.pack(side="left")

            if idx == 0:
                badge = ctk.CTkLabel(
                    top_card,
                    text="RECENTE",
                    font=ctk.CTkFont(size=9, weight="bold"),
                    text_color="#FF6B00",
                    fg_color="#2B1F17",
                    corner_radius=6,
                    padx=6,
                    pady=1
                )
                badge.pack(side="right")

            lbl_expr = ctk.CTkLabel(
                card,
                text=item["expression"],
                font=ctk.CTkFont(family="Consolas", size=13),
                text_color="#9CA3AF",
                anchor="w"
            )
            lbl_expr.pack(fill="x", padx=14, pady=(2, 0))

            bot_card = ctk.CTkFrame(card, fg_color="transparent")
            bot_card.pack(fill="x", padx=14, pady=(2, 8))

            lbl_res = ctk.CTkLabel(
                bot_card,
                text=f"= {item['result']}",
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                text_color="#FFFFFF",
                anchor="w"
            )
            lbl_res.pack(side="left")

            resultado_val = item["result"]
            btn_usar = ctk.CTkButton(
                bot_card,
                text="Reutilizar ↗",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color="#FF6B00",
                hover_color="#E05E00",
                text_color="#FFFFFF",
                width=75,
                height=24,
                corner_radius=8,
                command=lambda val=resultado_val: self.reutilizar_resultado(val)
            )
            btn_usar.pack(side="right")

    def _aplicar_abertura_maximizada(self):
        try:
            self.root.state("zoomed")
        except Exception:
            try:
                self.root.attributes("-zoomed", True)
            except Exception:
                self.root.geometry("1100x750")

    def _toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def _on_escape_key(self, event=None):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)
        else:
            self.limpar_tudo()

    def _toggle_som(self):
        ativado = self.sound_manager.toggle()
        texto = "🔊 Som: Ativado" if ativado else "🔇 Som: Desativado"
        if HAS_CUSTOMTKINTER:
            self.btn_som.configure(text=texto, text_color="#FF6B00" if ativado else "#80828D")
        else:
            self.btn_som.config(text=texto, fg="#FF6B00" if ativado else "#80828D")

    def _toggle_deg_rad(self):
        novo_modo = self.evaluator.toggle_angle_mode()
        self.sound_manager.play_operator()
        if HAS_CUSTOMTKINTER and self.btn_deg_rad:
            self.btn_deg_rad.configure(text=novo_modo)

    def _obter_cores_botao(self, tipo: str):
        if tipo == "op":
            return "#FF6B00", "#EA580C", "#FFFFFF"
        if tipo == "eq":
            return "#FF6B00", "#E05300", "#FFFFFF"
        if tipo == "fn":
            return "#252834", "#353949", "#FF9A3C"
        if tipo == "deg":
            return "#282B38", "#383C4D", "#FF6B00"
        return "#1F212A", "#2B2E3A", "#FFFFFF"

    def _definir_display(self, texto: str):
        self.expressao_atual = str(texto)
        if HAS_CUSTOMTKINTER:
            self.lbl_display.configure(text=self.expressao_atual)

    def _definir_secundaria(self, texto: str):
        self.expressao_secundaria = str(texto)
        if HAS_CUSTOMTKINTER:
            self.lbl_secundaria.configure(text=self.expressao_secundaria)

    def inserir_texto(self, texto: str):
        self.sound_manager.play_digit()
        if self.aguardando_novo_numero or self.expressao_atual == "0" or "Erro" in self.expressao_atual:
            self._definir_display(texto)
            self.aguardando_novo_numero = False
        else:
            self._definir_display(self.expressao_atual + texto)

    def inserir_ponto(self):
        self.sound_manager.play_digit()
        if self.aguardando_novo_numero or "Erro" in self.expressao_atual:
            self._definir_display("0.")
            self.aguardando_novo_numero = False
            return
        if not self.expressao_atual.endswith("."):
            self._definir_display(self.expressao_atual + ".")

    def inserir_operador(self, op: str):
        self.sound_manager.play_operator()
        if "Erro" in self.expressao_atual:
            return
        self.aguardando_novo_numero = False
        self._definir_display(self.expressao_atual + op)

    def inserir_funcao(self, nome_func: str):
        self.sound_manager.play_operator()
        if self.expressao_atual == "0" or self.aguardando_novo_numero or "Erro" in self.expressao_atual:
            self._definir_display(f"{nome_func}(")
            self.aguardando_novo_numero = False
        else:
            self._definir_display(f"{self.expressao_atual}{nome_func}(")

    def inserir_porcentagem(self):
        self.sound_manager.play_operator()
        if "Erro" in self.expressao_atual:
            return
        self._definir_display(self.expressao_atual + "%")

    def alternar_sinal(self):
        self.sound_manager.play_operator()
        atual = self.expressao_atual.strip()
        if atual == "0" or "Erro" in atual:
            return
        if atual.startswith("-"):
            self._definir_display(atual[1:])
        else:
            self._definir_display("-" + atual)

    def apagar_ultimo(self):
        self.sound_manager.play_digit()
        atual = self.expressao_atual
        if "Erro" in atual or self.aguardando_novo_numero:
            self._definir_display("0")
            self.aguardando_novo_numero = False
            return

        if len(atual) <= 1 or (len(atual) == 2 and atual.startswith("-")):
            self._definir_display("0")
        else:
            if atual.endswith(" "):
                self._definir_display(atual.rstrip()[:-1].rstrip())
            else:
                self._definir_display(atual[:-1])

    def limpar_tudo(self):
        self.sound_manager.play_operator()
        self._definir_display("0")
        self._definir_secundaria("")
        self.aguardando_novo_numero = False

    def calcular(self):
        expr = self.expressao_atual.strip()
        if not expr or expr == "0" or "Erro" in expr:
            return

        try:
            res_num = self.evaluator.evaluate(expr)
            res_str = format_number(res_num)

            self.sound_manager.play_equals()
            self._definir_secundaria(f"{expr} =")
            self._definir_display(res_str)

            self.history_manager.add_entry(expr, res_str)
            if HAS_CUSTOMTKINTER:
                self._renderizar_historico_ctk()

            self.aguardando_novo_numero = True

        except MathEvaluationError as e:
            self.sound_manager.play_error()
            self._definir_secundaria(f"{expr} =")
            self._definir_display(f"Erro: {str(e)}")
            self.aguardando_novo_numero = True
        except Exception:
            self.sound_manager.play_error()
            self._definir_secundaria(f"{expr} =")
            self._definir_display("Erro: Expressão inválida")
            self.aguardando_novo_numero = True

    def reutilizar_resultado(self, valor: str):
        self.sound_manager.play_digit()
        self._definir_display(valor)
        self.aguardando_novo_numero = False

    def confirmar_limpar_historico(self):
        if not self.history_manager.history:
            return

        resposta = messagebox.askyesno(
            "Limpar Histórico",
            "Deseja realmente apagar todos os 5 cálculos do histórico?",
            parent=self.root
        )
        if resposta:
            self.history_manager.clear()
            if HAS_CUSTOMTKINTER:
                self._renderizar_historico_ctk()

    def copiar_resultado(self):
        resultado = self.expressao_atual
        if "Erro" in resultado:
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(resultado)

        if HAS_CUSTOMTKINTER:
            self.btn_copiar.configure(text="✓ Copiado!", text_color="#10B981")
            self.root.after(1600, lambda: self.btn_copiar.configure(text="📋 Copiar", text_color="#FFFFFF"))

    def _tratar_teclado(self, event):
        tecla = event.char
        keysym = event.keysym

        if tecla in "0123456789":
            self.inserir_texto(tecla)
        elif tecla == "+":
            self.inserir_operador(" + ")
        elif tecla == "-":
            self.inserir_operador(" - ")
        elif tecla in "*xX":
            self.inserir_operador(" × ")
        elif tecla == "/":
            self.inserir_operador(" ÷ ")
        elif tecla in ".,":
            self.inserir_ponto()
        elif tecla in "()":
            self.inserir_texto(tecla)
        elif tecla == "^":
            self.inserir_operador(" ^ ")
        elif tecla == "%":
            self.inserir_porcentagem()
        elif keysym in ("Return", "equal") or tecla == "=":
            self.calcular()
        elif keysym in ("BackSpace",):
            self.apagar_ultimo()
        elif keysym in ("Delete",) or tecla in ("c", "C"):
            self.limpar_tudo()


if __name__ == "__main__":
    CalculadoraModernaApp()
`;

export const INSTALL_INSTRUCTIONS_PT = [
  {
    step: '1. Pré-requisito',
    title: 'Python 3.8+ Instalado',
    description: 'Instale o Python em seu computador marcando a opção "Add Python to PATH" durante a instalação.',
    command: 'python --version',
  },
  {
    step: '2. Instalar biblioteca CustomTkinter',
    title: 'Visual moderno com cantos arredondados',
    description: 'Instala o pacote que ativa os cartões modernos, abas Básica e Científica e cantos arredondados:',
    command: 'pip install customtkinter',
  },
  {
    step: '3. Executar o aplicativo no Windows',
    title: 'Rodar direto no computador',
    description: 'Abra o CMD ou PowerShell na pasta onde estão os arquivos e execute:',
    command: 'python calculadora.py',
  },
  {
    step: '4. Gerar Executável .exe Portátil (PyInstaller)',
    title: 'Criar aplicativo instalável de 1 clique',
    description: 'Cria o executável CalculadoraModerna.exe que abre com 1 clique no Windows sem precisar de terminal:',
    command: 'pip install pyinstaller && pyinstaller --noconsole --onefile --name "CalculadoraModerna" calculadora.py',
  },
];
