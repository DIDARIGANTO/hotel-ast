#!/usr/bin/env python3
"""Собирает то, что выкладывается на хостинг: папку dist/ и архив hotel-ast-site.zip.

В пакет попадают только файлы сайта: страницы, kk/, en/, assets/,
robots.txt, sitemap.xml, favicon.ico, .htaccess, 404.html. Папки docs/,
tests/, tools/, README и служебные файлы git остаются дома.

Запуск из корня проекта:

    python3 tools/package.py

Архив удобен для первой заливки через файловый менеджер Plesk/cPanel:
загрузить один zip в корень сайта и выбрать «Извлечь файлы». Перетаскивать
папки в браузер нельзя: браузер молча пропускает вложенные папки.
"""
import os
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
ZIP = os.path.join(ROOT, 'hotel-ast-site.zip')

ROOT_FILES = ('robots.txt', 'sitemap.xml', 'favicon.ico', '.htaccess', 'llms.txt')
DIRS = ('assets', 'kk', 'en')
SKIP = ('.DS_Store', '.gitkeep')


def site_files():
    """Пути файлов сайта относительно корня проекта."""
    out = [f for f in sorted(os.listdir(ROOT)) if f.endswith('.html')]
    out += [f for f in ROOT_FILES if os.path.exists(os.path.join(ROOT, f))]
    for d in DIRS:
        for folder, dirs, files in os.walk(os.path.join(ROOT, d)):
            dirs.sort()
            for f in sorted(files):
                if f in SKIP:
                    continue
                out.append(os.path.relpath(os.path.join(folder, f), ROOT))
    return out


def build():
    files = site_files()
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    for rel in files:
        dst = os.path.join(DIST, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, rel), dst)
    with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
        for rel in files:
            z.write(os.path.join(DIST, rel), rel)
    size = sum(os.path.getsize(os.path.join(DIST, f)) for f in files)
    print(f'dist/: {len(files)} файлов, {size / 1024 / 1024:.1f} МБ')
    print(f'архив: {os.path.relpath(ZIP, ROOT)}, {os.path.getsize(ZIP) / 1024 / 1024:.1f} МБ')
    return files


if __name__ == '__main__':
    build()
    sys.exit(0)
