import test from 'node:test';
import assert from 'node:assert/strict';
import {
  INITIAL_STATE,
  inputDigit,
  inputDecimal,
  handleOperator,
  calculateEquals,
  inputPercent,
  toggleSign,
  backspace,
  clearAll,
  clearHistory,
  recallHistoryItem,
  MAX_HISTORY_ITEMS,
} from './calculator';

test('Calculates simple addition: 25 + 75 = 100', () => {
  let state = INITIAL_STATE;
  state = inputDigit(state, '2');
  state = inputDigit(state, '5');
  assert.equal(state.displayValue, '25');

  state = handleOperator(state, '+');
  assert.equal(state.previousValue, '25');
  assert.equal(state.operator, '+');

  state = inputDigit(state, '7');
  state = inputDigit(state, '5');
  assert.equal(state.displayValue, '75');

  state = calculateEquals(state);
  assert.equal(state.displayValue, '100');
  assert.equal(state.history.length, 1);
  assert.equal(state.history[0].expression, '25 + 75');
  assert.equal(state.history[0].result, '100');
});

test('Calculates subtraction: 100 - 35 = 65', () => {
  let state = INITIAL_STATE;
  state = inputDigit(state, '1');
  state = inputDigit(state, '0');
  state = inputDigit(state, '0');
  state = handleOperator(state, '-');
  state = inputDigit(state, '3');
  state = inputDigit(state, '5');
  state = calculateEquals(state);

  assert.equal(state.displayValue, '65');
});

test('Calculates multiplication: 12 × 4 = 48', () => {
  let state = INITIAL_STATE;
  state = inputDigit(state, '1');
  state = inputDigit(state, '2');
  state = handleOperator(state, '×');
  state = inputDigit(state, '4');
  state = calculateEquals(state);

  assert.equal(state.displayValue, '48');
});

test('Calculates division: 50 ÷ 2 = 25', () => {
  let state = INITIAL_STATE;
  state = inputDigit(state, '5');
  state = inputDigit(state, '0');
  state = handleOperator(state, '÷');
  state = inputDigit(state, '2');
  state = calculateEquals(state);

  assert.equal(state.displayValue, '25');
});

test('Handles division by zero gracefully', () => {
  let state = INITIAL_STATE;
  state = inputDigit(state, '9');
  state = handleOperator(state, '÷');
  state = inputDigit(state, '0');
  state = calculateEquals(state);

  assert.equal(state.hasError, true);
  assert.equal(state.displayValue, 'Erro: Divisão por 0');
});

test('Handles percentage in operations: 200 + 10% = 220', () => {
  let state = INITIAL_STATE;
  state = inputDigit(state, '2');
  state = inputDigit(state, '0');
  state = inputDigit(state, '0');
  state = handleOperator(state, '+');
  state = inputDigit(state, '1');
  state = inputDigit(state, '0');
  state = inputPercent(state); // 10% of 200 is 20
  assert.equal(state.displayValue, '20');

  state = calculateEquals(state); // 200 + 20 = 220
  assert.equal(state.displayValue, '220');
});

test('Handles standalone percentage: 50% = 0.5', () => {
  let state = INITIAL_STATE;
  state = inputDigit(state, '5');
  state = inputDigit(state, '0');
  state = inputPercent(state);
  assert.equal(state.displayValue, '0.5');
});

test('Enforces strictly max 5 items in calculation memory', () => {
  let state = INITIAL_STATE;

  for (let i = 1; i <= 7; i++) {
    state = inputDigit(state, String(i));
    state = handleOperator(state, '+');
    state = inputDigit(state, '1');
    state = calculateEquals(state);
  }

  // Exactly MAX_HISTORY_ITEMS (5) items kept
  assert.equal(state.history.length, MAX_HISTORY_ITEMS);
  // Most recent calculation was 7 + 1 = 8
  assert.equal(state.history[0].expression, '7 + 1');
  assert.equal(state.history[0].result, '8');
  // Oldest calculation retained is 3 + 1 = 4 (1 and 2 discarded)
  assert.equal(state.history[4].expression, '3 + 1');
  assert.equal(state.history[4].result, '4');
});

test('Recall and clear memory functions work properly', () => {
  let state = INITIAL_STATE;
  state = inputDigit(state, '8');
  state = handleOperator(state, '×');
  state = inputDigit(state, '8');
  state = calculateEquals(state);

  assert.equal(state.displayValue, '64');
  const item = state.history[0];

  state = clearAll(state);
  assert.equal(state.displayValue, '0');

  state = recallHistoryItem(state, item);
  assert.equal(state.displayValue, '64');

  state = clearHistory(state);
  assert.equal(state.history.length, 0);
});

test('Sign toggle and backspace work as expected', () => {
  let state = INITIAL_STATE;
  state = inputDigit(state, '1');
  state = inputDigit(state, '2');
  state = inputDigit(state, '3');
  assert.equal(state.displayValue, '123');

  state = backspace(state);
  assert.equal(state.displayValue, '12');

  state = toggleSign(state);
  assert.equal(state.displayValue, '-12');

  state = toggleSign(state);
  assert.equal(state.displayValue, '12');
});
