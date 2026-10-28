# Calculadora Moderna em Python 🧮

Uma calculadora de desktop profissional, sofisticada e intuitiva desenvolvida em Python para Windows, Linux e macOS. Possui identidade visual em **preto profundo (#0A0A0E)**, botões arredondados em cinza escuro, destaques em **laranja vibrante (#FF6B00)** e fonte branca minimalista de alta legibilidade.

---

## ✨ Principais Recursos

### 1. Interface Gráfica Moderna & Responsiva
- **Design Sofisticado:** Paleta Dark Premium com contraste balanceado e botões arredondados modernos.
- **Abertura Maximizada Automática:** O aplicativo inicializa ocupando o espaço útil do monitor para máxima produtividade.
- **Modo Tela Cheia:** Alterne rapidamente em tela cheia com **F11** e saia a qualquer momento com a tecla **Esc**.
- **Layout Adaptável:** Redimensionamento inteligente sem cortes de texto, números ou botões.

### 2. Abas: Básica e Científica
- **Aba Básica:**
  - Operações aritméticas essenciais: Adição (`+`), Subtração (`-`), Multiplicação (`×`), Divisão (`÷`).
  - Porcentagem (`%`).
  - Inversão de sinal (`±`).
  - Limpar entrada (`C`) e apagar dígito (`⌫`).
- **Aba Científica:**
  - Raiz quadrada (`√` ou `sqrt`).
  - Potenciação (`x^y` ou `^`) e Quadrado de um número (`x²`).
  - Logaritmo de base 10 (`log`) e Logaritmo natural (`ln`).
  - Funções trigonométricas: Seno (`sin`), Cosseno (`cos`), Tangente (`tan`).
  - Funções trigonométricas inversas: Arco-seno (`asin`), Arco-cosseno (`acos`), Arco-tangente (`atan`).
  - Alternância de ângulo entre **DEG** (graus) e **RAD** (radianos) com indicador em tempo real.
  - Parênteses para expressões compostas: `(` e `)`.
  - Constantes matemáticas fundamentais: `π` (pi) e `e` (Euler).
  - Fatorial (`n!`).

### 3. Avaliador Matemático Seguro (AST-based)
- **Zero Risco de Segurança:** Não utiliza a função insegura `eval()`.
- Implementado com a Árvore Sintática Abstrata do Python (`ast`), permitindo exclusivamente números, operadores autorizados e funções matemáticas válidas.
- Respeita rigorosamente a precedência matemática (`*` e `/` antes de `+` e `-`).
- Tratamento amigável de erros matemáticos (divisão por zero, raiz de número negativo, logaritmo de valor menor ou igual a zero, etc.), sem travar o aplicativo ou expor tracebacks técnicos.

### 4. Sistema de Histórico com Persistência Local (5 Últimos Cálculos)
- Cada operação é apresentada em um **cartão visual espaçado e elegante**.
- Exibe expressão, resultado destacado e **data e hora (timestamp)** de cada cálculo.
- **Clique para Reutilizar:** Botão *"Reutilizar ↗"* carrega o resultado instantaneamente no visor.
- **Botão Limpar:** Exibe caixa de diálogo de confirmação antes de apagar todo o histórico.
- **Persistência Local Automática em JSON:** Salva os dados na pasta do usuário:
  - Windows: `%APPDATA%\CalculadoraModerna\historico.json`
  - Linux/Mac: `~/.config/CalculadoraModerna/historico.json`
- Se o arquivo não existir ou estiver corrompido, a calculadora inicia normalmente com histórico limpo.

### 5. Sons Programáticos Não-Bloqueantes
- Sons curtos e agradáveis para digitação de números, operadores, igual e alerta de erro.
- Executados em threads secundárias (*daemon*), sem travar nem causar engasgos na interface gráfica.
- Botão no cabeçalho para ativar ou desativar os sons a qualquer momento.

### 6. Usabilidade e Produtividade
- **Suporte ao Teclado Físico:** Digite números, operadores, `Enter`, `Backspace`, `Esc` e parênteses.
- **Copiar Resultado:** Botão *"📋 Copiar"* envia o valor atual para a área de transferência com feedback visual (*"✓ Copiado!"*).
- **Sem Artefatos de Ponto Flutuante:** Formatação precisa (ex: `0.1 + 0.2` resulta exatamente em `0.3`, e inteiros como `4.0` aparecem como `4`).

---

## 📂 Estrutura do Projeto

```text
├── calculadora.py         # Aplicação gráfica desktop (CustomTkinter + Tkinter)
├── calculadora_core.py    # Lógica desacoplada (Avaliador AST, Histórico JSON, Sons)
├── test_calculadora.py    # Suíte completa de testes unitários automatizados
├── README.md              # Documentação do projeto para o GitHub
```

---

## 🚀 Como Executar no seu Computador

### Pré-requisitos
- **Python 3.8 ou superior** instalado no computador.
- Certifique-se de marcar a opção *"Add Python to PATH"* durante a instalação do Python no Windows.

### Passo 1: Clonar ou Baixar os Arquivos
Baixe os arquivos `calculadora.py` e `calculadora_core.py` para uma pasta de sua escolha.

### Passo 2: Instalar a Biblioteca de Interface Moderna (Recomendado)
Para ativar os cantos arredondados e a estética Dark Premium completa:
```bash
pip install customtkinter
```
*(Nota: se você optar por não instalar o `customtkinter`, a calculadora detecta automaticamente e roda utilizando o `tkinter` nativo padrão do Python sem falhas).*

### Passo 3: Executar a Calculadora
Abra o terminal ou Prompt de Comando (CMD) na pasta do projeto e execute:
```bash
python calculadora.py
```

---

## 📦 Como Gerar o Executável `.exe` para Windows (PyInstaller)

Você pode transformar o aplicativo em um programa `.exe` de um clique que abre diretamente no Windows sem precisar de terminal:

1. Instale o PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Gere o executável portátil de arquivo único:
   ```bash
   pyinstaller --noconsole --onefile --name "CalculadoraModerna" calculadora.py
   ```

3. O arquivo final estará pronto na pasta `dist/CalculadoraModerna.exe`. Basta dar dois cliques para abrir!

---

## 🧪 Executando os Testes Automatizados

O projeto inclui testes de unidade para validação matemática, precedência de operadores, funções trigonométricas, cálculo de fatorial, persistência de histórico e tratamento de erros:

```bash
python -m unittest test_calculadora.py
```

---

## ⌨️ Atalhos do Teclado

| Tecla | Ação |
| :--- | :--- |
| `0` a `9` | Inserir números |
| `+`, `-`, `*`, `/` | Operações básicas |
| `^` | Potenciação |
| `%` | Porcentagem |
| `(` e `)` | Parênteses |
| `.` ou `,` | Ponto decimal |
| `Enter` ou `=` | Calcular resultado |
| `Backspace` | Apagar último caractere |
| `Esc` | Sair da tela cheia ou limpar tudo |
| `F11` | Alternar modo Tela Cheia |

---

## 📄 Licença
Distribuído sob a licença Apache 2.0.
