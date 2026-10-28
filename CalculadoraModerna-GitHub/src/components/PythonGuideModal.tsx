import React, { useState } from 'react';
import {
  Download,
  Copy,
  Check,
  Terminal,
  FileCode2,
  PackageCheck,
  Sparkles,
  Info,
  Layers,
} from 'lucide-react';
import {
  PYTHON_CALCULATOR_CODE,
  PYTHON_CALCULATOR_CORE_CODE,
  INSTALL_INSTRUCTIONS_PT,
} from '../data/pythonCode';

interface PythonGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PythonGuideModal: React.FC<PythonGuideModalProps> = ({ isOpen, onClose }) => {
  const [copiedCode, setCopiedCode] = useState(false);
  const [copiedCommandIdx, setCopiedCommandIdx] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'install' | 'code_app' | 'code_core'>('install');

  if (!isOpen) return null;

  const getActiveCode = () => {
    return activeTab === 'code_core' ? PYTHON_CALCULATOR_CORE_CODE : PYTHON_CALCULATOR_CODE;
  };

  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(getActiveCode());
      setCopiedCode(true);
      setTimeout(() => setCopiedCode(false), 2200);
    } catch {
      // fallback
    }
  };

  const handleCopyCommand = async (cmd: string, index: number) => {
    try {
      await navigator.clipboard.writeText(cmd);
      setCopiedCommandIdx(index);
      setTimeout(() => setCopiedCommandIdx(null), 2000);
    } catch {
      // fallback
    }
  };

  const handleDownloadFile = (filename: string, content: string) => {
    const blob = new Blob([content], { type: 'text/x-python;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="python-modal-title"
    >
      <div className="bg-[#13141a] border border-neutral-800 rounded-3xl w-full max-w-3xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-neutral-800 bg-[#161820]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-orange-500/10 border border-orange-500/30 flex items-center justify-center text-orange-400">
              <FileCode2 className="w-5 h-5" />
            </div>
            <div>
              <h2 id="python-modal-title" className="text-base font-bold text-white flex items-center gap-2">
                Calculadora Moderna Python (Desktop v2.0)
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-orange-500/20 text-orange-400 border border-orange-500/30">
                  Científica & Básica
                </span>
              </h2>
              <p className="text-xs text-neutral-400">
                Aplicativo nativo para Windows/Linux/Mac com abertura maximizada, tela cheia (F11/Esc) e histórico persistente
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="text-neutral-400 hover:text-white p-2 rounded-xl hover:bg-neutral-800 transition-colors"
            aria-label="Fechar modal"
          >
            ✕
          </button>
        </div>

        {/* Tab selection & download buttons */}
        <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-[#111217] border-b border-neutral-800/80">
          <div className="flex items-center gap-1 bg-[#1a1c24] p-1 rounded-xl border border-neutral-800">
            <button
              type="button"
              onClick={() => setActiveTab('install')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                activeTab === 'install'
                  ? 'bg-orange-500 text-white shadow-md shadow-orange-500/20'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              <Terminal className="w-3.5 h-3.5" />
              Guia de Instalação (.exe)
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('code_app')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                activeTab === 'code_app'
                  ? 'bg-orange-500 text-white shadow-md shadow-orange-500/20'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              <FileCode2 className="w-3.5 h-3.5" />
              calculadora.py
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('code_core')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                activeTab === 'code_core'
                  ? 'bg-orange-500 text-white shadow-md shadow-orange-500/20'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              calculadora_core.py
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleCopyCode}
              className="px-3 py-1.5 rounded-xl text-xs font-medium bg-[#1e2028] hover:bg-[#282a36] text-neutral-200 border border-neutral-700/80 hover:border-neutral-600 flex items-center gap-1.5 transition-all"
            >
              {copiedCode ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copiado!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-neutral-400" />
                  <span>Copiar Código</span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={() => handleDownloadFile('calculadora.py', PYTHON_CALCULATOR_CODE)}
              className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-orange-500 hover:bg-orange-600 text-white shadow-lg shadow-orange-500/20 flex items-center gap-1.5 transition-all active:scale-95"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Baixar calculadora.py</span>
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {activeTab === 'install' ? (
            <div className="space-y-4">
              <div className="bg-orange-500/10 border border-orange-500/20 rounded-2xl p-4 flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-orange-400 shrink-0 mt-0.5" />
                <div className="text-xs text-neutral-300 leading-relaxed">
                  <strong className="text-white">Evolução Completa v2.0:</strong> Abas <strong>Básica</strong> e{' '}
                  <strong>Científica</strong> (trigonometria, DEG/RAD, log10, ln, raiz, potências, fatorial n!, parênteses, pi e e),
                  avaliador seguro via AST (sem eval inseguro), histórico dos 5 cálculos em cartões visuais com data/hora e persistência em JSON em{' '}
                  <code className="text-orange-300 font-mono-calc">%APPDATA%\CalculadoraModerna\historico.json</code>.
                </div>
              </div>

              <div className="grid gap-3">
                {INSTALL_INSTRUCTIONS_PT.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-2xl bg-[#181a22] border border-neutral-800/80 hover:border-neutral-700 transition-all flex flex-col gap-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-orange-400">{item.step}</span>
                      <span className="text-xs font-medium text-white">{item.title}</span>
                    </div>

                    <p className="text-xs text-neutral-400">{item.description}</p>

                    <div className="flex items-center justify-between bg-[#0e0f14] border border-neutral-800 rounded-xl px-3 py-2 mt-1 font-mono-calc text-xs text-neutral-200">
                      <code className="text-orange-300 select-all">{item.command}</code>
                      <button
                        type="button"
                        onClick={() => handleCopyCommand(item.command, idx)}
                        className="text-neutral-400 hover:text-white p-1 rounded hover:bg-neutral-800 transition-colors ml-2"
                        title="Copiar comando"
                        aria-label={`Copiar comando: ${item.command}`}
                      >
                        {copiedCommandIdx === idx ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-4 rounded-2xl bg-[#14151b] border border-neutral-800 text-xs text-neutral-400 flex items-start gap-2.5">
                <Info className="w-4 h-4 text-neutral-400 shrink-0 mt-0.5" />
                <span>
                  <strong>Atalhos no Windows:</strong> Pressione <kbd className="text-orange-300 px-1 py-0.5 rounded bg-neutral-800 font-mono-calc">F11</kbd> para alternar o modo tela cheia e <kbd className="text-orange-300 px-1 py-0.5 rounded bg-neutral-800 font-mono-calc">Esc</kbd> para sair. O botão de cópia envia o resultado para a área de transferência do Windows.
                </span>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs text-neutral-400">
                <span>
                  Arquivo exibido: <strong className="text-white">{activeTab === 'code_core' ? 'calculadora_core.py' : 'calculadora.py'}</strong>
                </span>
                <button
                  type="button"
                  onClick={() =>
                    handleDownloadFile(
                      activeTab === 'code_core' ? 'calculadora_core.py' : 'calculadora.py',
                      getActiveCode()
                    )
                  }
                  className="text-orange-400 hover:underline flex items-center gap-1 font-medium"
                >
                  <Download className="w-3.5 h-3.5" />
                  Baixar este arquivo
                </button>
              </div>
              <div className="bg-[#0b0c10] border border-neutral-800 rounded-2xl p-4 font-mono-calc text-xs text-neutral-300 overflow-x-auto max-h-[50vh] leading-relaxed">
                <pre>{getActiveCode()}</pre>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-neutral-800 bg-[#14161d] flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-neutral-400">
            <PackageCheck className="w-4 h-4 text-emerald-400" />
            <span>Persistência local em JSON (%APPDATA%\CalculadoraModerna\historico.json)</span>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-neutral-800 hover:bg-neutral-700 text-white transition-colors"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
};
