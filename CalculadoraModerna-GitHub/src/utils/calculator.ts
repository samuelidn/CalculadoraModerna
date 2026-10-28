/**
 * Pure calculator logic engine & memory state management.
 */

export type Operator = '+' | '-' | '×' | '÷';

export interface CalculationHistoryItem {
  id: string;
  expression: string;
  result: string;
  timestamp: number;
}

export interface CalculatorState {
  displayValue: string;
  previousValue: string | null;
  operator: Operator | null;
  waitingForOperand: boolean;
  history: CalculationHistoryItem[];
  hasError: boolean;
  lastCalculatedExpression?: string;
}

export const MAX_HISTORY_ITEMS = 5;

export const INITIAL_STATE: CalculatorState = {
  displayValue: '0',
  previousValue: null,
  operator: null,
  waitingForOperand: false,
  history: [],
  hasError: false,
};

/**
 * Formats a numeric string to standard display, preventing floating-point weirdness.
 */
export function formatResult(num: number): string {
  if (isNaN(num) || !isFinite(num)) {
    return 'Erro';
  }
  // Strip trailing zeros after precision formatting
  const fixed = parseFloat(num.toPrecision(12));
  return String(fixed);
}

/**
 * Performs basic arithmetic operation.
 */
export function executeOperation(
  first: number,
  second: number,
  operator: Operator
): { result: number; error?: string } {
  switch (operator) {
    case '+':
      return { result: first + second };
    case '-':
      return { result: first - second };
    case '×':
      return { result: first * second };
    case '÷':
      if (second === 0) {
        return { result: NaN, error: 'Erro: Divisão por 0' };
      }
      return { result: first / second };
    default:
      return { result: second };
  }
}

/**
 * Handles digit input ('0'-'9').
 */
export function inputDigit(state: CalculatorState, digit: string): CalculatorState {
  if (state.hasError) {
    return {
      ...state,
      displayValue: digit,
      hasError: false,
      waitingForOperand: false,
      previousValue: null,
      operator: null,
    };
  }

  const { displayValue, waitingForOperand } = state;

  if (waitingForOperand) {
    return {
      ...state,
      displayValue: digit,
      waitingForOperand: false,
    };
  }

  // Prevent multiple leading zeros
  const nextValue = displayValue === '0' ? digit : displayValue + digit;

  // Max display length limitation
  if (nextValue.length > 15) {
    return state;
  }

  return {
    ...state,
    displayValue: nextValue,
  };
}

/**
 * Handles decimal dot input ('.' or ',').
 */
export function inputDecimal(state: CalculatorState): CalculatorState {
  if (state.hasError) {
    return {
      ...state,
      displayValue: '0.',
      hasError: false,
      waitingForOperand: false,
    };
  }

  if (state.waitingForOperand) {
    return {
      ...state,
      displayValue: '0.',
      waitingForOperand: false,
    };
  }

  if (!state.displayValue.includes('.')) {
    return {
      ...state,
      displayValue: state.displayValue + '.',
    };
  }

  return state;
}

/**
 * Toggles positive/negative sign (±).
 */
export function toggleSign(state: CalculatorState): CalculatorState {
  if (state.hasError || state.displayValue === '0') {
    return state;
  }

  const num = parseFloat(state.displayValue);
  if (isNaN(num)) return state;

  return {
    ...state,
    displayValue: formatResult(-num),
  };
}

/**
 * Handles percentage calculation (%).
 * - If in middle of an addition or subtraction (e.g. 200 + 10%): calculates 10% of 200 = 20
 * - If in multiplication or division (e.g. 50 × 20%): calculates 20 / 100 = 0.2
 * - If standalone (e.g. 25%): calculates 25 / 100 = 0.25
 */
