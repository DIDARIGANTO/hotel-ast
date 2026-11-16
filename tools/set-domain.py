#!/usr/bin/env python3
"""Переводит сайт на новый адрес одной командой.

Адрес сайта стоит в canonical, hreflang, og:url, og:image, JSON-LD,
sitemap.xml, robots.txt и <base> страницы 404. Если поменять его руками
в одном месте, поисковики получат противоречивые данные, поэтому скрипт
меняет его везде разом и пересобирает языковые версии.

Запуск из корня проекта:

    python3 tools/set-domain.py https://hotels-astana.kz
    python3 tools/set-domain.py https://hotels-astana.kz --github-pages

Флаг --github-pages нужен, только если сайт остаётся на GitHub Pages с
собственным доменом: тогда скрипт пишет файл CNAME. Для хостинга в
Казахстане (PS.kz и т. п.) флаг не ставится, а CNAME удаляется.
"""
import os
import re
import subprocess
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, 'tools', 'build-langs.py')
# Файлы, где адрес записан руками; kk/, en/ и sitemap.xml генерируются заново.
EXTRA = ['robots.txt', 'llms.txt']


def current_base():
    src = open(BUILD, encoding='utf-8').read()
    m = re.search(r"^BASE = '([^']+)'", src, re.M)
    if not m:
        sys.exit('не нашёл BASE в tools/build-langs.py')
    return m.group(1)


def normalize(url):
    url = url.strip()
    if not url.startswith(('https://', 'http://')):
        url = 'https://' + url
    parsed = urlparse(url)
    if not parsed.netloc or '.' not in parsed.netloc:
        sys.exit(f'странный адрес: {url}')
    return url.rstrip('/') + '/'


def targets():
    files = [os.path.join(ROOT, f) for f in sorted(os.listdir(ROOT)) if f.endswith('.html')]
    files += [os.path.join(ROOT, f) for f in EXTRA if os.path.exists(os.path.join(ROOT, f))]
    return files


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 1:
        sys.exit(__doc__)
    github_pages = '--github-pages' in sys.argv
    new = normalize(args[0])
    old = current_base()

    if old == new:
        print(f'адрес уже {new}')
    else:
        changed = 0
        for path in targets() + [BUILD]:
            text = open(path, encoding='utf-8').read()
            if old in text:
                open(path, 'w', encoding='utf-8').write(text.replace(old, new))
                changed += 1
        print(f'адрес заменён в {changed} файлах: {old} → {new}')

    cname = os.path.join(ROOT, 'CNAME')
    host = urlparse(new).netloc
    if github_pages and not host.endswith('github.io'):
        open(cname, 'w', encoding='utf-8').write(host + '\n')
        print(f'CNAME: {host}')
    elif os.path.exists(cname):
        os.remove(cname)
        print('CNAME удалён: сайт живёт не на GitHub Pages')

    subprocess.run([sys.executable, BUILD], check=True, cwd=ROOT)

    # контроль: старого адреса не должно остаться нигде, кроме истории git
    left = []
    for folder, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', 'docs', 'dist')]
        for f in files:
            if f.endswith(('.html', '.xml', '.txt', '.py', '.js', '.json')):
                p = os.path.join(folder, f)
                if old != new and old in open(p, encoding='utf-8', errors='ignore').read():
                    left.append(os.path.relpath(p, ROOT))
    if left:
        print('ВНИМАНИЕ, старый адрес остался в:', ', '.join(left))
        return 1
    print('готово: старого адреса в проекте не осталось')
    return 0


if __name__ == '__main__':
    sys.exit(main())
