"""Native Codex plugin installation into an explicitly isolated profile."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from package_plugin import NAME, MARKETPLACE, ROOT, records, write_directory


def prepare(profile, package=None):
    profile = Path(os.path.expandvars(os.path.expanduser(str(profile)))).resolve()
    default = Path(os.environ.get("CODEX_HOME", str(Path.home()/".codex"))).resolve()
    if profile in (default, Path.home().resolve(), (Path.home()/".codex").resolve()):
        raise ValueError("Choose a separate Codex test/profile directory; global profiles are refused")
    package = Path(package).resolve() if package else profile.parent/"instagram-plugin-source-0.1.0"
    if profile.is_relative_to(package) or package.is_relative_to(profile):
        raise ValueError("Plugin source and profile/cache must be separate directories")
    data=records()
    if package.exists():
        current={p.relative_to(package).as_posix():p.read_bytes() for p in package.rglob('*') if p.is_file()}
        if current!=data:
            raise ValueError("Different source snapshot exists; choose a fresh package directory")
    return profile, package


def install(profile, package=None, dry_run=False, codex="codex"):
    profile, package=prepare(profile,package)
    result={"plugin":NAME,"codex_home":str(profile),"source_package":str(package),"dry_run":dry_run}
    if dry_run:return result
    write_directory(package)
    profile.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,CODEX_HOME=str(profile))
    operations=(['plugin','marketplace','add',str(package),'--json'],
                ['plugin','add',NAME+'@'+MARKETPLACE,'--json'],
                ['plugin','list','--marketplace',MARKETPLACE,'--json'])
    receipts=[]
    for args in operations:
        run=subprocess.run([codex,*args],env=env,capture_output=True,encoding='utf-8',timeout=60)
        if run.returncode:
            raise ValueError(f"Native Codex {' '.join(args[:2])} failed ({run.returncode}): {run.stderr[-1000:]}")
        receipts.append(json.loads(run.stdout))
    installed=receipts[-1].get('installed',[])
    if not any(p.get('pluginId')==NAME+'@'+MARKETPLACE and p.get('installed') and p.get('enabled') for p in installed):
        raise ValueError("Native Codex did not confirm installed/enabled plugin")
    result['native_results']=receipts
    return result


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-home',required=True,help='separate profile directory; global home is refused')
    parser.add_argument('--package-dir',help='separate clean plugin source directory')
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    try:
        print(json.dumps(install(args.codex_home,args.package_dir,args.dry_run),indent=2,ensure_ascii=False))
        print('Launch Codex with this CODEX_HOME. Sign in using the normal Codex browser flow if needed; the installer never copies authentication.')
    except (OSError,ValueError,KeyError,subprocess.TimeoutExpired) as exc:
        print(f'error: {exc}',file=sys.stderr)
        raise SystemExit(2)