export function inputPercent(state: CalculatorState): CalculatorState {
  if (state.hasError) return state;

  const current = parseFloat(state.displayValue);
  if (isNaN(current)) return state;

  if (state.previousValue !== null && state.operator !== null) {
    const prev = parseFloat(state.previousValue);
    if (!isNaN(prev)) {
      if (state.operator === '+' || state.operator === '-') {
        // e.g. 200 + 10% -> 10% of 200 is 20
        const percentVal = (prev * current) / 100;
        return {
          ...state,
          displayValue: formatResult(percentVal),
        };
      } else {
        // e.g. 200 * 10% -> 10% is 0.1
        const percentVal = current / 100;
        return {
          ...state,
          displayValue: formatResult(percentVal),
        };
      }
    }
  }

  // Standalone percentage
  const result = current / 100;
  return {
    ...state,
    displayValue: formatResult(result),
  };
}

/**
 * Handles backspace / delete last character.
 */
export function backspace(state: CalculatorState): CalculatorState {
  if (state.hasError || state.waitingForOperand) {
    return state;
  }

  if (state.displayValue.length <= 1 || (state.displayValue.length === 2 && state.displayValue.startsWith('-'))) {
    return {
      ...state,
      displayValue: '0',
    };
  }

  return {
    ...state,
    displayValue: state.displayValue.slice(0, -1),
  };
}

/**
 * Sets an operator (+, -, ×, ÷).
 */
export function handleOperator(state: CalculatorState, nextOperator: Operator): CalculatorState {
  if (state.hasError) return state;

  const current = parseFloat(state.displayValue);

  if (state.previousValue === null) {
    return {
      ...state,
      previousValue: state.displayValue,
      operator: nextOperator,
      waitingForOperand: true,
    };
  }

  if (state.operator && !state.waitingForOperand) {
    const prev = parseFloat(state.previousValue);
    const { result, error } = executeOperation(prev, current, state.operator);

    if (error) {
      return {
        ...state,
        displayValue: error,
        hasError: true,
        previousValue: null,
        operator: null,
        waitingForOperand: false,
      };
    }

    const formatted = formatResult(result);
    return {
      ...state,
      displayValue: formatted,
      previousValue: formatted,
      operator: nextOperator,
      waitingForOperand: true,
    };
  }

  return {
    ...state,
    operator: nextOperator,
  };
}

/**
 * Handles the equal button (=), performing the calculation and adding to the 5-item memory history.
 */
export function calculateEquals(state: CalculatorState): CalculatorState {
  if (state.hasError || state.previousValue === null || state.operator === null) {
    return state;
  }

  const prev = parseFloat(state.previousValue);
  const current = parseFloat(state.displayValue);
  const { result, error } = executeOperation(prev, current, state.operator);

  if (error) {
    return {
      ...state,
      displayValue: error,
      hasError: true,
      previousValue: null,
      operator: null,
      waitingForOperand: false,
    };
  }

  const formattedResult = formatResult(result);
  const expression = `${state.previousValue} ${state.operator} ${state.displayValue}`;

  const newHistoryItem: CalculationHistoryItem = {
    id: `${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
    expression,
    result: formattedResult,
    timestamp: Date.now(),
  };

  // Keep strictly the last 5 calculations (newest first)
  const updatedHistory = [newHistoryItem, ...state.history].slice(0, MAX_HISTORY_ITEMS);

  return {
    ...state,
    displayValue: formattedResult,
    previousValue: null,
    operator: null,
    waitingForOperand: true,
    history: updatedHistory,
    hasError: false,
    lastCalculatedExpression: expression,
  };
}

/**
 * Clears current entry or all state.
 */
export function clearAll(state: CalculatorState): CalculatorState {
  return {
    ...state,
    displayValue: '0',
    previousValue: null,
    operator: null,
    waitingForOperand: false,
    hasError: false,
    lastCalculatedExpression: undefined,
  };
}

/**
 * Clears the memory history.
 */
export function clearHistory(state: CalculatorState): CalculatorState {
  return {
    ...state,
    history: [],
  };
}

/**
 * Recalls an item from history and places its result as the active display value.
 */
export function recallHistoryItem(state: CalculatorState, item: CalculationHistoryItem): CalculatorState {
  return {
    ...state,
    displayValue: item.result,
    waitingForOperand: false,
    hasError: false,
  };
}
