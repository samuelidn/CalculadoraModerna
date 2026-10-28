import React, { useState, useEffect, useCallback } from 'react';
import {
  Percent,
  Plus,
  Minus,
  X,
  Divide,
  Equal,
  Delete,
  Copy,
  Check,
  Volume2,
  VolumeX,
  Sparkles,
} from 'lucide-react';
import {
  CalculatorState,
  INITIAL_STATE,
  inputDigit,
  inputDecimal,
  inputPercent,
  toggleSign,
  backspace,
  handleOperator,
  calculateEquals,
  clearAll,
  clearHistory,
  recallHistoryItem,
  CalculationHistoryItem,
  Operator,
} from '../utils/calculator';
import { MemoryPanel } from './MemoryPanel';

interface CalculatorProps {
  onHistoryChange?: (count: number) => void;
  isMemoryOpen: boolean;
  onToggleMemory: () => void;
}

// Audio click generator for tactile feedback
function playKeyClick(type: 'num' | 'op' | 'eq' | 'clear', soundEnabled: boolean) {
  if (!soundEnabled || typeof window === 'undefined') return;
  try {
    const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.connect(gain);
    gain.connect(ctx.destination);

    const freq = type === 'eq' ? 520 : type === 'op' ? 440 : type === 'clear' ? 280 : 360;
    osc.frequency.setValueAtTime(freq, ctx.currentTime);
    osc.type = 'sine';

    gain.gain.setValueAtTime(0.04, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.05);

    osc.start();
    osc.stop(ctx.currentTime + 0.05);
  } catch {
    // AudioContext blocked or not supported
  }
}

