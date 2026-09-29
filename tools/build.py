"""Build the site in place. Run from the project root after any edit:

    python tools/build.py            stamp partials + structured data, then run checks
    python tools/build.py --images   also regenerate images (needs Pillow)
    python tools/build.py --quiet    only print failures
    python tools/build.py --committed
                                     fail if building changed any file (use before
                                     committing to be sure you ran the build)

Netlify runs "python3 tools/build.py --quiet" on every deploy, so the published
pages are always freshly stamped (current © year, next 12 months of holiday
hours, live status config). A deploy is blocked only if tools/check.py fails.

Steps: build-images (optional) -> build-partials -> build-schema -> check.
Running it twice in a row changes nothing the second time.
"""
import hashlib
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')


def snapshot():
    out = {}
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', 'font-src', '__pycache__', '.playwright-mcp')]
        for f in files:
            if f.endswith(('.html', '.js', '.css', '.xml')):
                p = os.path.join(base, f)
                out[p] = hashlib.sha1(open(p, 'rb').read()).hexdigest()
    return out


def run(script, *args):
    print(f'--> {script} {" ".join(args)}'.rstrip())
    r = subprocess.run([sys.executable, os.path.join(TOOLS, script), *args], cwd=ROOT)
    if r.returncode:
        sys.exit(r.returncode)


def main():
    before = snapshot()
    if '--images' in sys.argv:
        run('build-images.py')
    run('build-partials.py')
    run('build-schema.py')
    after = snapshot()
    changed = sorted(os.path.relpath(p, ROOT) for p in after if before.get(p) != after[p])
    if changed:
        print(f'updated {len(changed)} file(s)')
    if '--committed' in sys.argv and changed:
        print('FAIL: the build changed files. Commit these after reviewing them:')
        for c in changed:
            print('   ', c)
        sys.exit(1)
    run('check.py', *(['--quiet'] if '--quiet' in sys.argv else []))


if __name__ == '__main__':
    main()
