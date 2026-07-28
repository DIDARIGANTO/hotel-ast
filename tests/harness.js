// Мини-раннер тестов для браузера. На машине нет Node, поэтому вместо
// node:test и node:assert/strict наборы импортируют test() и assert отсюда.
// API совпадает с node:assert/strict в той части, что используется в тестах:
// equal, deepEqual, match, ok. Результаты печатаются прямо на страницу.

const PASS_COLOR = '#1B7F4B';
const FAIL_COLOR = '#C0392B';

/** Все выполненные проверки: { name, ok, error }. */
export const results = [];

/* ── Вспомогательное ──────────────────────────────────────── */

// Читаемое представление значения для текста ошибки.
function view(value) {
  if (typeof value === 'string') return `«${value}»`;
  if (value instanceof RegExp) return String(value);
  if (value === undefined) return 'undefined';
  if (typeof value === 'bigint') return `${value}n`;
  if (typeof value === 'function') return `функция ${value.name || 'без имени'}`;
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

// Подсказка из третьего аргумента дописывается через тире.
const withHint = (text, hint) => (hint ? `${text} — ${hint}` : text);

function isDeepEqual(a, b) {
  if (Object.is(a, b)) return true;
  if (typeof a !== 'object' || typeof b !== 'object' || a === null || b === null) return false;
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  if (a instanceof Date || b instanceof Date) {
    return a instanceof Date && b instanceof Date && a.getTime() === b.getTime();
  }
  const keysA = Object.keys(a);
  const keysB = Object.keys(b);
  if (keysA.length !== keysB.length) return false;
  return keysA.every(
    (key) => Object.prototype.hasOwnProperty.call(b, key) && isDeepEqual(a[key], b[key])
  );
}

/* ── Проверки ─────────────────────────────────────────────── */

export const assert = {
  // Строгое равенство, как assert.strictEqual в Node.
  equal(actual, expected, message) {
    if (!Object.is(actual, expected)) {
      throw new Error(
        withHint(`ожидалось ${view(expected)}, получено ${view(actual)}`, message)
      );
    }
  },

  // Глубокое сравнение массивов и объектов.
  deepEqual(actual, expected, message) {
    if (!isDeepEqual(actual, expected)) {
      throw new Error(
        withHint(`ожидалось ${view(expected)}, получено ${view(actual)}`, message)
      );
    }
  },

  // Соответствие строки регулярному выражению.
  match(value, regexp, message) {
    if (typeof value !== 'string') {
      throw new Error(withHint(`ожидалась строка, получено ${view(value)}`, message));
    }
    if (!(regexp instanceof RegExp)) {
      throw new Error(withHint(`ожидалось регулярное выражение, получено ${view(regexp)}`, message));
    }
    if (!regexp.test(value)) {
      throw new Error(withHint(`строка ${view(value)} не подходит под ${regexp}`, message));
    }
  },

  // Истинность значения.
  ok(value, message) {
    if (!value) {
      throw new Error(withHint(`ожидалось истинное значение, получено ${view(value)}`, message));
    }
  },
};

/* ── Вывод на страницу ────────────────────────────────────── */

function listNode() {
  let node = document.getElementById('results');
  if (!node) {
    node = document.createElement('div');
    node.id = 'results';
    document.body.append(node);
  }
  return node;
}

function totalNode() {
  let node = document.getElementById('total');
  if (!node) {
    node = document.createElement('p');
    node.id = 'total';
    document.body.append(node);
  }
  return node;
}

function printLine(ok, text) {
  const line = document.createElement('div');
  line.className = ok ? 'test test--pass' : 'test test--fail';
  line.style.color = ok ? PASS_COLOR : FAIL_COLOR;
  line.style.whiteSpace = 'pre-wrap';
  line.textContent = text;
  listNode().append(line);
}

/** Перерисовывает итоговую строку и возвращает счётчики. */
export function renderTotal() {
  const passed = results.filter((item) => item.ok).length;
  const failed = results.length - passed;
  const node = totalNode();
  node.textContent = `ИТОГО: ${passed} пройдено, ${failed} провалено`;
  node.style.color = failed ? FAIL_COLOR : PASS_COLOR;
  return { passed, failed, total: results.length };
}

/* ── Запуск ───────────────────────────────────────────────── */

/**
 * Выполняет проверку. Исключение внутри fn не останавливает прогон:
 * тест помечается как проваленный, остальные продолжают выполняться.
 */
export function test(name, fn) {
  try {
    fn();
    results.push({ name, ok: true, error: null });
    printLine(true, `PASS ${name}`);
  } catch (error) {
    results.push({ name, ok: false, error });
    printLine(false, `FAIL ${name} — ${error?.message ?? error}`);
    console.error(`FAIL ${name}`, error);
  }
  return renderTotal();
}

/** Отмечает провал вне теста — например, набор не загрузился. */
export function fail(name, error) {
  results.push({ name, ok: false, error });
  printLine(false, `FAIL ${name} — ${error?.message ?? error}`);
  console.error(`FAIL ${name}`, error);
  return renderTotal();
}

// Итог доступен из консоли и автоматизации: window.astTests.
globalThis.astTests = { results, renderTotal };
