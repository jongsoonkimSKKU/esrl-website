"""Build ESRL for GitHub Pages, retaining the root-based Sites output in dist."""
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def verify_asset(entry):
    relative = Path(entry['path'])
    if relative.is_absolute() or '..' in relative.parts or not str(relative).startswith('dist/assets/'):
        raise ValueError('Invalid asset path')
    path = ROOT / relative
    if not path.is_file():
        raise FileNotFoundError('Repository asset missing: ' + str(relative))
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
        raise ValueError('Repository asset checksum mismatch: ' + str(relative))


def validate_links(output, base_path):
    failures = []
    class Links(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for key, value in attrs:
                if key not in ('href', 'src', 'poster') or not value or not value.startswith('/') or value.startswith('//'):
                    continue
                path = unquote(urlsplit(value).path)
                if base_path and not path.startswith(base_path + '/'):
                    failures.append(value)
                    continue
                target = output / path[len(base_path):].lstrip('/')
                if not target.is_file() and not (target / 'index.html').is_file():
                    failures.append(value)
    for page in output.rglob('*.html'):
        Links().feed(page.read_text())
    for css in output.rglob('*.css'):
        for match in re.finditer(r'url\([\s\"\']*(/[^)\"\'\s]+)', css.read_text()):
            path = unquote(urlsplit(match[1]).path)
            if base_path and not path.startswith(base_path + '/'):
                failures.append(match[1])
            elif not (output / path[len(base_path):].lstrip('/')).is_file():
                failures.append(match[1])
    if failures:
        raise ValueError('Broken internal links: ' + ', '.join(sorted(set(failures))))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-path', default='/esrl-website')
    args = parser.parse_args()
    base_path = args.base_path.rstrip('/')
    if base_path and (not re.fullmatch(r'/[A-Za-z0-9._/-]+', base_path) or '..' in base_path.split('/')):
        parser.error('Invalid base path')
    manifest = json.loads((ROOT / 'scripts/pages-assets.json').read_text())
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(verify_asset, manifest['files']))
    subprocess.run([sys.executable, 'build.py'], cwd=ROOT, check=True)
    output = ROOT / '_pages'
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(ROOT / 'dist', output, ignore=shutil.ignore_patterns('.openai'))
    for page in output.rglob('*.html'):
        html = re.sub(r'((?:href|src|poster|action)=[\"\'])/(?!/)', lambda m: m[1] + base_path + '/', page.read_text())
        page.write_text(html)
    for css in output.rglob('*.css'):
        text = re.sub(r'(url\([\s\"\']*)/(?!/)', lambda m: m[1] + base_path + '/', css.read_text())
        css.write_text(text)
    (output / '.nojekyll').touch()
    validate_links(output, base_path)
    print(f'GitHub Pages ready: {len(list(output.rglob("*.html")))} pages; all local links and assets verified.')


if __name__ == '__main__':
    main()
