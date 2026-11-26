"""Regenerate the .docx files from the .md sources in the folder above.

Usage: python3 tools/build_docx.py            (all papers except README and TEMPLATE)
       python3 tools/build_docx.py FILE.md ... (selected files)
Needs python-docx (pip install python-docx). Handles headings, paragraphs, bullet and
numbered lists, pipe tables, bold, italics, code and links (as text).
"""
import re,os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
INL=re.compile(r'(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))')
def add_inline(p,text):
    text=text.replace('\\*','*')
    for part in INL.split(text):
        if not part: continue
        if part.startswith('**') and part.endswith('**'): r=p.add_run(part[2:-2]); r.bold=True
        elif part.startswith('`') and part.endswith('`'): r=p.add_run(part[1:-1]); r.font.name='Consolas'; r.font.size=Pt(9.5)
        elif part.startswith('[') and '](' in part:
            m=re.match(r'\[([^\]]+)\]\(([^)]+)\)',part); r=p.add_run(m.group(1)); r.font.color.rgb=RGBColor(0x1F,0x4E,0x99)
        elif part.startswith('*') and part.endswith('*') and len(part)>2: r=p.add_run(part[1:-1]); r.italic=True
        else: p.add_run(part)
def convert(md,out):
    d=Document(); st=d.styles['Normal']; st.font.name='Calibri'; st.font.size=Pt(11)
    lines=open(md).read().split('\n'); i=0
    while i<len(lines):
        l=lines[i]
        if l.startswith('|') and i+1<len(lines) and re.match(r'^\|[\s:\-|]+\|$',lines[i+1]):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                if not re.match(r'^\|[\s:\-|]+\|$',lines[i]):
                    rows.append([c.strip() for c in re.split(r'(?<!\\)\|',lines[i].strip())[1:-1]])
                i+=1
            n=max(len(r) for r in rows); t=d.add_table(rows=len(rows),cols=n); t.style='Table Grid'
            for ri,row in enumerate(rows):
                for ci in range(n):
                    cell=t.cell(ri,ci); cell.text=''; p=cell.paragraphs[0]
                    add_inline(p,row[ci] if ci<len(row) else '')
                    for r in p.runs:
                        r.font.size=Pt(9)
                        if ri==0: r.bold=True
            d.add_paragraph(); continue
        m=re.match(r'^(#{1,4}) (.*)',l)
        if m:
            lvl=len(m.group(1)); h=d.add_heading(level=0 if lvl==1 else lvl-1); add_inline(h,m.group(2)); i+=1; continue
        if l.startswith('~~~') or l.startswith('```'):
            i+=1; buf=[]
            while i<len(lines) and not (lines[i].startswith('~~~') or lines[i].startswith('```')): buf.append(lines[i]); i+=1
            p=d.add_paragraph(); r=p.add_run('\n'.join(buf)); r.font.name='Consolas'; r.font.size=Pt(9); i+=1; continue
        m=re.match(r'^(\s*)[-*] (\[[ x]\] )?(.*)',l)
        if m:
            p=d.add_paragraph(style='List Bullet' if len(m.group(1))<2 else 'List Bullet 2')
            if m.group(2): p.add_run('☐ ')
            add_inline(p,m.group(3)); i+=1; continue
        m=re.match(r'^\s*\d+\. (.*)',l)
        if m:
            p=d.add_paragraph(style='List Number'); add_inline(p,m.group(1)); i+=1; continue
        if l.strip()=='' or l.strip()=='---': i+=1; continue
        if l.startswith('!['): i+=1; continue
        p=d.add_paragraph(); add_inline(p,l); i+=1
    d.save(out)

if __name__=='__main__':
    import glob,sys
    here=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    targets=sys.argv[1:] or [f for f in sorted(glob.glob(os.path.join(here,'*.md'))) if os.path.basename(f) not in ('README.md','TEMPLATE.md')]
    for f in targets:
        convert(f,f[:-3]+'.docx'); print('wrote',os.path.relpath(f[:-3]+'.docx',here))
