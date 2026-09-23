"""Check committed evidence identity, local documentation links and source syntax."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'provenance.json').read_text(encoding='utf-8'))
for name, entry in manifest['files'].items():
    path = ROOT / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
        raise SystemExit('Changed imported evidence/source: ' + name)

count, size = 0, 0
for directory, folders, files in os.walk(ROOT):
    folders[:] = [f for f in folders if f not in {'.git', '.local', '__pycache__'} and not f.startswith('.venv')]
    for name in files:
        path = Path(directory) / name
        if path.suffix.lower() in {'.npz', '.safetensors', '.pt', '.pth', '.glb', '.rrd', '.png', '.jpg', '.jpeg', '.exe', '.zip', '.tgz'}:
            raise SystemExit('Unexpected binary/input artifact: ' + str(path.relative_to(ROOT)))
        if name == '.env' or name.startswith('.env.') or path.stat().st_size > 1_000_000:
            raise SystemExit('Unexpected local/large artifact: ' + str(path.relative_to(ROOT)))
        if path.suffix == '.py':
            ast.parse(path.read_text(encoding='utf-8'), filename=str(path.relative_to(ROOT)))
        if path.suffix == '.md' and 'archive' not in path.relative_to(ROOT).parts:
            for url in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if url.startswith(('https://', 'http://', '#')):
                    continue
                target = (path.parent / url.split('#')[0]).resolve()
                if not target.is_relative_to(ROOT) or not target.exists():
                    raise SystemExit('Broken/nonportable link: ' + str(path.relative_to(ROOT)) + ': ' + url)
        count += 1
        size += path.stat().st_size

print(f'PASS: {len(manifest["files"])} imported file hashes; {count} project files / {size} bytes; links, artifact scope and Python syntax')
