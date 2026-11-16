#!/usr/bin/env python3
"""Выкладывает сайт на хостинг по FTP с шифрованием (FTPS).

Заливает только новые и изменённые файлы и удаляет с сервера то, что
раньше выкладывал сам и что из проекта исчезло. Чужие файлы на сервере
(например, файлы подтверждения Google и Яндекса) не трогает.

Настройка один раз:

1. Файл tools/deploy.local.json (в git не попадает):

       {"host": "srv-plesk39.ps.kz", "user": "логин_ftp", "root": "/httpdocs"}

   host — имя сервера Plesk (сертификат FTP выписан на *.ps.kz, поэтому
   не домен сайта); логин — в панели хостинга, раздел «Доступ по FTP».
   root — папка сайта: у основного домена подписки Plesk это /httpdocs,
   у дополнительного — папка с именем домена, например /hotel-astana.kz.
   Проверить: python3 tools/deploy-ftp.py --ls

2. Пароль — в Связку ключей macOS, командой в Терминале (пароль спросит сам
   и в файлах не останется):

       security add-generic-password -s hotel-ast-ftp -a логин_ftp -w

Запуск из корня проекта:

    python3 tools/deploy-ftp.py --dry-run   # показать, что изменится
    python3 tools/deploy-ftp.py             # выложить
    python3 tools/deploy-ftp.py --all       # перезалить всё целиком
"""
import ftplib
import hashlib
import json
import os
import posixpath
import ssl
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
CONFIG = os.path.join(ROOT, 'tools', 'deploy.local.json')
MANIFEST = os.path.join(ROOT, 'tools', '.deploy-manifest.json')
DIST = os.path.join(ROOT, 'dist')
KEYCHAIN_SERVICE = 'hotel-ast-ftp'


def sha1(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def load_config():
    if not os.path.exists(CONFIG):
        sys.exit('нет tools/deploy.local.json — см. описание в начале скрипта')
    cfg = json.load(open(CONFIG, encoding='utf-8'))
    for key in ('host', 'user'):
        if not cfg.get(key):
            sys.exit(f'в tools/deploy.local.json не заполнено поле {key}')
    cfg.setdefault('root', '/httpdocs')
    cfg.setdefault('port', 21)
    cfg.setdefault('tls_verify', True)
    return cfg


def password(user):
    env = os.environ.get('HOTEL_AST_FTP_PASSWORD')
    if env:
        return env
    res = subprocess.run(['security', 'find-generic-password', '-s', KEYCHAIN_SERVICE, '-a', user, '-w'],
                         capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit('пароля нет в Связке ключей. Добавьте его командой:\n'
                 f'  security add-generic-password -s {KEYCHAIN_SERVICE} -a {user} -w')
    return res.stdout.rstrip('\n')


def plan(full):
    """Сравнивает dist/ с прошлой выкладкой: что залить и что удалить."""
    import importlib
    package = importlib.import_module('package')
    files = package.build()
    now = {rel.replace(os.sep, '/'): sha1(os.path.join(DIST, rel)) for rel in files}
    before = {} if full or not os.path.exists(MANIFEST) else json.load(open(MANIFEST, encoding='utf-8'))
    upload = sorted(p for p, h in now.items() if before.get(p) != h)
    remove = sorted(p for p in before if p not in now)
    return now, upload, remove


def connect(cfg):
    ctx = ssl.create_default_context()
    if not cfg['tls_verify']:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    ftp = ftplib.FTP_TLS(context=ctx, timeout=60)
    ftp.connect(cfg['host'], int(cfg['port']))
    try:
        ftp.login(cfg['user'], password(cfg['user']))
    except ssl.SSLCertVerificationError:
        sys.exit('сертификат FTP-сервера не прошёл проверку. Если хост верный, '
                 'добавьте в tools/deploy.local.json: "tls_verify": false')
    ftp.prot_p()
    ftp.set_pasv(True)
    return ftp


def ensure_dirs(ftp, remote_dir, made):
    parts = [p for p in remote_dir.split('/') if p]
    path = ''
    for part in parts:
        path += '/' + part
        if path in made:
            continue
        try:
            ftp.mkd(path)
        except ftplib.error_perm:
            pass  # папка уже есть
        made.add(path)


def list_root(cfg):
    """Показывает папки FTP-аккаунта и что лежит в выбранном корне сайта."""
    ftp = connect(cfg)
    print('папки аккаунта:', ', '.join(sorted(n for n in ftp.nlst('/') if not n.startswith('.'))))
    root = '/' + cfg['root'].strip('/')
    try:
        print(f'в {root}:', ', '.join(sorted(ftp.nlst(root))))
    except ftplib.error_perm as e:
        print(f'папки {root} нет: {e}')
    ftp.quit()
    return 0


def main():
    dry = '--dry-run' in sys.argv
    full = '--all' in sys.argv
    cfg = load_config()
    if '--ls' in sys.argv:
        return list_root(cfg)
    now, upload, remove = plan(full)
    print(f'залить: {len(upload)}, удалить: {len(remove)}')
    for p in upload:
        print('  +', p)
    for p in remove:
        print('  -', p)
    if dry or not (upload or remove):
        print('ничего не отправлено' if dry else 'на сервере всё актуально')
        return 0

    ftp = connect(cfg)
    root = '/' + cfg['root'].strip('/')
    made = set()
    for rel in upload:
        remote = posixpath.join(root, rel)
        ensure_dirs(ftp, posixpath.dirname(remote), made)
        with open(os.path.join(DIST, rel), 'rb') as f:
            ftp.storbinary(f'STOR {remote}', f)
    for rel in remove:
        try:
            ftp.delete(posixpath.join(root, rel))
        except ftplib.error_perm:
            pass
    ftp.quit()
    json.dump(now, open(MANIFEST, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
    print('выложено')
    return 0


if __name__ == '__main__':
    sys.exit(main())
