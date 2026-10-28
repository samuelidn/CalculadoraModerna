import React from 'react';
import { Keyboard, X } from 'lucide-react';

interface KeyboardGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SHORTCUTS = [
  { key: '0 - 9', desc: 'Inserir números' },
  { key: '+', desc: 'Soma / Adição' },
  { key: '-', desc: 'Subtração' },
  { key: '* ou x', desc: 'Multiplicação' },
  { key: '/', desc: 'Divisão' },
  { key: '%', desc: 'Porcentagem' },
  { key: '. ou ,', desc: 'Ponto decimal' },
  { key: 'Enter ou =', desc: 'Calcular resultado' },
  { key: 'Backspace', desc: 'Apagar último dígito' },
  { key: 'Esc ou C', desc: 'Limpar tudo' },
];

export const KeyboardGuideModal: React.FC<KeyboardGuideModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="shortcuts-title"
    >
      <div className="bg-[#14151b] border border-neutral-800 rounded-3xl w-full max-w-md p-5 shadow-2xl">
        <div className="flex items-center justify-between pb-3 border-b border-neutral-800">
          <div className="flex items-center gap-2">
            <Keyboard className="w-4 h-4 text-orange-400" />
            <h3 id="shortcuts-title" className="text-sm font-bold text-white">
              Atalhos do Teclado
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-neutral-400 hover:text-white p-1 rounded-lg hover:bg-neutral-800 transition-colors"
            aria-label="Fechar atalhos"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <p className="text-xs text-neutral-400 mt-2 mb-4">
          Você pode usar diretamente o teclado físico ou teclado numérico do seu computador:
        </p>

        <div className="grid grid-cols-2 gap-2 text-xs">
          {SHORTCUTS.map((item, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-2 rounded-xl bg-[#1c1e26] border border-neutral-800"
            >
              <kbd className="px-2 py-0.5 rounded-md bg-[#282a36] border border-neutral-700 text-orange-400 font-mono-calc font-semibold text-[11px]">
                {item.key}
              </kbd>
              <span className="text-neutral-300 text-[11px] text-right">{item.desc}</span>
            </div>
          ))}
        </div>

        <div className="mt-5 pt-3 border-t border-neutral-800 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-orange-500 hover:bg-orange-600 text-white font-semibold text-xs transition-colors"
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
};