export const Calculator: React.FC<CalculatorProps> = ({
  onHistoryChange,
  isMemoryOpen,
  onToggleMemory,
}) => {
  const [state, setState] = useState<CalculatorState>(() => {
    // Attempt to load from localStorage
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem('calc_memory_history');
        if (saved) {
          const parsed = JSON.parse(saved);
          if (Array.isArray(parsed)) {
            return {
              ...INITIAL_STATE,
              history: parsed.slice(0, 5),
            };
          }
        }
      } catch {
        // ignore
      }
    }
    return INITIAL_STATE;
  });

  const [soundEnabled, setSoundEnabled] = useState(false);
  const [copiedDisplay, setCopiedDisplay] = useState(false);
  const [activeButton, setActiveButton] = useState<string | null>(null);

  // Sync history to localStorage and parent
  useEffect(() => {
    try {
      localStorage.setItem('calc_memory_history', JSON.stringify(state.history));
    } catch {
      // ignore
    }
    onHistoryChange?.(state.history.length);
  }, [state.history, onHistoryChange]);

  // Flash button effect on keyboard press
  const flashButton = (key: string) => {
    setActiveButton(key);
    setTimeout(() => setActiveButton(null), 120);
  };

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Ignore if user is inside an input or modal
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      const key = e.key;

      if (/^[0-9]$/.test(key)) {
        e.preventDefault();
        flashButton(key);
        playKeyClick('num', soundEnabled);
        setState((prev) => inputDigit(prev, key));
      } else if (key === '.' || key === ',') {
        e.preventDefault();
        flashButton('.');
        playKeyClick('num', soundEnabled);
        setState((prev) => inputDecimal(prev));
      } else if (key === '+') {
        e.preventDefault();
        flashButton('+');
        playKeyClick('op', soundEnabled);
        setState((prev) => handleOperator(prev, '+'));
      } else if (key === '-') {
        e.preventDefault();
        flashButton('-');
        playKeyClick('op', soundEnabled);
        setState((prev) => handleOperator(prev, '-'));
      } else if (key === '*' || key === 'x' || key === 'X') {
        e.preventDefault();
        flashButton('×');
        playKeyClick('op', soundEnabled);
        setState((prev) => handleOperator(prev, '×'));
      } else if (key === '/') {
        e.preventDefault();
        flashButton('÷');
        playKeyClick('op', soundEnabled);
        setState((prev) => handleOperator(prev, '÷'));
      } else if (key === '%') {
        e.preventDefault();
        flashButton('%');
        playKeyClick('num', soundEnabled);
        setState((prev) => inputPercent(prev));
      } else if (key === 'Enter' || key === '=') {
        e.preventDefault();
        flashButton('=');
        playKeyClick('eq', soundEnabled);
        setState((prev) => calculateEquals(prev));
      } else if (key === 'Backspace') {
        e.preventDefault();
        flashButton('backspace');
        playKeyClick('clear', soundEnabled);
        setState((prev) => backspace(prev));
      } else if (key === 'Escape' || key === 'c' || key === 'C') {
        e.preventDefault();
        flashButton('C');
        playKeyClick('clear', soundEnabled);
        setState((prev) => clearAll(prev));
      }
    },
    [soundEnabled]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const handleCopyDisplay = async () => {
    try {
      await navigator.clipboard.writeText(state.displayValue);
      setCopiedDisplay(true);
      setTimeout(() => setCopiedDisplay(false), 1800);
    } catch {
      // fallback
    }
  };

  // Dynamic font sizing for long values
  const getDisplayFontSize = (text: string) => {
    const len = text.length;
    if (len > 13) return 'text-2xl';
    if (len > 10) return 'text-3xl';
    if (len > 7) return 'text-4xl';
    return 'text-5xl';
  };

  return (
    <div className="w-full max-w-md mx-auto flex flex-col gap-4">
      {/* Main Calculator Body */}
      <div
        className="bg-[#121319] border border-neutral-800/90 rounded-[2.2rem] p-5 sm:p-6 shadow-2xl relative overflow-hidden"
        style={{
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 40px rgba(249, 115, 22, 0.05)',
        }}
      >
        {/* Subtle orange accent glow at top */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-1 bg-gradient-to-r from-transparent via-orange-500/40 to-transparent blur-sm" />

        {/* Display Header Options: Audio Toggle, Copy, Memory Status */}
        <div className="flex items-center justify-between mb-2 text-xs text-neutral-400">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setSoundEnabled((prev) => !prev)}
              className="p-1.5 rounded-lg hover:bg-neutral-800 text-neutral-400 hover:text-white transition-colors flex items-center gap-1"
              title={soundEnabled ? 'Desativar som de clique' : 'Ativar som de clique'}
              aria-label={soundEnabled ? 'Desativar som de clique' : 'Ativar som de clique'}
            >
              {soundEnabled ? (
                <Volume2 className="w-3.5 h-3.5 text-orange-400" />
              ) : (
                <VolumeX className="w-3.5 h-3.5 text-neutral-500" />
              )}
              <span className="text-[10px] font-medium hidden sm:inline">
                {soundEnabled ? 'Som' : 'Mudo'}
              </span>
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleCopyDisplay}
              className="px-2 py-1 rounded-lg hover:bg-neutral-800 text-neutral-400 hover:text-white transition-colors flex items-center gap-1 text-[11px]"
              title="Copiar resultado atual"
              aria-label="Copiar resultado"
            >
              {copiedDisplay ? (
                <>
                  <Check className="w-3 h-3 text-emerald-400" />
                  <span className="text-emerald-400 font-medium">Copiado</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3 text-neutral-400" />
                  <span className="text-neutral-400 font-mono-calc">Copiar</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Display Screen */}
        <div className="bg-[#181a22] border border-neutral-800/80 rounded-2xl p-4 sm:p-5 flex flex-col justify-end min-h-[110px] mb-5 shadow-inner">
          {/* Secondary Expression Display */}
          <div className="h-6 text-right text-xs font-mono-calc text-neutral-400 overflow-hidden text-ellipsis whitespace-nowrap">
            {state.lastCalculatedExpression ? (
              <span className="text-neutral-400">{state.lastCalculatedExpression} =</span>
            ) : state.previousValue !== null && state.operator !== null ? (
              <span className="text-orange-400/90 font-medium">
                {state.previousValue} {state.operator}
              </span>
            ) : (
              <span className="opacity-0">0</span>
            )}
          </div>

          {/* Main Number Display (Crisp White Minimalist Font) */}
          <div
            className={`text-right font-mono-calc font-semibold text-white tracking-tight leading-none mt-1 transition-all overflow-x-auto select-all ${getDisplayFontSize(
              state.displayValue
            )}`}
            aria-live="polite"
            data-testid="calculator-display"
          >
            {state.displayValue}
          </div>
        </div>

        {/* Keypad Grid (Dark gray rounded buttons + Vibrant Orange action buttons) */}
        <div className="grid grid-cols-4 gap-2.5 sm:gap-3">
          {/* Row 1: C, ±, %, ÷ */}
          <button
            type="button"
            onClick={() => {
              playKeyClick('clear', soundEnabled);
              setState((prev) => clearAll(prev));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#262832] hover:bg-[#323643] active:bg-[#3c4150] text-[#ff8c38] font-bold text-lg sm:text-xl transition-all flex items-center justify-center border border-neutral-700/50 shadow-md active:scale-95 ${
              activeButton === 'C' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            aria-label="Limpar calculadora (C)"
          >
            C
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('num', soundEnabled);
              setState((prev) => toggleSign(prev));
            }}
            className="h-14 sm:h-16 rounded-2xl bg-[#22242d] hover:bg-[#2d303b] active:bg-[#383c4a] text-neutral-200 font-semibold text-lg sm:text-xl transition-all flex items-center justify-center border border-neutral-800 shadow-md active:scale-95"
            aria-label="Alternar positivo e negativo (±)"
          >
            ±
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('num', soundEnabled);
              setState((prev) => inputPercent(prev));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#22242d] hover:bg-[#2d303b] active:bg-[#383c4a] text-neutral-200 font-semibold text-lg sm:text-xl transition-all flex items-center justify-center border border-neutral-800 shadow-md active:scale-95 ${
              activeButton === '%' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            aria-label="Porcentagem (%)"
          >
            <Percent className="w-5 h-5 text-neutral-300" />
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('op', soundEnabled);
              setState((prev) => handleOperator(prev, '÷'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-orange-500 hover:bg-orange-600 active:bg-orange-700 text-white font-bold text-xl sm:text-2xl transition-all flex items-center justify-center shadow-lg shadow-orange-500/25 active:scale-95 border border-orange-400/30 ${
              state.operator === '÷' || activeButton === '÷'
                ? 'ring-2 ring-white/60 bg-orange-600'
                : ''
            }`}
            aria-label="Dividir (÷)"
          >
            <Divide className="w-6 h-6 stroke-[2.5]" />
          </button>

          {/* Row 2: 7, 8, 9, × */}
          <button
            type="button"
            onClick={() => {
              playKeyClick('num', soundEnabled);
              setState((prev) => inputDigit(prev, '7'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#1f2129] hover:bg-[#292c36] active:bg-[#343845] text-white font-mono-calc font-semibold text-xl sm:text-2xl transition-all flex items-center justify-center border border-neutral-800/80 shadow-md active:scale-95 ${
              activeButton === '7' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            aria-label="7"
          >
            7
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('num', soundEnabled);
              setState((prev) => inputDigit(prev, '8'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#1f2129] hover:bg-[#292c36] active:bg-[#343845] text-white font-mono-calc font-semibold text-xl sm:text-2xl transition-all flex items-center justify-center border border-neutral-800/80 shadow-md active:scale-95 ${
              activeButton === '8' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            aria-label="8"
          >
            8
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('num', soundEnabled);
              setState((prev) => inputDigit(prev, '9'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#1f2129] hover:bg-[#292c36] active:bg-[#343845] text-white font-mono-calc font-semibold text-xl sm:text-2xl transition-all flex items-center justify-center border border-neutral-800/80 shadow-md active:scale-95 ${
              activeButton === '9' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            aria-label="9"
          >
            9
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('op', soundEnabled);
              setState((prev) => handleOperator(prev, '×'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-orange-500 hover:bg-orange-600 active:bg-orange-700 text-white font-bold text-xl sm:text-2xl transition-all flex items-center justify-center shadow-lg shadow-orange-500/25 active:scale-95 border border-orange-400/30 ${
              state.operator === '×' || activeButton === '×'
                ? 'ring-2 ring-white/60 bg-orange-600'
                : ''
            }`}
            aria-label="Multiplicar (×)"
          >
            <X className="w-5 h-5 stroke-[2.5]" />
          </button>

          {/* Row 3: 4, 5, 6, - */}
          <button
            type="button"
            onClick={() => {
              playKeyClick('num', soundEnabled);
              setState((prev) => inputDigit(prev, '4'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#1f2129] hover:bg-[#292c36] active:bg-[#343845] text-white font-mono-calc font-semibold text-xl sm:text-2xl transition-all flex items-center justify-center border border-neutral-800/80 shadow-md active:scale-95 ${
              activeButton === '4' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            aria-label="4"
          >
            4
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('num', soundEnabled);
              setState((prev) => inputDigit(prev, '5'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#1f2129] hover:bg-[#292c36] active:bg-[#343845] text-white font-mono-calc font-semibold text-xl sm:text-2xl transition-all flex items-center justify-center border border-neutral-800/80 shadow-md active:scale-95 ${
              activeButton === '5' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            aria-label="5"
          >
            5
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('num', soundEnabled);
              setState((prev) => inputDigit(prev, '6'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#1f2129] hover:bg-[#292c36] active:bg-[#343845] text-white font-mono-calc font-semibold text-xl sm:text-2xl transition-all flex items-center justify-center border border-neutral-800/80 shadow-md active:scale-95 ${
              activeButton === '6' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            aria-label="6"
          >
            6
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('op', soundEnabled);
              setState((prev) => handleOperator(prev, '-'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-orange-500 hover:bg-orange-600 active:bg-orange-700 text-white font-bold text-xl sm:text-2xl transition-all flex items-center justify-center shadow-lg shadow-orange-500/25 active:scale-95 border border-orange-400/30 ${
              state.operator === '-' || activeButton === '-'
                ? 'ring-2 ring-white/60 bg-orange-600'
                : ''
            }`}
            aria-label="Subtrair (-)"
          >
            <Minus className="w-5 h-5 stroke-[2.5]" />
          </button>

          {/* Row 4: 1, 2, 3, + */}
          <button
            type="button"
            onClick={() => {
              playKeyClick('num', soundEnabled);
              setState((prev) => inputDigit(prev, '1'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#1f2129] hover:bg-[#292c36] active:bg-[#343845] text-white font-mono-calc font-semibold text-xl sm:text-2xl transition-all flex items-center justify-center border border-neutral-800/80 shadow-md active:scale-95 ${
              activeButton === '1' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            aria-label="1"
          >
            1
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('num', soundEnabled);
              setState((prev) => inputDigit(prev, '2'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#1f2129] hover:bg-[#292c36] active:bg-[#343845] text-white font-mono-calc font-semibold text-xl sm:text-2xl transition-all flex items-center justify-center border border-neutral-800/80 shadow-md active:scale-95 ${
              activeButton === '2' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            aria-label="2"
          >
            2
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('num', soundEnabled);
              setState((prev) => inputDigit(prev, '3'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#1f2129] hover:bg-[#292c36] active:bg-[#343845] text-white font-mono-calc font-semibold text-xl sm:text-2xl transition-all flex items-center justify-center border border-neutral-800/80 shadow-md active:scale-95 ${
              activeButton === '3' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            aria-label="3"
          >
            3
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('op', soundEnabled);
              setState((prev) => handleOperator(prev, '+'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-orange-500 hover:bg-orange-600 active:bg-orange-700 text-white font-bold text-xl sm:text-2xl transition-all flex items-center justify-center shadow-lg shadow-orange-500/25 active:scale-95 border border-orange-400/30 ${
              state.operator === '+' || activeButton === '+'
                ? 'ring-2 ring-white/60 bg-orange-600'
                : ''
            }`}
            aria-label="Somar (+)"
          >
            <Plus className="w-5 h-5 stroke-[2.5]" />
          </button>

          {/* Row 5: 0, ., ⌫, = */}
          <button
            type="button"
            onClick={() => {
              playKeyClick('num', soundEnabled);
              setState((prev) => inputDigit(prev, '0'));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#1f2129] hover:bg-[#292c36] active:bg-[#343845] text-white font-mono-calc font-semibold text-xl sm:text-2xl transition-all flex items-center justify-center border border-neutral-800/80 shadow-md active:scale-95 ${
              activeButton === '0' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            aria-label="0"
          >
            0
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('num', soundEnabled);
              setState((prev) => inputDecimal(prev));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#1f2129] hover:bg-[#292c36] active:bg-[#343845] text-white font-mono-calc font-semibold text-xl sm:text-2xl transition-all flex items-center justify-center border border-neutral-800/80 shadow-md active:scale-95 ${
              activeButton === '.' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            aria-label="Ponto decimal (.)"
          >
            .
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('clear', soundEnabled);
              setState((prev) => backspace(prev));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-[#22242d] hover:bg-[#2d303b] active:bg-[#383c4a] text-neutral-300 font-semibold text-lg transition-all flex items-center justify-center border border-neutral-800 shadow-md active:scale-95 ${
              activeButton === 'backspace' ? 'ring-2 ring-orange-400 scale-95' : ''
            }`}
            title="Apagar último dígito (Backspace)"
            aria-label="Apagar último dígito"
          >
            <Delete className="w-5 h-5" />
          </button>

          <button
            type="button"
            onClick={() => {
              playKeyClick('eq', soundEnabled);
              setState((prev) => calculateEquals(prev));
            }}
            className={`h-14 sm:h-16 rounded-2xl bg-orange-500 hover:bg-orange-600 active:bg-orange-700 text-white font-bold text-2xl sm:text-3xl transition-all flex items-center justify-center shadow-lg shadow-orange-500/35 active:scale-95 border border-orange-400/40 ${
              activeButton === '=' ? 'ring-2 ring-white scale-95 bg-orange-600' : ''
            }`}
            title="Calcular resultado (=)"
            aria-label="Igual / Calcular resultado (=)"
          >
            <Equal className="w-7 h-7 stroke-[2.8]" />
          </button>
        </div>
      </div>

      {/* Memory Drawer (5 Últimos Cálculos) */}
      <MemoryPanel
        history={state.history}
        isOpen={isMemoryOpen}
        onSelect={(item) => {
          setState((prev) => recallHistoryItem(prev, item));
        }}
        onClear={() => {
          setState((prev) => clearHistory(prev));
        }}
      />
    </div>
  );
};
