"""
Calculadora Moderna em Python (Desktop)
Versão 2.5 - Científica & Básica com Histórico Integrado e Responsividade Avançada

Identidade Visual:
- Fundo preto profundo (#0A0A0E)
- Painéis em cinza escuro (#14161D / #1C1E26)
- Tipografia branca minimalista e legível
- Laranja vibrante (#FF6B00 / #F97316) para operações principais e ações
- Botões arredondados e fontes com ajuste dinâmico proporcional em tela cheia e maximização

Recursos:
- Histórico integrado no topo do visor (estilo Android) exibindo os 3 últimos cálculos
- Botão "Mostrar Histórico" com lista completa de todos os cálculos anteriores
- Botão de desativar/ativar sons do teclado posicionado diretamente acima do ícone "C"
- Caracteres ampliados e com preenchimento robusto nos botões, mantendo proporção ao maximizar
- Abas: "Básica" e "Científica" com funções trigonométricas, DEG/RAD, potências e logaritmos
- Avaliador matemático seguro baseado em AST
- Suporte ao teclado físico e copiar para área de transferência
"""

import math
import os
import sys
import tkinter as tk
import tkinter.font as tkFont
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

        # Estados de cálculo e interface
        self.expressao_atual = "0"
        self.expressao_secundaria = ""
        self.aguardando_novo_numero = False
        self.is_fullscreen = False
        self.historico_aberto = False

        # Referências a botões sincronizados
        self.btn_som = None
        self.btn_som_top = None
        self.btn_deg_rad = None
        self.btn_deg_rad_tk = None

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
        self.root.geometry("640x780")
        self.root.minsize(500, 620)

        # Configuração de Fontes Dinâmicas e Responsivas
        self.font_btn_num = ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        self.font_btn_op = ctk.CTkFont(family="Segoe UI", size=28, weight="bold")
        self.font_btn_fn = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        self.font_btn_top = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        self.font_display = ctk.CTkFont(family="Segoe UI", size=44, weight="bold")
        self.font_display_sec = ctk.CTkFont(family="Consolas", size=15)
        self.font_hist_slot = ctk.CTkFont(family="Consolas", size=14)
        self.font_sci_fn = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")

        # Abertura maximizada
        self._aplicar_abertura_maximizada()

        # Teclas de atalho e redimensionamento dinâmico
        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Escape>", self._on_escape_key)
        self.root.bind("<Key>", self._tratar_teclado)
        self.root.bind("<Configure>", self._ajustar_responsividade_fontes)

        # Layout com uma coluna única (Painel lateral direito removido)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Container Central da Calculadora
        self.calc_container = ctk.CTkFrame(self.root, fg_color="#121319", corner_radius=24)
        self.calc_container.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self.calc_container.grid_columnconfigure(0, weight=1)
        self.calc_container.grid_rowconfigure(0, weight=0)  # Top Bar
        self.calc_container.grid_rowconfigure(1, weight=1)  # Visor Integrado
        self.calc_container.grid_rowconfigure(2, weight=4)  # Teclado / Abas

        # Barra Superior
        top_bar = ctk.CTkFrame(self.calc_container, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 6))

        titulo = ctk.CTkLabel(
            top_bar,
            text="CALCULADORA MODERNA",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#A0A2B0"
        )
        titulo.pack(side="left")

        # Botão de Histórico Completo no cabeçalho
        self.btn_hist_top = ctk.CTkButton(
            top_bar,
            text="📜 Histórico",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#1E2029",
            hover_color="#2A2D3A",
            text_color="#FF9A3C",
            width=90,
            height=28,
            corner_radius=10,
            command=self.abrir_historico
        )
        self.btn_hist_top.pack(side="right", padx=(8, 0))

        # Botão de Copiar no cabeçalho
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

        # Display do Visor Integrado (com Histórico dos 3 últimos cálculos estilo Android)
        self.display_frame = ctk.CTkFrame(self.calc_container, fg_color="#181A22", corner_radius=18)
        self.display_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(4, 10))
        self.display_frame.grid_columnconfigure(0, weight=1)

        # Container dos 3 últimos cálculos (Mini-Histórico no Visor)
        self.hist_display_frame = ctk.CTkFrame(self.display_frame, fg_color="transparent")
        self.hist_display_frame.pack(fill="x", padx=18, pady=(8, 2))

        self.lbl_hist_slots = []
        # Cores suaves e graduais para a lista dos 3 últimos cálculos
        cores_slots = ["#6A6E80", "#868B9E", "#A6ABC0"]
        for i in range(3):
            lbl = ctk.CTkLabel(
                self.hist_display_frame,
                text="",
                font=self.font_hist_slot,
                text_color=cores_slots[i],
                anchor="e",
                cursor="hand2"
            )
            lbl.pack(fill="x", pady=1)
            self.lbl_hist_slots.append(lbl)

        # Linha secundária de expressão ativa
        self.lbl_secundaria = ctk.CTkLabel(
            self.display_frame,
            text="",
            font=self.font_display_sec,
            text_color="#FF9A3C",
            anchor="e"
        )
        self.lbl_secundaria.pack(fill="x", padx=18, pady=(2, 0))

        # Visor Principal de Dígitos e Resultado
        self.lbl_display = ctk.CTkLabel(
            self.display_frame,
            text="0",
            font=self.font_display,
            text_color="#FFFFFF",
            anchor="e"
        )
        self.lbl_display.pack(fill="x", padx=18, pady=(0, 10))

        # Abas da Calculadora (Básica e Científica)
        self.tabview = ctk.CTkTabview(
            self.calc_container,
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

        # Monta a tela de sobreposição de Histórico Completo
        self._montar_overlay_historico_ctk()

        # Atualiza a lista dos 3 últimos cálculos no visor
        self._atualizar_visor_historico()

        self.root.mainloop()

    def _montar_teclado_basico_ctk(self, parent):
        for r in range(6):
            parent.grid_rowconfigure(r, weight=1)
        for c in range(4):
            parent.grid_columnconfigure(c, weight=1)

        # Linha 0: Botão de som diretamente acima do "C", botão de histórico e copiar
        self.btn_som = ctk.CTkButton(
            parent,
            text="🔊 Som",
            font=self.font_btn_top,
            fg_color="#252834",
            hover_color="#353949",
            text_color="#FF6B00",
            corner_radius=14,
            command=self._toggle_som
        )
        self.btn_som.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        btn_hist_grid = ctk.CTkButton(
            parent,
            text="📜 Histórico",
            font=self.font_btn_top,
            fg_color="#252834",
            hover_color="#353949",
            text_color="#FF9A3C",
            corner_radius=14,
            command=self.abrir_historico
        )
        btn_hist_grid.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="nsew")

        btn_copiar_grid = ctk.CTkButton(
            parent,
            text="📋 Copiar",
            font=self.font_btn_top,
            fg_color="#252834",
            hover_color="#353949",
            text_color="#FFFFFF",
            corner_radius=14,
            command=self.copiar_resultado
        )
        btn_copiar_grid.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")

        # Linhas 1 a 5: Teclado principal com botões cheios e destacados
        botoes = [
            ("C", 1, 0, "fn", self.limpar_tudo),
            ("±", 1, 1, "fn", self.alternar_sinal),
            ("%", 1, 2, "fn", self.inserir_porcentagem),
            ("÷", 1, 3, "op", lambda: self.inserir_operador(" ÷ ")),

            ("7", 2, 0, "num", lambda: self.inserir_texto("7")),
            ("8", 2, 1, "num", lambda: self.inserir_texto("8")),
            ("9", 2, 2, "num", lambda: self.inserir_texto("9")),
            ("×", 2, 3, "op", lambda: self.inserir_operador(" × ")),

            ("4", 3, 0, "num", lambda: self.inserir_texto("4")),
            ("5", 3, 1, "num", lambda: self.inserir_texto("5")),
            ("6", 3, 2, "num", lambda: self.inserir_texto("6")),
            ("-", 3, 3, "op", lambda: self.inserir_operador(" - ")),

            ("1", 4, 0, "num", lambda: self.inserir_texto("1")),
            ("2", 4, 1, "num", lambda: self.inserir_texto("2")),
            ("3", 4, 2, "num", lambda: self.inserir_texto("3")),
            ("+", 4, 3, "op", lambda: self.inserir_operador(" + ")),

            ("0", 5, 0, "num", lambda: self.inserir_texto("0")),
            (".", 5, 1, "num", self.inserir_ponto),
            ("⌫", 5, 2, "fn", self.apagar_ultimo),
            ("=", 5, 3, "eq", self.calcular),
        ]

        for texto, r, c, tipo, cmd in botoes:
            fg, hover, txt_cor = self._obter_cores_botao(tipo)
            if tipo == "num":
                f = self.font_btn_num
            elif tipo in ("op", "eq"):
                f = self.font_btn_op
            else:
                f = self.font_btn_fn

            btn = ctk.CTkButton(
                parent,
                text=texto,
                font=f,
                fg_color=fg,
                hover_color=hover,
                text_color=txt_cor,
                corner_radius=14,
                command=cmd
            )
            btn.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

    def _montar_teclado_cientifico_ctk(self, parent):
        for r in range(6):
            parent.grid_rowconfigure(r, weight=1, uniform="sci_row")
        for c in range(6):
            parent.grid_columnconfigure(c, weight=1, uniform="sci_col")

        botoes = [
            ("sin", 0, 0, "fn", lambda: self.inserir_funcao("sin")),
            ("asin", 0, 1, "fn", lambda: self.inserir_funcao("asin")),
            ("(", 0, 2, "fn", lambda: self.inserir_texto("(")),
            (")", 0, 3, "fn", lambda: self.inserir_texto(")")),
            ("⌫", 0, 4, "fn", self.apagar_ultimo),
            ("C", 0, 5, "fn", self.limpar_tudo),

            ("cos", 1, 0, "fn", lambda: self.inserir_funcao("cos")),
            ("acos", 1, 1, "fn", lambda: self.inserir_funcao("acos")),
            ("7", 1, 2, "num", lambda: self.inserir_texto("7")),
            ("8", 1, 3, "num", lambda: self.inserir_texto("8")),
            ("9", 1, 4, "num", lambda: self.inserir_texto("9")),
            ("÷", 1, 5, "op", lambda: self.inserir_operador(" ÷ ")),

            ("tan", 2, 0, "fn", lambda: self.inserir_funcao("tan")),
            ("atan", 2, 1, "fn", lambda: self.inserir_funcao("atan")),
            ("4", 2, 2, "num", lambda: self.inserir_texto("4")),
            ("5", 2, 3, "num", lambda: self.inserir_texto("5")),
            ("6", 2, 4, "num", lambda: self.inserir_texto("6")),
            ("×", 2, 5, "op", lambda: self.inserir_operador(" × ")),

            ("ln", 3, 0, "fn", lambda: self.inserir_funcao("ln")),
            ("log", 3, 1, "fn", lambda: self.inserir_funcao("log")),
            ("1", 3, 2, "num", lambda: self.inserir_texto("1")),
            ("2", 3, 3, "num", lambda: self.inserir_texto("2")),
            ("3", 3, 4, "num", lambda: self.inserir_texto("3")),
            ("-", 3, 5, "op", lambda: self.inserir_operador(" - ")),

            ("x²", 4, 0, "fn", lambda: self.inserir_texto("²")),
            ("x^y", 4, 1, "fn", lambda: self.inserir_operador(" ^ ")),
            ("π", 4, 2, "fn", lambda: self.inserir_texto("π")),
            ("0", 4, 3, "num", lambda: self.inserir_texto("0")),
            ("e", 4, 4, "fn", lambda: self.inserir_texto("e")),
            ("+", 4, 5, "op", lambda: self.inserir_operador(" + ")),

            ("√", 5, 0, "fn", lambda: self.inserir_funcao("sqrt")),
            ("n!", 5, 1, "fn", lambda: self.inserir_texto("!")),
            (self.evaluator.angle_mode, 5, 2, "deg", self._toggle_deg_rad),
            (".", 5, 3, "num", self.inserir_ponto),
            ("%", 5, 4, "fn", self.inserir_porcentagem),
            ("=", 5, 5, "eq", self.calcular),
        ]

        self.btn_deg_rad = None
        for texto, r, c, tipo, cmd in botoes:
            fg, hover, txt_cor = self._obter_cores_botao(tipo)
            f = self.font_btn_num if tipo == "num" else self.font_sci_fn
            btn = ctk.CTkButton(
                parent,
                text=texto,
                font=f,
                fg_color=fg,
                hover_color=hover,
                text_color=txt_cor,
                corner_radius=12,
                command=cmd
            )
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            if tipo == "deg":
                self.btn_deg_rad = btn

    def _montar_overlay_historico_ctk(self):
        """Cria o painel deslizante/sobreposto de Histórico Completo com todos os cálculos."""
        self.overlay_historico = ctk.CTkFrame(
            self.calc_container,
            fg_color="#121319",
            corner_radius=20
        )

        header = ctk.CTkFrame(self.overlay_historico, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 10))

        self.lbl_hist_count = ctk.CTkLabel(
            header,
            text="HISTÓRICO COMPLETO",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#FF6B00"
        )
        self.lbl_hist_count.pack(side="left")

        btn_fechar = ctk.CTkButton(
            header,
            text="✕ Fechar",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#1E2029",
            hover_color="#2A2D3A",
            text_color="#FFFFFF",
            width=75,
            height=28,
            corner_radius=8,
            command=self.fechar_historico
        )
        btn_fechar.pack(side="right", padx=(8, 0))

        btn_limpar = ctk.CTkButton(
            header,
            text="🗑 Limpar Tudo",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#242633",
            hover_color="#36394A",
            text_color="#F87171",
            width=95,
            height=28,
            corner_radius=8,
            command=self.confirmar_limpar_historico
        )
        btn_limpar.pack(side="right")

        self.scroll_historico = ctk.CTkScrollableFrame(
            self.overlay_historico,
            fg_color="#161821",
            corner_radius=14
        )
        self.scroll_historico.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def _renderizar_overlay_historico_ctk(self):
        for widget in self.scroll_historico.winfo_children():
            widget.destroy()

        historico = self.history_manager.history
        total = len(historico)
        self.lbl_hist_count.configure(text=f"HISTÓRICO COMPLETO ({total})")

        if not historico:
            vazio = ctk.CTkLabel(
                self.scroll_historico,
                text="Nenhum cálculo registrado ainda.\n\nTodos os cálculos realizados aparecerão aqui.",
                font=ctk.CTkFont(size=13),
                text_color="#636674",
                justify="center"
            )
            vazio.pack(fill="both", expand=True, pady=40)
            return

        for idx, item in enumerate(historico):
            card = ctk.CTkFrame(self.scroll_historico, fg_color="#1C1E26", corner_radius=12)
            card.pack(fill="x", padx=6, pady=5)

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
                    text="MAIS RECENTE",
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
                font=ctk.CTkFont(family="Consolas", size=14),
                text_color="#9CA3AF",
                anchor="w"
            )
            lbl_expr.pack(fill="x", padx=14, pady=(2, 0))

            bot_card = ctk.CTkFrame(card, fg_color="transparent")
            bot_card.pack(fill="x", padx=14, pady=(2, 8))

            lbl_res = ctk.CTkLabel(
                bot_card,
                text=f"= {item['result']}",
                font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
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
                width=78,
                height=26,
                corner_radius=8,
                command=lambda val=resultado_val: self._reutilizar_e_fechar(val)
            )
            btn_usar.pack(side="right")

    # =========================================================================
    # Fallback para Tkinter Padrão (Sem bibliotecas externas)
    # =========================================================================
    def _init_standard_tkinter_app(self):
        self.root = tk.Tk()
        self.root.title("Calculadora Moderna")
        self.root.configure(bg="#0A0A0E")
        self.root.geometry("640x780")
        self.root.minsize(500, 620)

        # Fontes Tkinter nativas escaláveis
        self.font_btn_num = tkFont.Font(family="Segoe UI", size=20, weight="bold")
        self.font_btn_op = tkFont.Font(family="Segoe UI", size=22, weight="bold")
        self.font_btn_fn = tkFont.Font(family="Segoe UI", size=18, weight="bold")
        self.font_btn_top = tkFont.Font(family="Segoe UI", size=12, weight="bold")
        self.font_display = tkFont.Font(family="Segoe UI", size=36, weight="bold")
        self.font_display_sec = tkFont.Font(family="Consolas", size=13)
        self.font_hist_slot = tkFont.Font(family="Consolas", size=12)
        self.font_sci_fn = tkFont.Font(family="Segoe UI", size=13, weight="bold")

        self._aplicar_abertura_maximizada()

        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Escape>", self._on_escape_key)
        self.root.bind("<Key>", self._tratar_teclado)
        self.root.bind("<Configure>", self._ajustar_responsividade_fontes)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#121319", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1E2029", foreground="#FFFFFF", padding=[16, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#FF6B00")], foreground=[("selected", "#FFFFFF")])

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.calc_container = tk.Frame(self.root, bg="#121319")
        self.calc_container.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self.calc_container.grid_columnconfigure(0, weight=1)
        self.calc_container.grid_rowconfigure(0, weight=0)
        self.calc_container.grid_rowconfigure(1, weight=1)
        self.calc_container.grid_rowconfigure(2, weight=4)

        top_bar = tk.Frame(self.calc_container, bg="#121319")
        top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 6))

        tk.Label(
            top_bar,
            text="CALCULADORA MODERNA",
            font=("Segoe UI", 12, "bold"),
            fg="#A0A2B0",
            bg="#121319"
        ).pack(side="left")

        self.btn_hist_top = tk.Button(
            top_bar,
            text="📜 Histórico",
            font=("Segoe UI", 9, "bold"),
            bg="#1E2029",
            fg="#FF9A3C",
            bd=0,
            padx=10,
            pady=4,
            command=self.abrir_historico
        )
        self.btn_hist_top.pack(side="right", padx=(8, 0))

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

        # Visor Integrado com Histórico estilo Android
        self.display_frame = tk.Frame(self.calc_container, bg="#181A22")
        self.display_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(4, 10))

        self.hist_display_frame = tk.Frame(self.display_frame, bg="#181A22")
        self.hist_display_frame.pack(fill="x", padx=16, pady=(8, 2))

        self.lbl_hist_slots = []
        cores_slots = ["#6A6E80", "#868B9E", "#A6ABC0"]
        for i in range(3):
            lbl = tk.Label(
                self.hist_display_frame,
                text="",
                font=self.font_hist_slot,
                fg=cores_slots[i],
                bg="#181A22",
                anchor="e",
                cursor="hand2"
            )
            lbl.pack(fill="x", pady=1)
            self.lbl_hist_slots.append(lbl)

        self.lbl_secundaria = tk.Label(
            self.display_frame,
            text="",
            font=self.font_display_sec,
            fg="#FF9A3C",
            bg="#181A22",
            anchor="e"
        )
        self.lbl_secundaria.pack(fill="x", padx=16, pady=(2, 0))

        self.lbl_display = tk.Label(
            self.display_frame,
            text="0",
            font=self.font_display,
            fg="#FFFFFF",
            bg="#181A22",
            anchor="e"
        )
        self.lbl_display.pack(fill="x", padx=16, pady=(0, 8))

        notebook = ttk.Notebook(self.calc_container)
        notebook.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 16))

        tab_basica = tk.Frame(notebook, bg="#121319")
        tab_cientifica = tk.Frame(notebook, bg="#121319")
        notebook.add(tab_basica, text="Básica")
        notebook.add(tab_cientifica, text="Científica")

        self._montar_teclado_basico_tk(tab_basica)
        self._montar_teclado_cientifico_tk(tab_cientifica)

        self._montar_overlay_historico_tk()
        self._atualizar_visor_historico()

        self.root.mainloop()

    def _montar_teclado_basico_tk(self, parent):
        for r in range(6):
            parent.grid_rowconfigure(r, weight=1)
        for c in range(4):
            parent.grid_columnconfigure(c, weight=1)

        # Botão de som diretamente acima do "C"
        self.btn_som = tk.Button(
            parent,
            text="🔊 Som",
            font=self.font_btn_top,
            bg="#252834",
            fg="#FF6B00",
            bd=0,
            command=self._toggle_som
        )
        self.btn_som.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")

        btn_hist = tk.Button(
            parent,
            text="📜 Histórico",
            font=self.font_btn_top,
            bg="#252834",
            fg="#FF9A3C",
            bd=0,
            command=self.abrir_historico
        )
        btn_hist.grid(row=0, column=1, columnspan=2, padx=4, pady=4, sticky="nsew")

        btn_cop = tk.Button(
            parent,
            text="📋 Copiar",
            font=self.font_btn_top,
            bg="#252834",
            fg="#FFFFFF",
            bd=0,
            command=self.copiar_resultado
        )
        btn_cop.grid(row=0, column=3, padx=4, pady=4, sticky="nsew")

        botoes = [
            ("C", 1, 0, "#262832", "#FF9A3C", self.limpar_tudo),
            ("±", 1, 1, "#22242D", "#FFFFFF", self.alternar_sinal),
            ("%", 1, 2, "#22242D", "#FFFFFF", self.inserir_porcentagem),
            ("÷", 1, 3, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" ÷ ")),

            ("7", 2, 0, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("7")),
            ("8", 2, 1, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("8")),
            ("9", 2, 2, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("9")),
            ("×", 2, 3, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" × ")),

            ("4", 3, 0, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("4")),
            ("5", 3, 1, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("5")),
            ("6", 3, 2, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("6")),
            ("-", 3, 3, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" - ")),

            ("1", 4, 0, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("1")),
            ("2", 4, 1, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("2")),
            ("3", 4, 2, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("3")),
            ("+", 4, 3, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" + ")),

            ("0", 5, 0, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("0")),
            (".", 5, 1, "#1F2129", "#FFFFFF", self.inserir_ponto),
            ("⌫", 5, 2, "#262832", "#FF9A3C", self.apagar_ultimo),
            ("=", 5, 3, "#FF6B00", "#FFFFFF", self.calcular),
        ]

        for texto, r, c, bg_cor, fg_cor, cmd in botoes:
            f = self.font_btn_num if texto in "0123456789." else self.font_btn_op
            btn = tk.Button(
                parent,
                text=texto,
                font=f,
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
            parent.grid_rowconfigure(r, weight=1, uniform="sci_row")
        for c in range(6):
            parent.grid_columnconfigure(c, weight=1, uniform="sci_col")

        botoes = [
            ("sin", 0, 0, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("sin")),
            ("asin", 0, 1, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("asin")),
            ("(", 0, 2, "#262832", "#FF9A3C", lambda: self.inserir_texto("(")),
            (")", 0, 3, "#262832", "#FF9A3C", lambda: self.inserir_texto(")")),
            ("⌫", 0, 4, "#262832", "#FF9A3C", self.apagar_ultimo),
            ("C", 0, 5, "#2A2226", "#FF8A65", self.limpar_tudo),

            ("cos", 1, 0, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("cos")),
            ("acos", 1, 1, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("acos")),
            ("7", 1, 2, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("7")),
            ("8", 1, 3, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("8")),
            ("9", 1, 4, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("9")),
            ("÷", 1, 5, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" ÷ ")),

            ("tan", 2, 0, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("tan")),
            ("atan", 2, 1, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("atan")),
            ("4", 2, 2, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("4")),
            ("5", 2, 3, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("5")),
            ("6", 2, 4, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("6")),
            ("×", 2, 5, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" × ")),

            ("ln", 3, 0, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("ln")),
            ("log", 3, 1, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("log")),
            ("1", 3, 2, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("1")),
            ("2", 3, 3, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("2")),
            ("3", 3, 4, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("3")),
            ("-", 3, 5, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" - ")),

            ("x²", 4, 0, "#22242D", "#FFFFFF", lambda: self.inserir_texto("²")),
            ("x^y", 4, 1, "#22242D", "#FFFFFF", lambda: self.inserir_operador(" ^ ")),
            ("π", 4, 2, "#22242D", "#FFFFFF", lambda: self.inserir_texto("π")),
            ("0", 4, 3, "#1F2129", "#FFFFFF", lambda: self.inserir_texto("0")),
            ("e", 4, 4, "#22242D", "#FFFFFF", lambda: self.inserir_texto("e")),
            ("+", 4, 5, "#FF6B00", "#FFFFFF", lambda: self.inserir_operador(" + ")),

            ("√", 5, 0, "#22242D", "#FFFFFF", lambda: self.inserir_funcao("sqrt")),
            ("n!", 5, 1, "#22242D", "#FFFFFF", lambda: self.inserir_texto("!")),
            (self.evaluator.angle_mode, 5, 2, "#262832", "#FF6B00", self._toggle_deg_rad),
            (".", 5, 3, "#1F2129", "#FFFFFF", self.inserir_ponto),
            ("%", 5, 4, "#22242D", "#FFFFFF", self.inserir_porcentagem),
            ("=", 5, 5, "#FF6B00", "#FFFFFF", self.calcular),
        ]

        self.btn_deg_rad_tk = None
        for texto, r, c, bg_cor, fg_cor, cmd in botoes:
            btn = tk.Button(
                parent,
                text=texto,
                font=self.font_sci_fn,
                bg=bg_cor,
                fg=fg_cor,
                bd=0,
                command=cmd
            )
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            if r == 5 and c == 2:
                self.btn_deg_rad_tk = btn

    def _montar_overlay_historico_tk(self):
        self.overlay_historico = tk.Frame(self.calc_container, bg="#121319")

        header = tk.Frame(self.overlay_historico, bg="#121319")
        header.pack(fill="x", padx=20, pady=(16, 10))

        self.lbl_hist_count = tk.Label(
            header,
            text="HISTÓRICO COMPLETO",
            font=("Segoe UI", 12, "bold"),
            fg="#FF6B00",
            bg="#121319"
        )
        self.lbl_hist_count.pack(side="left")

        btn_fechar = tk.Button(
            header,
            text="✕ Fechar",
            font=("Segoe UI", 9, "bold"),
            bg="#1E2029",
            fg="#FFFFFF",
            bd=0,
            padx=10,
            pady=4,
            command=self.fechar_historico
        )
        btn_fechar.pack(side="right", padx=(8, 0))

        btn_limpar = tk.Button(
            header,
            text="🗑 Limpar Tudo",
            font=("Segoe UI", 9, "bold"),
            bg="#242633",
            fg="#F87171",
            bd=0,
            padx=10,
            pady=4,
            command=self.confirmar_limpar_historico
        )
        btn_limpar.pack(side="right")

        canvas = tk.Canvas(self.overlay_historico, bg="#161821", bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.overlay_historico, orient="vertical", command=canvas.yview)
        self.scroll_historico_tk = tk.Frame(canvas, bg="#161821")

        self.scroll_historico_tk.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_historico_tk, anchor="nw", width=460)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(16, 0), pady=(0, 16))
        scrollbar.pack(side="right", fill="y", pady=(0, 16), padx=(0, 16))

    def _renderizar_overlay_historico_tk(self):
        for widget in self.scroll_historico_tk.winfo_children():
            widget.destroy()

        historico = self.history_manager.history
        total = len(historico)
        self.lbl_hist_count.config(text=f"HISTÓRICO COMPLETO ({total})")

        if not historico:
            tk.Label(
                self.scroll_historico_tk,
                text="Nenhum cálculo registrado ainda.\n\nTodos os cálculos realizados aparecerão aqui.",
                font=("Segoe UI", 11),
                fg="#636674",
                bg="#161821"
            ).pack(fill="both", expand=True, pady=40)
            return

        for idx, item in enumerate(historico):
            card = tk.Frame(self.scroll_historico_tk, bg="#1C1E26", padx=12, pady=8)
            card.pack(fill="x", padx=6, pady=5)

            top = tk.Frame(card, bg="#1C1E26")
            top.pack(fill="x")
            tk.Label(top, text=f"🕒 {item.get('timestamp', '')}", font=("Segoe UI", 8), fg="#7E8294", bg="#1C1E26").pack(side="left")
            if idx == 0:
                tk.Label(top, text="MAIS RECENTE", font=("Segoe UI", 8, "bold"), fg="#FF6B00", bg="#2B1F17", padx=4).pack(side="right")

            tk.Label(card, text=item["expression"], font=("Consolas", 11), fg="#9CA3AF", bg="#1C1E26", anchor="w").pack(fill="x", pady=(2, 0))

            bot = tk.Frame(card, bg="#1C1E26")
            bot.pack(fill="x", pady=(2, 0))
            tk.Label(bot, text=f"= {item['result']}", font=("Segoe UI", 13, "bold"), fg="#FFFFFF", bg="#1C1E26").pack(side="left")

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
                command=lambda val=resultado_val: self._reutilizar_e_fechar(val)
            ).pack(side="right")

    # =========================================================================
    # Lógica de Responsividade Dinâmica das Fontes
    # =========================================================================
    def _ajustar_responsividade_fontes(self, event=None):
        """Ajusta o tamanho dos caracteres dinamicamente para preencher cheiamente os ícones."""
        if event and event.widget != self.root:
            return

        h = self.root.winfo_height()
        if h < 250:
            return

        # Escala dinâmica baseada na altura da janela (altura padrão: 700px)
        scale = max(0.9, min(h / 700.0, 1.85))

        if HAS_CUSTOMTKINTER:
            self.font_btn_num.configure(size=int(26 * scale))
            self.font_btn_op.configure(size=int(28 * scale))
            self.font_btn_fn.configure(size=int(22 * scale))
            self.font_btn_top.configure(size=int(14 * scale))
            self.font_display.configure(size=int(44 * scale))
            self.font_display_sec.configure(size=int(15 * scale))
            self.font_hist_slot.configure(size=int(14 * scale))
            self.font_sci_fn.configure(size=int(16 * scale))
        else:
            self.font_btn_num.configure(size=int(20 * scale))
            self.font_btn_op.configure(size=int(22 * scale))
            self.font_btn_fn.configure(size=int(18 * scale))
            self.font_btn_top.configure(size=int(12 * scale))
            self.font_display.configure(size=int(36 * scale))
            self.font_display_sec.configure(size=int(13 * scale))
            self.font_hist_slot.configure(size=int(12 * scale))
            self.font_sci_fn.configure(size=int(13 * scale))

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
                self.root.geometry("700x820")

    def _toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def _on_escape_key(self, event=None):
        if self.historico_aberto:
            self.fechar_historico()
            return
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)
        else:
            self.limpar_tudo()

    def _toggle_som(self):
        """Ativa ou desativa os sons do teclado e atualiza a indicação visual."""
        ativado = self.sound_manager.toggle()
        texto = "🔊 Som" if ativado else "🔇 Mudo"
        cor = "#FF6B00" if ativado else "#7A7D8E"

        if hasattr(self, "btn_som") and self.btn_som:
            if HAS_CUSTOMTKINTER:
                self.btn_som.configure(text=texto, text_color=cor)
            else:
                self.btn_som.config(text=texto, fg=cor)

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

    def _atualizar_visor_historico(self):
        """Atualiza a lista dos 3 últimos cálculos no topo do visor estilo Android."""
        recentes = list(reversed(self.history_manager.get_recent(3)))
        for i in range(3):
            slot = self.lbl_hist_slots[i]
            offset = 3 - len(recentes)
            if i >= offset:
                item = recentes[i - offset]
                texto = f"{item['expression']} = {item['result']}"
                if HAS_CUSTOMTKINTER:
                    slot.configure(text=texto)
                else:
                    slot.config(text=texto)
                res_val = item['result']
                slot.bind("<Button-1>", lambda e, v=res_val: self.reutilizar_resultado(v))
            else:
                if HAS_CUSTOMTKINTER:
                    slot.configure(text="")
                else:
                    slot.config(text="")
                slot.unbind("<Button-1>")

    def abrir_historico(self):
        """Exibe o painel com todos os cálculos realizados anteriormente."""
        self.historico_aberto = True
        if HAS_CUSTOMTKINTER:
            self._renderizar_overlay_historico_ctk()
        else:
            self._renderizar_overlay_historico_tk()
        self.overlay_historico.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay_historico.lift()

    def fechar_historico(self):
        """Fecha o painel de histórico e retorna à calculadora."""
        self.historico_aberto = False
        self.overlay_historico.place_forget()

    def _reutilizar_e_fechar(self, valor: str):
        self.reutilizar_resultado(valor)
        self.fechar_historico()

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

            # Salva no histórico completo de cálculos
            self.history_manager.add_entry(expr, res_str)

            # Atualiza os 3 cálculos no visor e a sobreposição se estiver aberta
            self._atualizar_visor_historico()
            if self.historico_aberto:
                if HAS_CUSTOMTKINTER:
                    self._renderizar_overlay_historico_ctk()
                else:
                    self._renderizar_overlay_historico_tk()

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
            "Deseja realmente apagar todos os cálculos do histórico?",
            parent=self.root
        )
        if resposta:
            self.history_manager.clear()
            self._atualizar_visor_historico()
            if self.historico_aberto:
                if HAS_CUSTOMTKINTER:
                    self._renderizar_overlay_historico_ctk()
                else:
                    self._renderizar_overlay_historico_tk()

    def copiar_resultado(self):
        resultado = self.expressao_atual
        if "Erro" in resultado:
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(resultado)

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
