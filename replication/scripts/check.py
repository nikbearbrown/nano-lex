"""Check complete seed coverage, entry shape, and the upstream evidence rules."""
import csv, hashlib, json, sys
from pathlib import Path
from verify_drafts import verify

def records(path):
    result={}
    with open(path,encoding='utf8') as f:
        for line in f:
            if not line.strip(): continue
            row=json.loads(line)
            key=row['concept_id']
            if key in result: raise ValueError(f'{path}: duplicate {key}')
            result[key]=row
    return result

def check(e,b):
    errors=[]
    def need(ok,msg):
        if not ok: errors.append(msg)
    def string(v): return isinstance(v,str) and bool(v.strip())
    def nullable(v): return v is None or string(v)
    def exact(o,keys): return isinstance(o,dict) and o.keys()==set(keys.split())
    shape='concept_id work_sense links definition variants relations flags'
    need(set(e)-{'_meta'}==set(shape.split()),'wrong top-level keys')
    need(string(e.get('work_sense')),'work_sense missing')
    links=e.get('links')
    need(exact(links,'wikipedia wikidata wordnet') and all(exact(x,'choice reason') and nullable(x['choice']) and string(x['reason']) for x in links.values()),'invalid links')
    groups=[([e.get('definition')],'text basis pointers'),(e.get('variants'),'text condition basis pointers'),(e.get('relations'),'type target_label target_id proposed_new basis pointers note')]
    for rows,keys in groups:
        if not isinstance(rows,list):
            errors.append('invalid list: '+keys)
            continue
        for x in rows:
            valid=exact(x,keys)
            if valid:
                valid=(isinstance(x['pointers'],list) and all(map(string,x['pointers'])) and
                       x['basis'] in ('source','model_knowledge') and
                       not(x['basis']=='model_knowledge' and x['pointers']))
                valid=valid and (string(x['text']) if 'text' in x else string(x['target_label']) and nullable(x['target_id']) and isinstance(x['proposed_new'],bool) and x['proposed_new']==(x['target_id'] is None) and nullable(x['note']))
                if 'condition' in x: valid=valid and nullable(x['condition'])
                if x.get('target_id')==e['concept_id'] or x.get('type')=='certifies': valid=False
            need(valid,'invalid claim: '+keys)
    flags=e.get('flags')
    need(isinstance(flags,list) and all(map(string,flags)),'invalid flags')
    if errors: return errors,[]
    return verify(e,b)

def main():
    bundle_path,draft_path,report_path=sys.argv[1:]
    data=Path(__file__).resolve().parents[2]/'data'
    source=data/'seeds.tsv'
    manifest=json.loads((data/'source-manifest.json').read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest()!=manifest['sha256']:
        raise ValueError('seed SHA-256 differs from manifest')
    with source.open(encoding='utf8') as f:
        seeds={x['concept_id']:x['preferred_name'] for x in csv.DictReader(f,delimiter='\t')}
    if len(seeds)!=manifest['seed_count']: raise ValueError('seed count differs from manifest')
    b,d=records(bundle_path),records(draft_path)
    unexpected=(set(b)|set(d))-seeds.keys()
    if unexpected: raise ValueError('unknown seed IDs: '+str(sorted(unexpected)[:20]))
    passed=0
    with open(report_path,'w',encoding='utf8') as f:
        for key,title in seeds.items():
            bundle=b.get(key)
            entry=d.get(key)
            errors,warns=[],[]
            if bundle is None: errors.append('missing source bundle')
            if entry is None: errors.append('missing draft')
            if bundle is not None:
                concept=bundle.get('concept',{})
                if (set(bundle)!=set('concept_id concept neighbors examples wikipedia wikidata wordnet'.split()) or
                    concept.get('id')!=key or concept.get('preferred_name')!=title):
                    errors.append('bundle shape or seed identity mismatch')
            if not errors:
                try: errors,warns=check(entry,bundle)
                except (ValueError,KeyError,TypeError,AttributeError) as exc:
                    errors=[f'malformed bundle or entry: {exc}']
            passed+=not errors
            f.write(json.dumps({'concept_id':key,'status':'fail' if errors else 'pass','errors':errors,'warnings':warns})+'\n')
    print(f'{passed}/{len(seeds)} seeds passed')
    return 0 if passed==len(seeds) else 1

if __name__=='__main__':
    sys.exit(main())
