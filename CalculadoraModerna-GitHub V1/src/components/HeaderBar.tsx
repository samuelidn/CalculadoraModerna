import React from 'react';
import {
  FileCode2,
  History,
  Keyboard,
} from 'lucide-react';

interface HeaderBarProps {
  historyCount: number;
  onOpenPythonGuide: () => void;
  onToggleMemory: () => void;
  isMemoryOpen: boolean;
  onToggleKeyboardGuide: () => void;
}

export const HeaderBar: React.FC<HeaderBarProps> = ({
  historyCount,
  onOpenPythonGuide,
  onToggleMemory,
  isMemoryOpen,
  onToggleKeyboardGuide,
}) => {
  return (
    <header className="w-full max-w-md mx-auto mb-3 sm:mb-4 flex items-center justify-between px-3 py-2 sm:py-2.5 rounded-2xl bg-[#14161d]/90 backdrop-blur-md border border-neutral-800/80 shadow-lg">
      {/* Window dots (Mac/Desktop style) */}
      <div className="flex items-center gap-1.5 sm:gap-2">
        <div className="flex items-center gap-1 sm:gap-1.5 mr-1">
          <span className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-red-500/80 inline-block" />
          <span className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-yellow-500/80 inline-block" />
          <span className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-emerald-500/80 inline-block" />
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-bold text-white tracking-wide">
            Calculadora
          </span>
          <span className="hidden sm:inline-block text-[10px] font-semibold text-orange-400 bg-orange-500/10 border border-orange-500/20 px-1.5 py-0.2 rounded-full">
            Python
          </span>
        </div>
      </div>

      {/* Navigation & actions */}
      <div className="flex items-center gap-1 sm:gap-1.5">
        <button
          type="button"
          onClick={onToggleMemory}
          className={`px-2 sm:px-2.5 py-1.5 rounded-xl text-xs font-medium transition-all flex items-center gap-1 sm:gap-1.5 border ${
            isMemoryOpen
              ? 'bg-orange-500/20 text-orange-400 border-orange-500/40'
              : 'bg-[#1e2028] text-neutral-300 hover:text-white border-neutral-800 hover:border-neutral-700'
          }`}
          title="Histórico dos 5 últimos cálculos"
          aria-label="Abrir memória dos 5 últimos cálculos"
        >
          <History className="w-3.5 h-3.5 text-orange-400 shrink-0" />
          <span className="hidden min-[360px]:inline text-[11px] sm:text-xs">Memória</span>
          {historyCount > 0 && (
            <span className="text-[10px] font-bold px-1.5 py-0.2 rounded-full bg-orange-500 text-white leading-tight">
              {historyCount}
            </span>
          )}
        </button>

        <button
          type="button"
          onClick={onOpenPythonGuide}
          className="px-2.5 sm:px-3 py-1.5 rounded-xl text-xs font-semibold bg-orange-500 hover:bg-orange-600 text-white shadow-md shadow-orange-500/20 flex items-center gap-1 sm:gap-1.5 transition-all active:scale-95 shrink-0"
          title="Baixar código Python e guia de instalação no PC"
          aria-label="Código Python e guia de instalação"
        >
          <FileCode2 className="w-3.5 h-3.5 shrink-0" />
          <span className="text-[11px] sm:text-xs">Python</span>
        </button>

        <button
          type="button"
          onClick={onToggleKeyboardGuide}
          className="p-1.5 rounded-xl text-neutral-400 hover:text-white bg-[#1e2028] border border-neutral-800 hover:border-neutral-700 transition-colors shrink-0"
          title="Ver atalhos do teclado"
          aria-label="Atalhos do teclado"
        >
          <Keyboard className="w-3.5 h-3.5" />
        </button>
      </div>
    </header>
  );
};
