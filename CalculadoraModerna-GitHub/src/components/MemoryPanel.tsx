import React from 'react';
import { History, Trash2, ArrowUpRight, Clock } from 'lucide-react';
import { CalculationHistoryItem, MAX_HISTORY_ITEMS } from '../utils/calculator';

interface MemoryPanelProps {
  history: CalculationHistoryItem[];
  onSelect: (item: CalculationHistoryItem) => void;
  onClear: () => void;
  isOpen: boolean;
  onClose?: () => void;
}

export const MemoryPanel: React.FC<MemoryPanelProps> = ({
  history,
  onSelect,
  onClear,
  isOpen,
}) => {
  if (!isOpen) return null;

  return (
    <div
      className="bg-[#16171d] border border-neutral-800 rounded-2xl p-4 flex flex-col gap-3 shadow-xl transition-all"
      data-testid="memory-panel"
    >
      <div className="flex items-center justify-between pb-2 border-b border-neutral-800/80">
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-orange-500" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-neutral-300">
            Memória ({history.length}/{MAX_HISTORY_ITEMS})
          </h3>
        </div>

        {history.length > 0 && (
          <button
            type="button"
            onClick={onClear}
            className="text-xs text-neutral-400 hover:text-red-400 flex items-center gap-1 transition-colors px-2 py-1 rounded-md hover:bg-neutral-800/50"
            title="Limpar memória"
            aria-label="Limpar histórico de cálculos"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Limpar</span>
          </button>
        )}
      </div>

      {history.length === 0 ? (
        <div className="py-6 text-center text-neutral-500 text-xs">
          Nenhum cálculo em memória ainda. Realize cálculos pressionando '=' para vê-los aqui (máximo de 5).
        </div>
      ) : (
        <ul className="flex flex-col gap-2 max-h-60 overflow-y-auto pr-1">
          {history.map((item, idx) => (
            <li
              key={item.id}
              className="group flex items-center justify-between p-2.5 rounded-xl bg-[#1e2027] hover:bg-[#252831] border border-neutral-800/60 hover:border-orange-500/30 transition-all cursor-pointer"
              onClick={() => onSelect(item)}
              title="Clique para carregar este resultado na calculadora"
            >
              <div className="flex flex-col">
                <span className="text-[11px] text-neutral-400 font-mono-calc">
                  {item.expression}
                </span>
                <span className="text-sm font-semibold text-white font-mono-calc flex items-center gap-1.5">
                  = {item.result}
                  {idx === 0 && (
                    <span className="text-[9px] uppercase px-1.5 py-0.5 rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/20 font-sans">
                      Último
                    </span>
                  )}
                </span>
              </div>

              <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center text-xs text-orange-400 gap-1 bg-orange-500/10 px-2 py-1 rounded-lg">
                <span>Usar</span>
                <ArrowUpRight className="w-3 h-3" />
              </div>
            </li>
          ))}
        </ul>
      )}

      <div className="text-[10px] text-neutral-500 text-center flex items-center justify-center gap-1 pt-1">
        <Clock className="w-3 h-3 text-neutral-500" />
        <span>Salva em memória local estritamente os últimos 5 cálculos</span>
      </div>
    </div>
  );
};
