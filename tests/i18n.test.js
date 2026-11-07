import { test, assert } from './harness.js';
import { DICT, translate, LANGS } from '../assets/js/i18n.js';

test('поддерживаются три языка', () => {
  assert.deepEqual(LANGS, ['ru', 'kk', 'en']);
});

test('translate возвращает строку нужного языка', () => {
  assert.equal(translate('nav.contacts', 'ru'), DICT.ru['nav.contacts']);
  assert.equal(translate('nav.contacts', 'en'), DICT.en['nav.contacts']);
});

test('translate падает обратно на русский при отсутствии ключа', () => {
  assert.equal(translate('nav.contacts', 'xx'), DICT.ru['nav.contacts']);
});

test('неизвестный ключ возвращает сам ключ', () => {
  assert.equal(translate('нет.такого.ключа', 'ru'), 'нет.такого.ключа');
});

test('словари kk и en покрывают все ключи ru', () => {
  const ruKeys = Object.keys(DICT.ru);
  for (const lang of ['kk', 'en']) {
    const missing = ruKeys.filter((key) => !(key in DICT[lang]));
    assert.deepEqual(missing, [], `${lang}: не переведены ${missing.join(', ')}`);
  }
});
