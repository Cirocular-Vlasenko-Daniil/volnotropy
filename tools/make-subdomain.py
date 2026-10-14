#!/usr/bin/env python3
"""Готовит папку под отдельный субдомен на GitHub Pages.

GitHub Pages даёт один домен на репозиторий, поэтому страница, которая должна
жить на своём субдомене, выносится в отдельный репозиторий. Скрипт собирает
для неё готовую папку: копирует файлы, подменяет ссылки на главную
на абсолютные и кладёт .nojekyll.

    python3 tools/make-subdomain.py synthtusa synthtusa.volnotropy.ru

Результат — папка ../volnotropy-synthtusa рядом с проектом. Её содержимое
заливается в отдельный репозиторий, домен указывается в Settings → Pages.
"""
import pathlib, re, shutil, sys

MAIN_SITE = 'https://volnotropy.ru/'

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    folder, domain = sys.argv[1], sys.argv[2]
    root = pathlib.Path(__file__).resolve().parent.parent
    src = root / folder
    if not src.is_dir():
        sys.exit('нет такой папки: %s' % src)

    dest = root.parent / ('volnotropy-' + folder)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns('*.gif'))

    for page in dest.rglob('index.html'):
        text = page.read_text(encoding='utf-8')
        # глубина страницы внутри папки: index.html → 0, open-call/index.html → 1
        depth = len(page.relative_to(dest).parts) - 1

        def to_main(m):
            # заменяем только те ссылки, которые уходят выше корня папки;
            # внутренние («← Синтитуса») остаются относительными
            ups = m.group(2).count('../')
            return m.group(1) + MAIN_SITE + m.group(3) if ups > depth else m.group(0)

        text = re.sub(r'(href=")((?:\.\./)+)index\.html(")', to_main, text)
        # og:image под новый домен
        text = re.sub(r'(<meta property="og:image" content=")[^"]*(")',
                      r'\1https://' + domain + '/og.png' + r'\2', text)
        page.write_text(text, encoding='utf-8')
        print('поправлено:', page.relative_to(dest))

    (dest / '.nojekyll').touch()
    print('\nготово:', dest)
    print('дальше: создайте репозиторий, залейте содержимое папки,')
    print('в Settings → Pages укажите домен %s' % domain)

if __name__ == '__main__':
    main()
