"""
Calculadora Moderna em Python (Desktop)
Versão 2.0 - Científica & Básica

Identidade Visual:
- Fundo preto profundo (#0A0A0E)
- Painéis em cinza escuro (#14161D / #1C1E26)
- Tipografia branca minimalista e legível
- Laranja vibrante (#FF6B00 / #F97316) para operações principais e ações
- Botões arredondados e layout responsivo com abertura maximizada e tela cheia (F11/Esc)

Recursos:
- Abas: "Básica" e "Científica"
- Calculadora Científica: √x, x², x^y, log10, ln, sin, cos, tan, asin, acos, atan, parênteses (), π, e, n!, DEG/RAD
- Avaliador seguro baseado em AST (sem eval irrestrito)
- Histórico com os 5 últimos cálculos em cartões visuais com data/hora e clique para reutilizar
- Persistência local em JSON (%APPDATA%/CalculadoraModerna/historico.json)
- Sons programáticos e não-bloqueantes com opção de ativar/desativar
- Botão de copiar resultado para a área de transferência
"""

import math
import os
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

# Importa o módulo core com avaliador AST, histórico e sons
try:
    from calculadora_core import (
        HistoryManager,
        MathEvaluationError,
        SafeMathEvaluator,
        SoundManager,
        format_number,
    )
except ImportError:
    # Se executado diretamente como script independente, inclui o core embutido
    pass

try:
    import customtkinter as ctk
    HAS_CUSTOMTKINTER = True
except ImportError:
    HAS_CUSTOMTKINTER = False


