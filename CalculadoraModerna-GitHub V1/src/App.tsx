/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { HeaderBar } from './components/HeaderBar';
import { Calculator } from './components/Calculator';
import { PythonGuideModal } from './components/PythonGuideModal';
import { KeyboardGuideModal } from './components/KeyboardGuideModal';
import { Terminal, Download, Laptop, ShieldCheck } from 'lucide-react';

export default function App() {
  const [historyCount, setHistoryCount] = useState<number>(0);
  const [isMemoryOpen, setIsMemoryOpen] = useState<boolean>(true);
  const [isPythonModalOpen, setIsPythonModalOpen] = useState<boolean>(false);
  const [isKeyboardModalOpen, setIsKeyboardModalOpen] = useState<boolean>(false);

  return (
    <div className="min-h-screen bg-[#0a0a0e] text-white flex flex-col justify-between p-3 sm:p-6 selection:bg-orange-500 selection:text-white">
      {/* Background ambient lighting */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-orange-600/5 rounded-full blur-[140px]" />
        <div className="absolute bottom-10 right-10 w-[300px] h-[300px] bg-orange-500/5 rounded-full blur-[100px]" />
      </div>

      <div className="relative z-10 w-full max-w-lg mx-auto flex flex-col items-center">
        {/* Header Bar */}
        <HeaderBar
          historyCount={historyCount}
          onOpenPythonGuide={() => setIsPythonModalOpen(true)}
          onToggleMemory={() => setIsMemoryOpen((prev) => !prev)}
          isMemoryOpen={isMemoryOpen}
          onToggleKeyboardGuide={() => setIsKeyboardModalOpen(true)}
        />

        {/* Calculator Widget */}
        <main className="w-full">
          <Calculator
            onHistoryChange={setHistoryCount}
            isMemoryOpen={isMemoryOpen}
            onToggleMemory={() => setIsMemoryOpen((prev) => !prev)}
          />
        </main>

        {/* Quick banner to install or run Python */}
        <div className="w-full max-w-md mt-4 p-3 rounded-2xl bg-[#14151d]/90 border border-neutral-800/80 flex items-center justify-between text-xs text-neutral-400 backdrop-blur-md">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Pronto para rodar no seu computador</span>
          </div>
          <button
            type="button"
            onClick={() => setIsPythonModalOpen(true)}
            className="text-orange-400 hover:text-orange-300 font-medium flex items-center gap-1 hover:underline"
          >
            <span>Ver script Python</span>
            <span>→</span>
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 w-full max-w-md mx-auto mt-6 text-center text-[11px] text-neutral-500 flex flex-col sm:flex-row items-center justify-between gap-2 border-t border-neutral-900 pt-3">
        <span>Calculadora com Memória (5 últimos cálculos)</span>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setIsKeyboardModalOpen(true)}
            className="hover:text-neutral-300 transition-colors"
          >
            Atalhos
          </button>
          <span>•</span>
          <button
            type="button"
            onClick={() => setIsPythonModalOpen(true)}
            className="hover:text-orange-400 transition-colors"
          >
            Instalação PC (.py)
          </button>
        </div>
      </footer>

      {/* Modals */}
      <PythonGuideModal
        isOpen={isPythonModalOpen}
        onClose={() => setIsPythonModalOpen(false)}
      />

      <KeyboardGuideModal
        isOpen={isKeyboardModalOpen}
        onClose={() => setIsKeyboardModalOpen(false)}
      />
    </div>
  );
}
