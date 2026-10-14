#!/usr/bin/env python3
"""Копирует блок <style> из index.html во все остальные страницы сайта.

Каждая страница самодостаточна (оформление лежит внутри файла) — так папку
с ивентом можно залить на субдомен как есть. Цена этого — четыре копии CSS.
Поправили оформление в index.html → запустите из корня сайта:

    python3 tools/sync-style.py
"""
import pathlib, re, sys

root = pathlib.Path(__file__).resolve().parent.parent
src = (root / 'index.html').read_text(encoding='utf-8')
style = re.search(r'<style>.*?</style>', src, re.S)
if not style:
    sys.exit('в index.html не найден блок <style>')

changed = 0
for page in sorted(root.glob('*/index.html')):
    if page.parent.name in ('archive', 'synthtusa'):
        continue  # у Синтитусы своё оформление
    text = page.read_text(encoding='utf-8')
    new = re.sub(r'<style>.*?</style>', lambda _: style.group(0), text, count=1, flags=re.S)
    if new != text:
        page.write_text(new, encoding='utf-8')
        changed += 1
        print('обновлено:', page.relative_to(root))
print('готово, страниц обновлено:', changed)
