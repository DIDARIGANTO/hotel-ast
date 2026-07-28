#!/usr/bin/env python3
"""Статические проверки сайта AST Hotels.

Запуск из корня проекта:

    python3 tools/check.py

Скрипт печатает отчёт строками «OK …» и «ОШИБКА …» и завершается кодом 1,
если найдено хотя бы одно нарушение. Внешних зависимостей нет.

Что проверяется:
  1. Все ключи data-i18n и data-i18n-attr из *.html заведены в DICT.ru, .kk, .en.
  2. Внутренние ссылки href ведут на существующие файлы.
  3. В *.html нет цен — они приходят из assets/js/hotels.js (hotels.html
     пропускается: там таблица сравнения с подтверждёнными цифрами).
  4. Телефоны на страницах совпадают с номерами из assets/js/hotels.js.
  5. Каждая страница подключает ui.js, i18n.js и pages.js.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = os.path.join(ROOT, 'assets', 'js', 'i18n.js')
HOTELS = os.path.join(ROOT, 'assets', 'js', 'hotels.js')

LANGS = ('ru', 'kk', 'en')
REQUIRED_SCRIPTS = ('assets/js/ui.js', 'assets/js/i18n.js', 'assets/js/pages.js')
# Таблицу сравнения на hotels.html заполняли подтверждёнными цифрами 2ГИС.
PRICE_SKIP = {'hotels.html'}
SKIP_HREF_PREFIXES = ('#', 'http://', 'https://', 'tel:', 'mailto:', 'wa.me', '//')

RE_I18N = re.compile(r'data-i18n="([^"]+)"')
RE_I18N_ATTR = re.compile(r'data-i18n-attr="([^"]+)"')
RE_HREF = re.compile(r'href="([^"]*)"')
RE_SRC = re.compile(r'src="([^"]*)"')
RE_DICT_LANG = re.compile(r"^\s*(ru|kk|en):\s*\{")
RE_DICT_KEY = re.compile(r"^\s*'([^']+)':\s*'(.*)',?\s*$")
RE_JS_PHONE = re.compile(r"(?:phone|phoneAlt|whatsapp):\s*'([^']+)'")
# Цена в тенге и «от <четырёхзначное число>» — и то и другое должно приходить из данных.
RE_PRICE_SIGN = re.compile(r'\d[\d  ]{0,12}₸')
RE_PRICE_FROM = re.compile(r'\bот\s+(\d[\d  ]*)', re.IGNORECASE)
# Телефон опознаём только по явному контексту, чтобы не спутать с id карточки 2ГИС.
RE_PHONE_TEL = re.compile(r'tel:\+?(\d+)')
RE_PHONE_WA = re.compile(r'wa\.me/(\d+)')
RE_PHONE_TEXT = re.compile(r'\+7[\d\s()\-]{9,}')

report = []
errors = []


def ok(text):
    report.append('OK      ' + text)


def fail(text):
    line = 'ОШИБКА  ' + text
    report.append(line)
    errors.append(line)


def pages():
    """Страницы сайта в алфавитном порядке."""
    return sorted(f for f in os.listdir(ROOT) if f.endswith('.html'))


def read(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()


def parse_dict():
    """Читает DICT из i18n.js построчно: 'ключ': 'значение'."""
    result = {lang: {} for lang in LANGS}
    lang = None
    inside = False
    for raw in read(I18N).splitlines():
        if not inside:
            if raw.startswith('export const DICT'):
                inside = True
            continue
        if raw.startswith('};'):
            break
        match = RE_DICT_LANG.match(raw)
        if match:
            lang = match.group(1)
            continue
        match = RE_DICT_KEY.match(raw)
        if match and lang:
            result[lang][match.group(1)] = match.group(2)
    return result


def used_keys():
    """Ключи из разметки: {ключ: [страницы]}."""
    found = {}
    for page in pages():
        html = read(os.path.join(ROOT, page))
        keys = set(RE_I18N.findall(html))
        for value in RE_I18N_ATTR.findall(html):
            for pair in value.split(';'):
                if ':' in pair:
                    keys.add(pair.split(':', 1)[1].strip())
        for key in keys:
            found.setdefault(key, []).append(page)
    return found


# Карточки отелей и номеров собирает assets/js/pages.js, и часть ключей он
# строит на лету: `room.${hotel.id}.${room.id}`. Такие ключи в разметке не
# встречаются, поэтому они считаются используемыми по префиксу.
JS_KEY_PREFIXES = ('pages.', 'district.', 'address.', 'room.', 'beds.')


def js_keys():
    """Ключи, которые подставляют модули: {ключ: [файлы]}."""
    found = {}
    js_dir = os.path.join(ROOT, 'assets', 'js')
    for name in sorted(os.listdir(js_dir)):
        if not name.endswith('.js'):
            continue
        source = read(os.path.join(js_dir, name))
        for key in re.findall(r"""translate\(\s*['"]([\w.]+)['"]""", source):
            found.setdefault(key, []).append(f'assets/js/{name}')
        for key in re.findall(r"""\bt\(\s*['"]([\w.]+)['"]""", source):
            found.setdefault(key, []).append(f'assets/js/{name}')
    return found


def digits(text):
    return re.sub(r'\D', '', text)


# ── 1. Полнота словаря ──────────────────────────────────────
def check_dict():
    dicts = parse_dict()
    sizes = ', '.join(f'{lang} — {len(dicts[lang])}' for lang in LANGS)
    keys = used_keys()
    for key, files in js_keys().items():
        keys.setdefault(key, []).extend(files)
    missing = 0
    for key in sorted(keys):
        for lang in LANGS:
            if key not in dicts[lang]:
                missing += 1
                fail(f'{", ".join(keys[key])}: ключа «{key}» нет в DICT.{lang}')
    if not missing:
        word = plural(len(keys), 'ключ', 'ключа', 'ключей')
        ok(f'словарь: {len(keys)} {word} разметки заведены в трёх языках ({sizes})')

    extra = sorted(
        key for key in set(dicts['ru']) - set(keys)
        if not key.startswith(JS_KEY_PREFIXES)
    )
    for key in extra:
        fail(f'assets/js/i18n.js: ключ «{key}» есть в словаре, но нигде не используется')
    for lang in ('kk', 'en'):
        for key in sorted(set(dicts['ru']) - set(dicts[lang])):
            fail(f'assets/js/i18n.js: ключ «{key}» есть в ru, но отсутствует в {lang}')
        for key in sorted(set(dicts[lang]) - set(dicts['ru'])):
            fail(f'assets/js/i18n.js: ключ «{key}» есть в {lang}, но отсутствует в ru')
    if not extra:
        ok('словарь: лишних ключей нет')


# ── 2. Внутренние ссылки ────────────────────────────────────
def check_links():
    broken = 0
    total = 0
    for page in pages():
        html = read(os.path.join(ROOT, page))
        for href in sorted(set(RE_HREF.findall(html))):
            if not href or href.startswith(SKIP_HREF_PREFIXES):
                continue
            target = href.split('#', 1)[0].split('?', 1)[0]
            if not target:
                continue
            total += 1
            if not os.path.exists(os.path.join(ROOT, target)):
                broken += 1
                fail(f'{page}: ссылка href="{href}" ведёт в никуда — файла «{target}» нет')
    if not broken:
        word = plural(total, 'внутренний адрес', 'внутренних адреса', 'внутренних адресов')
        ok(f'ссылки: {total} {word}, все файлы на месте')


# ── 3. Цены в разметке ──────────────────────────────────────
def check_prices():
    found = 0
    for page in pages():
        if page in PRICE_SKIP:
            continue
        for number, line in enumerate(read(os.path.join(ROOT, page)).splitlines(), 1):
            for match in RE_PRICE_SIGN.finditer(line):
                found += 1
                fail(f'{page}:{number}: цена «{match.group(0).strip()}» в разметке — '
                     'она должна приходить из hotels.js')
            for match in RE_PRICE_FROM.finditer(line):
                if len(digits(match.group(1))) >= 4:
                    found += 1
                    fail(f'{page}:{number}: цена «{match.group(0).strip()}» в разметке — '
                         'она должна приходить из hotels.js')
    skipped = ', '.join(sorted(PRICE_SKIP))
    if not found:
        ok(f'цены: в разметке нет зашитых сумм (пропущен {skipped})')


# ── 4. Телефоны ─────────────────────────────────────────────
def check_phones():
    allowed = {digits(number) for number in RE_JS_PHONE.findall(read(HOTELS))}
    wrong = 0
    seen = set()
    for page in pages():
        html = read(os.path.join(ROOT, page))
        numbers = set()
        for regex in (RE_PHONE_TEL, RE_PHONE_WA, RE_PHONE_TEXT):
            numbers.update(digits(value) for value in regex.findall(html))
        for number in sorted(numbers):
            seen.add(number)
            if number not in allowed:
                wrong += 1
                fail(f'{page}: телефон +{number} не найден в assets/js/hotels.js')
    if not wrong:
        word = plural(len(seen), 'номер', 'номера', 'номеров')
        ok(f'телефоны: {len(seen)} {word} на страницах, все есть в hotels.js')


# ── 5. Подключение модулей ──────────────────────────────────
def check_scripts():
    missing = 0
    for page in pages():
        sources = set(RE_SRC.findall(read(os.path.join(ROOT, page))))
        for script in REQUIRED_SCRIPTS:
            if script not in sources:
                missing += 1
                fail(f'{page}: не подключён {script}')
    if not missing:
        word = plural(len(pages()), 'страница', 'страницы', 'страниц')
        ok(f'модули: все {len(pages())} {word} подключают ui.js, i18n.js и pages.js')


# ── 6. Разметка и словарь говорят одно и то же ──────────────
def check_defaults():
    """Русский текст в HTML — значение по умолчанию, когда JS отключён.
    Если он разошёлся со словарём, гость без JS прочитает старую редакцию."""
    dicts = parse_dict()
    ru = dicts['ru']
    bad = 0
    checked = 0
    for page in pages():
        html = read(os.path.join(ROOT, page))
        for m in re.finditer(r'data-i18n="([\w.-]+)"[^>]*>([^<]*)<', html):
            key, markup = m.group(1), m.group(2).strip()
            if not markup or key not in ru:
                continue
            checked += 1
            if ru[key].replace("\\'", "'") != markup:
                bad += 1
                fail(f'{page}: «{key}» в разметке и в словаре разный текст')
    if not bad:
        word = plural(checked, 'подпись', 'подписи', 'подписей')
        ok(f'разметка: {checked} {word} совпадают с русским словарём')


def plural(count, one, few, many):
    """Русское склонение числительного: 1 ключ, 2 ключа, 5 ключей."""
    if 11 <= count % 100 <= 14:
        return many
    tail = count % 10
    if tail == 1:
        return one
    if tail in (2, 3, 4):
        return few
    return many


def main():
    if not os.path.exists(I18N) or not os.path.exists(HOTELS):
        print('ОШИБКА  не найдены модули assets/js — запускайте из корня проекта')
        return 1

    print('AST Hotels — статические проверки')
    print('Проект:', ROOT)
    print()

    for check in (check_dict, check_defaults, check_links, check_prices,
                  check_phones, check_scripts):
        check()

    print('\n'.join(report))
    print()
    if errors:
        word = plural(len(errors), 'нарушение', 'нарушения', 'нарушений')
        print(f'Итог: {len(errors)} {word}')
        return 1
    print('Итог: нарушений нет')
    return 0


if __name__ == '__main__':
    sys.exit(main())
