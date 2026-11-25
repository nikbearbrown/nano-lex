"""Render one system/user packet per bundle. No model calls."""
import json, sys
from pathlib import Path
p=Path(__file__).resolve().parent.parent/'prompts'
system=(p/'system.txt').read_text()
template=(p/'user-template.txt').read_text()
with open(sys.argv[1],encoding='utf8') as src, open(sys.argv[2],'x',encoding='utf8') as out:
    for line in src:
        if not line.strip(): continue
        r=json.loads(line)
        print(json.dumps({'concept_id':r['concept_id'],'system':system,'user':template.replace('{{bundle}}',json.dumps(r,ensure_ascii=False,indent=2))},ensure_ascii=False),file=out)