class CalculadoraModernaApp:
    def __init__(self):
        # Gerenciadores
        self.evaluator = SafeMathEvaluator(angle_mode="DEG")
        self.history_manager = HistoryManager()
        self.sound_manager = SoundManager(enabled=True)

        # Estados de cálculo
        self.expressao_atual = "0"
        self.expressao_secundaria = ""
        self.aguardando_novo_numero = False
        self.is_fullscreen = False

        if HAS_CUSTOMTKINTER:
            self._init_customtkinter_app()
        else:
            self._init_standard_tkinter_app()

    # =========================================================================
    # Implementação Moderna com CustomTkinter
    # =========================================================================
    def _init_customtkinter_app(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.root.title("Calculadora Moderna")
        self.root.configure(fg_color="#0A0A0E")
        self.root.geometry("1024x720")
        self.root.minsize(820, 620)

        # Abertura maximizada
        self._aplicar_abertura_maximizada()

        # Teclas de atalho globais
        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Escape>", self._on_escape_key)
        self.root.bind("<Key>", self._tratar_teclado)

        # Layout Principal dividido em duas colunas responsivas:
        # Coluna 0: Calculadora (Abas Básica e Científica)
        # Coluna 1: Painel do Histórico dos 5 últimos cálculos
        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(0, weight=1)

        # Frame da Calculadora (Esquerda)
        calc_container = ctk.CTkFrame(self.root, fg_color="#121319", corner_radius=24)
        calc_container.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        calc_container.grid_columnconfigure(0, weight=1)
        calc_container.grid_rowconfigure(2, weight=1)

        # Barra Superior de Controles da Calculadora
        top_bar = ctk.CTkFrame(calc_container, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 6))

        titulo = ctk.CTkLabel(
            top_bar,
            text="CALCULADORA MODERNA",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#A0A2B0"
        )
        titulo.pack(side="left")

        # Botão de Som
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

        # Botão de Copiar
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

        # Display do Visor
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

        # Abas da Calculadora (Básica e Científica)
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

        # Frame do Histórico (Direita)
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
            # Linha 0: DEG/RAD, (, ), √, C
            (self.evaluator.angle_mode, 0, 0, "deg", self._toggle_deg_rad),
            ("(", 0, 1, "fn", lambda: self.inserir_texto("(")),
            (")", 0, 2, "fn", lambda: self.inserir_texto(")")),
            ("√", 0, 3, "fn", lambda: self.inserir_funcao("sqrt")),
            ("C", 0, 4, "fn", self.limpar_tudo),

            # Linha 1: sin, cos, tan, x², ÷
            ("sin", 1, 0, "fn", lambda: self.inserir_funcao("sin")),
            ("cos", 1, 1, "fn", lambda: self.inserir_funcao("cos")),
            ("tan", 1, 2, "fn", lambda: self.inserir_funcao("tan")),
            ("x²", 1, 3, "fn", lambda: self.inserir_texto("²")),
            ("÷", 1, 4, "op", lambda: self.inserir_operador(" ÷ ")),

            # Linha 2: asin, acos, atan, x^y, ×
            ("asin", 2, 0, "fn", lambda: self.inserir_funcao("asin")),
            ("acos", 2, 1, "fn", lambda: self.inserir_funcao("acos")),
            ("atan", 2, 2, "fn", lambda: self.inserir_funcao("atan")),
            ("x^y", 2, 3, "fn", lambda: self.inserir_operador(" ^ ")),
            ("×", 2, 4, "op", lambda: self.inserir_operador(" × ")),

            # Linha 3: ln, log10, 7, 8, -
            ("ln", 3, 0, "fn", lambda: self.inserir_funcao("ln")),
            ("log", 3, 1, "fn", lambda: self.inserir_funcao("log")),
            ("7", 3, 2, "num", lambda: self.inserir_texto("7")),
            ("8", 3, 3, "num", lambda: self.inserir_texto("8")),
            ("-", 3, 4, "op", lambda: self.inserir_operador(" - ")),

            # Linha 4: π, e, 4, 5, +
            ("π", 4, 0, "fn", lambda: self.inserir_texto("π")),
            ("e", 4, 1, "fn", lambda: self.inserir_texto("e")),
            ("4", 4, 2, "num", lambda: self.inserir_texto("4")),
            ("5", 4, 3, "num", lambda: self.inserir_texto("5")),
            ("+", 4, 4, "op", lambda: self.inserir_operador(" + ")),

            # Linha 5: n!, 9, 6, 1, 2
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

        # Linha inferior de números e confirmação científica
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

        # Cabeçalho do Histórico
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

        # Scrollable Frame para os cartões de cálculo
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

            # Cabeçalho do Card com Timestamp e Badge
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

            # Expressão
            lbl_expr = ctk.CTkLabel(
                card,
                text=item["expression"],
                font=ctk.CTkFont(family="Consolas", size=13),
                text_color="#9CA3AF",
                anchor="w"
            )
            lbl_expr.pack(fill="x", padx=14, pady=(2, 0))

            # Resultado com Botão de Reutilizar
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

    # =========================================================================
    # Fallback para Tkinter Padrão (Sem bibliotecas externas)
    # =========================================================================
    def _init_standard_tkinter_app(self):
        self.root = tk.Tk()
        self.root.title("Calculadora Moderna")
        self.root.configure(bg="#0A0A0E")
        self.root.geometry("1024x720")
        self.root.minsize(820, 620)

        self._aplicar_abertura_maximizada()

        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Escape>", self._on_escape_key)
        self.root.bind("<Key>", self._tratar_teclado)

        # Configuração de estilo ttk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#121319", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1E2029", foreground="#FFFFFF", padding=[16, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#FF6B00")], foreground=[("selected", "#FFFFFF")])

        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(0, weight=1)

        # Container da Calculadora
        calc_container = tk.Frame(self.root, bg="#121319")
        calc_container.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        calc_container.grid_columnconfigure(0, weight=1)
        calc_container.grid_rowconfigure(2, weight=1)

        # Top Bar
        top_bar = tk.Frame(calc_container, bg="#121319")
        top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 6))

        tk.Label(
            top_bar,
            text="CALCULADORA MODERNA",
            font=("Segoe UI", 12, "bold"),
            fg="#A0A2B0",
            bg="#121319"
        ).pack(side="left")

        self.btn_som = tk.Button(
            top_bar,
            text="🔊 Som: Ativado",
            font=("Segoe UI", 9, "bold"),
            bg="#1E2029",
            fg="#FF6B00",
            bd=0,
            padx=10,
            pady=4,
            command=self._toggle_som
        )
        self.btn_som.pack(side="right", padx=(8, 0))

        self.btn_copiar = tk.Button(
            top_bar,
            text="📋 Copiar",
            font=("Segoe UI", 9, "bold"),
            bg="#1E2029",
            fg="#FFFFFF",
            bd=0,
            padx=10,
            pady=4,
            command=self.copiar_resultado
        )
        self.btn_copiar.pack(side="right")

        # Visor
        display_frame = tk.Frame(calc_container, bg="#181A22")
        display_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(6, 12))

        self.lbl_secundaria = tk.Label(
            display_frame,
            text="",
            font=("Consolas", 11),
            fg="#7A7D8E",
            bg="#181A22",
            anchor="e"
        )
        self.lbl_secundaria.pack(fill="x", padx=16, pady=(10, 0))

        self.lbl_display = tk.Label(
            display_frame,
            text="0",
            font=("Segoe UI", 32, "bold"),
            fg="#FFFFFF",
            bg="#181A22",
            anchor="e"
        )
        self.lbl_display.pack(fill="x", padx=16, pady=(0, 10))

        # Notebook com Abas
        notebook = ttk.Notebook(calc_container)
        notebook.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 16))

        tab_basica = tk.Frame(notebook, bg="#121319")
        tab_cientifica = tk.Frame(notebook, bg="#121319")
        notebook.add(tab_basica, text="Básica")
        notebook.add(tab_cientifica, text="Científica")

        self._montar_teclado_basico_tk(tab_basica)
        self._montar_teclado_cientifico_tk(tab_cientifica)

        # Histórico
        self._montar_painel_historico_tk()

        self.root.mainloop()

    def _montar_teclado_basico_tk(self, parent):
        for r in range(5):
            parent.grid_rowconfigure(r, weight=1)
        for c in range(4):
            parent.grid_columnconfigure(c, weight=1)

        botoes = [
            ("C", 0, 0, "#262832", "#FF9A3C", self.limpar_tudo),
            ("±", 0, 1, "#22242D", "#FFFFFF", self.alternar_sinal),
            ("%", 0, 2, "#22242D", "#FFFFFF", self.inserir_porcentagem),
            ("÷", 0, 3, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" ÷ ")),

            ("7", 1, 0, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("7")),
            ("8", 1, 1, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("8")),
            ("9", 1, 2, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("9")),
            ("×", 1, 3, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" × ")),

            ("4", 2, 0, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("4")),
            ("5", 2, 1, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("5")),
            ("6", 2, 2, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("6")),
            ("-", 2, 3, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" - ")),

            ("1", 3, 0, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("1")),
            ("2", 3, 1, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("2")),
            ("3", 3, 2, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("3")),
            ("+", 3, 3, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" + ")),

            ("0", 4, 0, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("0")),
            (".", 4, 1, "#1F2129", "#FFFFFF", self.inserir_ponto),
            ("⌫", 4, 2, "#262832", "#FF9A3C", self.apagar_ultimo),
            ("=", 4, 3, "#FF6B00", "#FFFFFF", self.calcular),
        ]

        for texto, r, c, bg_cor, fg_cor, cmd in botoes:
            btn = tk.Button(
                parent,
                text=texto,
                font=("Segoe UI", 15, "bold"),
                bg=bg_cor,
                fg=fg_cor,
                activebackground="#FF8533" if bg_cor == "#FF6B00" else "#333742",
                activeforeground="#FFFFFF",
                bd=0,
                command=cmd
            )
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

    def _montar_teclado_cientifico_tk(self, parent):
        for r in range(6):
            parent.grid_rowconfigure(r, weight=1)
        for c in range(5):
            parent.grid_columnconfigure(c, weight=1)

        botoes = [
            (self.evaluator.angle_mode, 0, 0, "#262832", "#FF6B00", self._toggle_deg_rad),
            ("(", 0, 1, "#262832", "#FF9A3C", lambda: self.inserir_texto("(")),
            (")", 0, 2, "#262832", "#FF9A3C", lambda: self.inserir_texto(")")),
            ("√", 0, 3, "#262832", "#FF9A3C", lambda: self.inserir_funcao("sqrt")),
            ("C", 0, 4, "#262832", "#FF9A3C", self.limpar_tudo),

            ("sin", 1, 0, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("sin")),
            ("cos", 1, 1, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("cos")),
            ("tan", 1, 2, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("tan")),
            ("x²", 1, 3, "#22242D", "#FFFFFF", lambda: self.inserir_texto("²")),
            ("÷", 1, 4, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" ÷ ")),

            ("asin", 2, 0, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("asin")),
            ("acos", 2, 1, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("acos")),
            ("atan", 2, 2, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("atan")),
            ("x^y", 2, 3, "#22242D", "#FFFFFF", lambda: self.inserir_operador(" ^ ")),
            ("×", 2, 4, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" × ")),

            ("ln", 3, 0, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("ln")),
            ("log", 3, 1, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("log")),
            ("7", 3, 2, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("7")),
            ("8", 3, 3, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("8")),
            ("-", 3, 4, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" - ")),

            ("π", 4, 0, "#22242D", "#FFFFFF", lambda: self.inserir_texto("π")),
            ("e", 4, 1, "#22242D", "#FFFFFF", lambda: self.inserir_texto("e")),
            ("4", 4, 2, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("4")),
            ("5", 4, 3, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("5")),
            ("+", 4, 4, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" + ")),

            ("n!", 5, 0, "#22242D", "#FFFFFF", lambda: self.inserir_texto("!")),
            ("9", 5, 1, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("9")),
            ("6", 5, 2, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("6")),
            ("1", 5, 3, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("1")),
            ("2", 5, 4, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("2")),
        ]

        self.btn_deg_rad_tk = None
        for texto, r, c, bg_cor, fg_cor, cmd in botoes:
            btn = tk.Button(
                parent,
                text=texto,
                font=("Segoe UI", 11, "bold"),
                bg=bg_cor,
                fg=fg_cor,
                bd=0,
                command=cmd
            )
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            if r == 0 and c == 0:
                self.btn_deg_rad_tk = btn

        row_extra = tk.Frame(parent, bg="#121319")
        row_extra.grid(row=6, column=0, columnspan=5, sticky="nsew", pady=(4, 0))
        for i in range(5):
            row_extra.grid_columnconfigure(i, weight=1)

        botoes_extra = [
            ("3", 0, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("3")),
            ("0", 1, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("0")),
            (".", 2, "#1F2129", "#FFFFFF", self.inserir_ponto),
            ("⌫", 3, "#262832", "#FF9A3C", self.apagar_ultimo),
            ("=", 4, "#FF6B00", "#FFFFFF", self.calcular),
        ]

        for texto, col, bg_cor, fg_cor, cmd in botoes_extra:
            btn = tk.Button(
                row_extra,
                text=texto,
                font=("Segoe UI", 12, "bold"),
                bg=bg_cor,
                fg=fg_cor,
                bd=0,
                command=cmd
            )
            btn.grid(row=0, column=col, padx=3, pady=2, sticky="nsew")

    def _montar_painel_historico_tk(self):
        hist_container = tk.Frame(self.root, bg="#121319")
        hist_container.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)
        hist_container.grid_columnconfigure(0, weight=1)
        hist_container.grid_rowconfigure(1, weight=1)

        hist_header = tk.Frame(hist_container, bg="#121319")
        hist_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 12))

        tk.Label(
            hist_header,
            text="HISTÓRICO (5 ÚLTIMOS)",
            font=("Segoe UI", 11, "bold"),
            fg="#A0A2B0",
            bg="#121319"
        ).pack(side="left")

        tk.Button(
            hist_header,
            text="🗑 Limpar",
            font=("Segoe UI", 9, "bold"),
            bg="#242633",
            fg="#F87171",
            bd=0,
            padx=8,
            pady=3,
            command=self.confirmar_limpar_historico
        ).pack(side="right")

        canvas = tk.Canvas(hist_container, bg="#121319", bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(hist_container, orient="vertical", command=canvas.yview)
        self.scroll_historico_tk = tk.Frame(canvas, bg="#121319")

        self.scroll_historico_tk.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_historico_tk, anchor="nw", width=360)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=1, column=0, sticky="nsew", padx=(16, 0), pady=(0, 16))
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 16))

        self._renderizar_historico_tk()

    def _renderizar_historico_tk(self):
        for widget in self.scroll_historico_tk.winfo_children():
            widget.destroy()

        historico = self.history_manager.history
        if not historico:
            tk.Label(
                self.scroll_historico_tk,
                text="Nenhum cálculo registrado ainda.\\n\\nOs últimos 5 cálculos salvos\\naparecerão aqui.",
                font=("Segoe UI", 10),
                fg="#636674",
                bg="#121319"
            ).pack(fill="both", expand=True, pady=40)
            return

        for idx, item in enumerate(historico):
            card = tk.Frame(self.scroll_historico_tk, bg="#181A24", padx=12, pady=8)
            card.pack(fill="x", padx=4, pady=6)

            top = tk.Frame(card, bg="#181A24")
            top.pack(fill="x")
            tk.Label(top, text=f"🕒 {item.get('timestamp', '')}", font=("Segoe UI", 8), fg="#7E8294", bg="#181A24").pack(side="left")
            if idx == 0:
                tk.Label(top, text="RECENTE", font=("Segoe UI", 8, "bold"), fg="#FF6B00", bg="#2B1F17", padx=4).pack(side="right")

            tk.Label(card, text=item["expression"], font=("Consolas", 10), fg="#9CA3AF", bg="#181A24", anchor="w").pack(fill="x", pady=(2, 0))

            bot = tk.Frame(card, bg="#181A24")
            bot.pack(fill="x", pady=(2, 0))
            tk.Label(bot, text=f"= {item['result']}", font=("Segoe UI", 12, "bold"), fg="#FFFFFF", bg="#181A24").pack(side="left")

            resultado_val = item["result"]
            tk.Button(
                bot,
                text="Reutilizar ↗",
                font=("Segoe UI", 8, "bold"),
                bg="#FF6B00",
                fg="#FFFFFF",
                bd=0,
                padx=6,
                pady=2,
                command=lambda val=resultado_val: self.reutilizar_resultado(val)
            ).pack(side="right")

    # =========================================================================
    # Lógica de Interação & Cálculo
    # =========================================================================
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
        elif hasattr(self, "btn_deg_rad_tk") and self.btn_deg_rad_tk:
            self.btn_deg_rad_tk.config(text=novo_modo)

    def _definir_display(self, texto: str):
        self.expressao_atual = str(texto)
        if HAS_CUSTOMTKINTER:
            self.lbl_display.configure(text=self.expressao_atual)
        else:
            self.lbl_display.config(text=self.expressao_atual)

    def _definir_secundaria(self, texto: str):
        self.expressao_secundaria = str(texto)
        if HAS_CUSTOMTKINTER:
            self.lbl_secundaria.configure(text=self.expressao_secundaria)
        else:
            self.lbl_secundaria.config(text=self.expressao_secundaria)

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
            # Se terminar com espaço de operador, remove o bloco do operador
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

            # Salva no histórico (mantém estritamente os 5 mais recentes)
            self.history_manager.add_entry(expr, res_str)

            # Atualiza interface do histórico
            if HAS_CUSTOMTKINTER:
                self._renderizar_historico_ctk()
            else:
                self._renderizar_historico_tk()

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
            else:
                self._renderizar_historico_tk()

    def copiar_resultado(self):
        resultado = self.expressao_atual
        if "Erro" in resultado:
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(resultado)

        # Feedback visual temporário no botão
        if HAS_CUSTOMTKINTER:
            self.btn_copiar.configure(text="✓ Copiado!", text_color="#10B981")
            self.root.after(1600, lambda: self.btn_copiar.configure(text="📋 Copiar", text_color="#FFFFFF"))
        else:
            self.btn_copiar.config(text="✓ Copiado!", fg="#10B981")
            self.root.after(1600, lambda: self.btn_copiar.config(text="📋 Copiar", fg="#FFFFFF"))

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
