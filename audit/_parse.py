import json,re,xml.etree.ElementTree as E
from pathlib import Path
w=Path(__file__).parent
r=E.parse(w/'sources/official.xml').getroot()
m=r.find('norm/metadaten'); ab=m.findtext('jurabk'); year=m.findtext('ausfertigung-datum')[:4]
units=[]; canonical=['# '+m.findtext('langue'),'Stand: '+m.findtext('standangabe/standkommentar')]; structural=[]
def txt(e):
 if e is None:return ''
 # Insert block boundaries without altering words or inline markup.
 out=e.text or ''
 for c in e:
  t=txt(c)
  if c.tag in ('P','DL','DT','DD','LA','TR','BR'):out+='\n'+t+'\n'
  else:out+=t
  out+=c.tail or ''
 return out
for n in r.findall('norm'):
 md=n.find('metadaten'); label=md.findtext('enbez') or ''
 ge=md.find('gliederungseinheit')
 if ge is not None:structural=[(ge.findtext('gliederungsbez') or '')+' — '+(ge.findtext('gliederungstitel') or '')]
 if not label.startswith('§') and not label.startswith('Anlage'):continue
 text=re.sub(r'[ \t]+',' ',txt(n.find('textdaten/text/Content'))).strip()
 text=re.sub(r'\n[ \t]*\n+', '\n\n', text)
 title=' '.join(txt(md.find('titel')).split())
 num=int(re.search(r'\d+',label).group())
 chapter=1 if ab=='ProdHaftG' else (1 if num<=4 else 2 if num<=22 else 3)
 u=dict(id='p'+str(num),label=label,title=title,text=text,chapter=chapter,repealed=bool(re.fullmatch(r'\(?weggefallen\)?|\(?aufgehoben\)?',text,re.I)))
 u['structure']=list(structural)
 notes=[txt(e).strip() for e in n.findall('textdaten/fussnoten') if txt(e).strip()]
 if notes:u['notes']=notes
 units.append(u);canonical.extend(['## '+label+' '+title,text])
(w/'units.jsonl').write_text(''.join(json.dumps(u,ensure_ascii=False)+'\n' for u in units))
(w/'sources/canonical.md').write_text('\n\n'.join(canonical)+'\n')
chapters=[dict(n=1,slug='kommentar',title='Haftung, Schadensumfang und Schlussvorschriften')] if ab=='ProdHaftG' else [dict(n=1,slug='allgemeine-vorschriften',title='Allgemeine Vorschriften'),dict(n=2,slug='glaeubigerbeschluesse',title='Beschlüsse der Gläubiger'),dict(n=3,slug='schlussvorschriften',title='Bußgeld- und Übergangsbestimmungen')]
repo=f'Komentar-DE-{ab.upper()}-{year}'
meta=dict(cc='de',lang='de',repo=repo,repo_dir='/Volumes/LaCie/open-commentary/de/'+repo,title='Kommentar: '+m.findtext('langue'),source_path=str(w/'sources/canonical.md'),intro_file='00-einleitung.md',intro_desc='Grundlagen, Quellen und Methode',labels=dict(text='Wortlaut der Vorschrift',chapter='Kommentarkapitel',notes='Amtliche Anmerkung'),chapters=chapters)
(w/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print(repo,len(units),[u['label'] for u in units])
