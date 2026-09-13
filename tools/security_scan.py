"""Scan local working files, full Git history and build output without printing secrets."""
from pathlib import Path
import re
import subprocess

patterns=[re.compile(rb'sk-(?:ant-|proj-)?[A-Za-z0-9_-]{24,}'),re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(rb'github_pat_[A-Za-z0-9_]{30,}'),re.compile(rb'AKIA[0-9A-Z]{16}'),re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
findings=[];count=0
def scan(location,data):
    global count
    count+=1
    if any(p.search(data) for p in patterns):findings.append(location)
for raw in subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard']).split(b'\0'):
    if raw and Path(raw.decode()).is_file():scan(raw.decode(),Path(raw.decode()).read_bytes())
for path in Path('web/dist').rglob('*'):
    if path.is_file():scan(str(path),path.read_bytes())
for line in subprocess.check_output(['git','rev-list','--objects','--all']).decode().splitlines():
    oid=line.split(' ',1)[0]
    if subprocess.check_output(['git','cat-file','-t',oid]).strip()==b'blob':scan('git-blob:'+oid,subprocess.check_output(['git','cat-file','blob',oid]))
print(f'Scanned {count} working/history/build objects. Possible secret locations: {len(findings)}')
for finding in findings:print(finding)
raise SystemExit(bool(findings))
