"""
Suíte de testes unitários da Calculadora Moderna em Python.
Testa o avaliador seguro AST, precedência de operadores, funções científicas,
modo DEG/RAD, tratamento de erros, formatação numérica e persistência do histórico em JSON.
"""

import math
import os
import tempfile
import unittest
from pathlib import Path

from calculadora_core import (
    HistoryManager,
    MathEvaluationError,
    SafeMathEvaluator,
    SoundManager,
    format_number,
)


class TestSafeMathEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = SafeMathEvaluator(angle_mode="DEG")

    def test_basic_arithmetic(self):
        self.assertEqual(self.evaluator.evaluate("25 + 75"), 100.0)
        self.assertEqual(self.evaluator.evaluate("100 - 35"), 65.0)
        self.assertEqual(self.evaluator.evaluate("12 * 4"), 48.0)
        self.assertEqual(self.evaluator.evaluate("50 / 2"), 25.0)
        self.assertEqual(self.evaluator.evaluate("10 % 3"), 1.0)

    def test_friendly_symbols(self):
        # Testa símbolos ×, ÷, virgula como ponto
        self.assertEqual(self.evaluator.evaluate("12 × 4"), 48.0)
        self.assertEqual(self.evaluator.evaluate("50 ÷ 2"), 25.0)
        self.assertEqual(self.evaluator.evaluate("3,5 + 2,5"), 6.0)

    def test_operator_precedence(self):
        # Multiplicação antes da adição
        self.assertEqual(self.evaluator.evaluate("2 + 3 * 4"), 14.0)
        # Parênteses alterando precedência
        self.assertEqual(self.evaluator.evaluate("(2 + 3) * 4"), 20.0)
        self.assertEqual(self.evaluator.evaluate("10 - 2 * 3 + 4 / 2"), 6.0)

    def test_powers_and_square_root(self):
        self.assertEqual(self.evaluator.evaluate("2 ^ 3"), 8.0)
        self.assertEqual(self.evaluator.evaluate("5 ^ 2"), 25.0)
        self.assertEqual(self.evaluator.evaluate("sqrt(49)"), 7.0)
        self.assertEqual(self.evaluator.evaluate("√(16)"), 4.0)

    def test_percentage(self):
        self.assertEqual(self.evaluator.evaluate("50%"), 0.5)
        self.assertEqual(self.evaluator.evaluate("200 * 10%"), 20.0)

    def test_constants(self):
        self.assertAlmostEqual(self.evaluator.evaluate("pi"), math.pi)
        self.assertAlmostEqual(self.evaluator.evaluate("π"), math.pi)
        self.assertAlmostEqual(self.evaluator.evaluate("e"), math.e)
        self.assertAlmostEqual(self.evaluator.evaluate("2 * pi"), 2 * math.pi)

    def test_logarithms(self):
        self.assertAlmostEqual(self.evaluator.evaluate("log(100)"), 2.0)
        self.assertAlmostEqual(self.evaluator.evaluate("log(1000)"), 3.0)
        self.assertAlmostEqual(self.evaluator.evaluate("ln(e)"), 1.0)

    def test_trigonometry_deg(self):
        self.evaluator.set_angle_mode("DEG")
        self.assertAlmostEqual(self.evaluator.evaluate("sin(30)"), 0.5, places=5)
        self.assertAlmostEqual(self.evaluator.evaluate("cos(60)"), 0.5, places=5)
        self.assertAlmostEqual(self.evaluator.evaluate("tan(45)"), 1.0, places=5)
        self.assertAlmostEqual(self.evaluator.evaluate("asin(0.5)"), 30.0, places=5)
        self.assertAlmostEqual(self.evaluator.evaluate("acos(0.5)"), 60.0, places=5)
        self.assertAlmostEqual(self.evaluator.evaluate("atan(1)"), 45.0, places=5)

    def test_trigonometry_rad(self):
        self.evaluator.set_angle_mode("RAD")
        self.assertAlmostEqual(self.evaluator.evaluate("sin(pi / 2)"), 1.0, places=5)
        self.assertAlmostEqual(self.evaluator.evaluate("cos(pi)"), -1.0, places=5)

    def test_factorial(self):
        self.assertEqual(self.evaluator.evaluate("fact(5)"), 120)
        self.assertEqual(self.evaluator.evaluate("5!"), 120)
        self.assertEqual(self.evaluator.evaluate("fact(0)"), 1)

    def test_mathematical_errors(self):
        # Divisão por zero
        with self.assertRaises(MathEvaluationError):
            self.evaluator.evaluate("10 / 0")

        # Raiz de número negativo
        with self.assertRaises(MathEvaluationError):
            self.evaluator.evaluate("sqrt(-25)")

        # Logaritmo de número negativo ou zero
        with self.assertRaises(MathEvaluationError):
            self.evaluator.evaluate("log(0)")
        with self.assertRaises(MathEvaluationError):
            self.evaluator.evaluate("ln(-10)")

        # Fatorial de negativo ou não-inteiro
        with self.assertRaises(MathEvaluationError):
            self.evaluator.evaluate("fact(-3)")
        with self.assertRaises(MathEvaluationError):
            self.evaluator.evaluate("fact(3.5)")

        # Domínio inválido para arco-seno
        with self.assertRaises(MathEvaluationError):
            self.evaluator.evaluate("asin(2)")

    def test_security_ast_sandbox(self):
        # Nenhuma injeção de código ou funções não autorizadas deve ser permitida
        malicious_inputs = [
            "__import__('os').system('ls')",
            "open('/etc/passwd')",
            "eval('2+2')",
            "exec('x = 1')",
            "globals()",
            "[x for x in (1, 2)]",
        ]
        for malicious in malicious_inputs:
            with self.assertRaises((MathEvaluationError, Exception)):
                self.evaluator.evaluate(malicious)


