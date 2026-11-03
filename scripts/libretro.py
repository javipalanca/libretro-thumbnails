#!/usr/bin/env python3
"""Find and download real game artwork from libretro-thumbnails."""
import argparse
import json
import posixpath
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

CACHE = Path.home() / '.cache' / 'libretro-thumbnails'
KINDS = {'boxart': 'Named_Boxarts/', 'title': 'Named_Titles/', 'snap': 'Named_Snaps/'}


def validate_repo(repo):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', repo):
        raise ValueError('Invalid repository name')
    return repo


def index(repo, refresh=False):
    validate_repo(repo)
    CACHE.mkdir(parents=True, exist_ok=True)
    cache = CACHE / f'{repo}.json'
    if cache.exists() and not refresh:
        try:
            record = json.loads(cache.read_text())
            if record.get('version') == 2:
                return record['commit'], record['files']
        except (ValueError, KeyError):
            pass
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['git', 'clone', '-q', '--filter=blob:none', '--no-checkout', '--depth', '1',
                        f'https://github.com/libretro-thumbnails/{repo}', tmp], check=True, timeout=180)
        commit = subprocess.check_output(['git', '-C', tmp, 'rev-parse', 'HEAD'], text=True).strip()
        tree = subprocess.check_output(['git', '-C', tmp, 'ls-tree', '-rz', 'HEAD'])
        files = {}
        for entry in tree.split(b'\0'):
            if entry:
                metadata, path = entry.split(b'\t', 1)
                files[path.decode('utf-8')] = metadata.split()[0].decode('ascii')
    record = {'version': 2, 'commit': commit, 'files': files}
    with tempfile.NamedTemporaryFile(mode='w', dir=CACHE, delete=False) as temporary:
        json.dump(record, temporary)
        name = temporary.name
    Path(name).replace(cache)
    return commit, files


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'libretro-thumbnails-skill/1.1'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def ext_of(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png'
    if data.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    if data.startswith((b'GIF87a', b'GIF89a')):
        return '.gif'
    raise ValueError('Unknown image format')


def resolve(repo, commit, files, path):
    visited = set()
    while True:
        if path not in files:
            raise ValueError(f'Not in index: {path}')
        if path in visited:
            raise ValueError(f'Symlink cycle: {path}')
        visited.add(path)
        url = f'https://raw.githubusercontent.com/libretro-thumbnails/{repo}/{commit}/{urllib.parse.quote(path)}'
        data = fetch(url)
        if files[path] != '120000':
            return path, data
        target = data.decode('utf-8').strip()
        if posixpath.isabs(target):
            raise ValueError('Absolute symlink target')
        path = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
        if path == '..' or path.startswith('../'):
            raise ValueError('Symlink target escapes repository')


def cmd_search(args):
    words = args.query.casefold().split()
    if not words or args.limit < 1:
        raise ValueError('Provide a nonempty query and positive limit')
    for repo in args.repo:
        _, files = index(repo, args.refresh)
        hits = [p for p in files if p.startswith(KINDS.get(args.kind, 'Named_'))
                and all(w in p.casefold() for w in words)]
        for path in hits[:args.limit]:
            print(f'{repo}\t{path}')
        if len(hits) > args.limit:
            print(f'{repo}: {len(hits) - args.limit} more matches', file=sys.stderr)


def cmd_get(args):
    commit, files = index(args.repo, args.refresh)
    path, data = resolve(args.repo, commit, files, args.path)
    out = Path(args.out).with_suffix(ext_of(data))
    sidecar = out.with_suffix(out.suffix + '.json')
    if not args.force and (out.exists() or sidecar.exists()):
        raise ValueError(f'Output already exists: {out}; use --force to replace')
    record = {'repo': args.repo, 'commit': commit, 'requested_path': args.path, 'path': path,
              'page': f'https://github.com/libretro-thumbnails/{args.repo}/blob/{commit}/{urllib.parse.quote(path)}',
              'file': str(out)}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    sidecar.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)
    search = sub.add_parser('search')
    search.add_argument('query')
    search.add_argument('--repo', action='append', required=True)
    search.add_argument('--kind', choices=KINDS)
    search.add_argument('--limit', type=int, default=30)
    get = sub.add_parser('get')
    get.add_argument('repo')
    get.add_argument('path')
    get.add_argument('--out', required=True)
    get.add_argument('--force', action='store_true')
    get.add_argument('--json', action='store_true', help='Compatibility flag; provenance is always saved')
    for command in (search, get):
        command.add_argument('--refresh', action='store_true', help='Rebuild cached repository index')
    sub.add_parser('repos', help='List cached repositories, not the complete upstream catalog')
    args = parser.parse_args()
    try:
        if args.cmd == 'search':
            cmd_search(args)
        elif args.cmd == 'get':
            cmd_get(args)
        else:
            print('\n'.join(p.stem for p in sorted(CACHE.glob('*.json'))))
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