class TestNumberFormatting(unittest.TestCase):
    def test_floating_point_artifacts(self):
        # 0.1 + 0.2 no Python normalmente dá 0.30000000000000004
        val = 0.1 + 0.2
        self.assertEqual(format_number(val), "0.3")

    def test_integer_formatting(self):
        self.assertEqual(format_number(4.0), "4")
        self.assertEqual(format_number(100.0), "100")
        self.assertEqual(format_number(0.0), "0")

    def test_regular_decimals(self):
        self.assertEqual(format_number(3.14159), "3.14159")
        self.assertEqual(format_number(2.5), "2.5")


class TestHistoryManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.history_file = Path(self.temp_dir.name) / "test_historico.json"
        self.history_manager = HistoryManager(custom_path=self.history_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_strict_5_limit(self):
        for i in range(1, 8):
            self.history_manager.add_entry(f"{i} + 1", str(i + 1))

        # Deve conter exatamente 5 itens
        self.assertEqual(len(self.history_manager.history), 5)
        # Mais recente no topo (7 + 1 = 8)
        self.assertEqual(self.history_manager.history[0]["expression"], "7 + 1")
        self.assertEqual(self.history_manager.history[0]["result"], "8")
        # Item mais antigo retido é o 3 + 1 = 4
        self.assertEqual(self.history_manager.history[-1]["expression"], "3 + 1")
        self.assertEqual(self.history_manager.history[-1]["result"], "4")

    def test_persistence_reload(self):
        # Salva dados
        self.history_manager.add_entry("10 * 5", "50")
        self.history_manager.add_entry("20 / 2", "10")

        # Cria nova instância apontando para o mesmo arquivo (simula fechar e reabrir o app)
        new_manager = HistoryManager(custom_path=self.history_file)
        self.assertEqual(len(new_manager.history), 2)
        self.assertEqual(new_manager.history[0]["expression"], "20 / 2")
        self.assertEqual(new_manager.history[0]["result"], "10")

    def test_corrupted_json_recovery(self):
        # Escreve arquivo JSON corrompido
        with open(self.history_file, "w") as f:
            f.write("{invalid json content!!!")

        # Não deve levantar exceção, deve iniciar com lista vazia
        manager = HistoryManager(custom_path=self.history_file)
        self.assertEqual(len(manager.history), 0)

    def test_clear_history(self):
        self.history_manager.add_entry("5 + 5", "10")
        self.assertEqual(len(self.history_manager.history), 1)
        self.history_manager.clear()
        self.assertEqual(len(self.history_manager.history), 0)


class TestSoundManager(unittest.TestCase):
    def test_toggle_and_calls(self):
        sm = SoundManager(enabled=True)
        self.assertTrue(sm.enabled)
        sm.toggle()
        self.assertFalse(sm.enabled)

        # Não deve travar nem gerar erro ao chamar métodos
        sm.play_digit()
        sm.play_operator()
        sm.play_equals()
        sm.play_error()


if __name__ == "__main__":
    unittest.main()
