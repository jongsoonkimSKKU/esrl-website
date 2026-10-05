"""Generate the lab's static pages from public, editable content.json."""
from pathlib import Path
from html import escape as e
import json
import hashlib
ROOT=Path(__file__).parent
D=json.loads((ROOT/'content.json').read_text())
D['publications']=json.loads((ROOT/'publications.json').read_text())
JOURNAL_METRICS=json.loads((ROOT/'journal_metrics.json').read_text())
LAB_LIFE=json.loads((ROOT/'lab_life.json').read_text())
DIST=ROOT/'dist'
STYLESHEET_VERSION=hashlib.sha256((DIST/'style.css').read_bytes()).hexdigest()[:12]
SCRIPT_VERSION=hashlib.sha256((DIST/'site.js').read_bytes()).hexdigest()[:12]
ARROW='<span class="arrow" aria-hidden="true">↗</span>'
NAV=[('Home','/'),('Research','/research/'),('Professor','/professor/'),('People','/people/'),('Publications','/publications/'),('Lab life','/life/')]
PUBLICATION_GROUPS=[('2026',['2026']),('2025',['2025']),('2024',['2024']),('2023',['2023']),('2022',['2022']),('2021',['2021']),('2020',['2020']),('2019',['2019']),('2018–2017',['2018','2017']),('2016–2015',['2016','2015']),('2014–2012',['2014','2013','2012']),('2011–2009',['2011','2010','2009'])]
def pubroute(label):return '/publications/'+label.replace('–','-')+'/'
def navigation(route):
 items=[]
 for label,url in NAV:
  if label in ('People','Publications'):
   entries=[('Current members · 현재 구성원','/people/'),('Alumni · 졸업생','/people/alumni/')] if label=='People' else [('All papers · 전체','/publications/')]+[(label,pubroute(label)) for label,_ in PUBLICATION_GROUPS]
   active=route.startswith(url)
   links=''.join(f'<a href="{href}"'+(' aria-current="page"' if route==href else '')+f'>{text}</a>' for text,href in entries)
   items.append(f'<details class="nav-group'+(' active' if active else '')+'"><summary>'+label+'<span aria-hidden="true">⌄</span></summary><div class="nav-submenu'+(' publication-menu' if label=='Publications' else '')+'">'+links+'</div></details>')
  else:items.append(f'<a href="{url}"'+(' aria-current="page"' if route==url else '')+f'>{label}</a>')
 return ''.join(items)
def people_tabs(active):
 return '<nav class="year-nav people-tabs" aria-label="People pages">'+''.join(f'<a href="{url}"'+(' aria-current="page"' if key==active else '')+f'>{label}</a>' for key,url,label in [('current','/people/','Current members · 현재 구성원'),('alumni','/people/alumni/','Alumni · 졸업생')])+'</nav>'
from urllib.parse import quote
import re
SCHOLAR_METRICS=json.loads((ROOT/'scholar_metrics.json').read_text())
SCHOLAR=SCHOLAR_METRICS['source']
KEYWORDS=[('lithium','Lithium / Li · 리튬',r'\blithium\b|\blibs?\b|\bli(?=$|[^a-z])|(?-i:\bLi(?=[A-Zxy]))'),('sodium','Sodium / Na · 소듐',r'\bsodium\b|\bna(?=$|[^a-z])|(?-i:\bNa(?=[A-Zxy]))'),('potassium','Potassium / K · 포타슘',r'\bpotassium\b|\bk(?=$|[^a-z])|(?-i:\bK(?=[A-Zxy]))'),('zinc','Zinc / Zn · 아연',r'\bzinc\b|\bzn(?=$|[^a-z])|(?-i:\bZn(?=[A-Zxy]))'),('solid','Solid-state · 전고체',r'solid.state|solid electrolyte'),('oxygen','Oxygen redox · 산소 산화환원',r'oxygen.redox|anionic.redox'),('modeling','Calculation · 계산',r'first.princip|calculation|computational|simulation'),('interface','Interfaces · 계면',r'interfac|interphase|coating|surface')]
def journal_key(name):
 return re.sub(r'[^a-z0-9]','',name.lower().replace('&','and').replace('journal of material chemistry a','journal of materials chemistry a'))
def category_top(category):
 return 100*category['rank']/category['total'] if 'rank' in category else category['top_percent']
def category_rank(category):
 return f"{category['rank']}/{category['total']} journals" if 'rank' in category else f"JCR Top {category_top(category):.2f}%"+(f" · {category['total']} journals" if category.get('total') else '')
def journal_metrics(p):
 name=p['citation'].split(',')[0]
 journal=JOURNAL_METRICS['journals'].get(journal_key(name),{})
 year=int(p['year'])-1
 metric=journal.get('years',{}).get(str(year))
 if not metric:return ''
 categories=sorted(metric.get('categories',[]),key=lambda c:(category_top(c),c['category']))
 impact=metric.get('impact_factor');badges=[]
 if impact is not None:badges.append(f'<span class="journal-if">IF <strong>{float(impact):.1f}</strong></span>')
 if categories:
  best=categories[0];top=category_top(best)
  badges.append(f'<span class="journal-top">JCR Top <strong>{top:.2f}%</strong></span>')
 if not badges:return ''
 badges.append(f'<span class="journal-metric-year">{year} metrics</span>')
 out='<details class="journal-metrics"><summary>'+''.join(badges)+'<span class="journal-metric-toggle">Details · 지표 정보</span></summary><div class="journal-metric-detail">'
 out+=f'<p lang="ko">논문 게재연도({p["year"]})의 전년도인 {year}년 IF·JCR 지표를 표시합니다.</p>'
 if categories:
  out+='<p><strong>Best-ranked category · 최상위 분야</strong><br>'+e(best['category'])+f' · {category_rank(best)}</p>'
  out+='<ul>'+''.join(f'<li><span>{e(c["category"])}</span><span>{category_rank(c)}'+(f' · Top {category_top(c):.2f}%' if 'rank' in c else '')+'</span></li>' for c in categories)+'</ul>'
 sources=[s for s in metric.get('sources',[]) if s.get('url') and 'akaturk.com' not in s['url'] and s['label'].startswith('IF')]
 out+='<p class="journal-metric-sources">'+ ' · '.join([f'JCR {year}']+[f'<a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["label"])}</a>' for s in sources])+'</p>'
 return out+'</div></details>'
def bibtex(p,key):
 author=re.sub(r'[†‡*]','',p['authors'])
 author=' and '.join(a.strip() for a in author.replace(' and ',', ').split(',') if a.strip())
 fields={'title':p['title'],'author':author,'journal':p['citation'].split(',')[0],'year':str(p['year'])}
 if p.get('url'):fields['url']=p['url']
 if 'doi.org/' in p.get('url',''):fields['doi']=p['url'].split('doi.org/',1)[1]
 def safe(s):return s.replace('\\',r'\textbackslash{}').replace('{',r'\{').replace('}',r'\}').replace('&',r'\&').replace('%',r'\%').replace('_',r'\_')
 return '@article{'+key+',\n'+',\n'.join('  '+k+' = {'+safe(v)+'}' for k,v in fields.items())+'\n}'
def publication_title(p):
 text=e(p['title'])
 return f'<a href="{e(p["url"])}" target="_blank" rel="noopener noreferrer">{text}</a>' if p.get('url') else text
def publication_library(papers,label):
 from html import escape as e
 selected=lambda x:' aria-current="page"' if x==label else ''
 nav='<nav class="year-nav" aria-label="Publication year"><a href="/publications/"'+selected('All')+'>All papers · 전체</a>'+''.join('<a href="'+pubroute(other)+'"'+selected(other)+'>'+other+'</a>' for other,_ in PUBLICATION_GROUPS)+'</nav>'
 journals=sorted(set(p['citation'].split(',')[0] for p in papers));years=sorted(set(str(p['year']) for p in papers),reverse=True)
 out='<section class="section publication-library"><div class="wrap">'+nav
 out+=f'''<div class="publication-metrics"><a href="{e(SCHOLAR)}" target="_blank" rel="noopener noreferrer"><strong>{SCHOLAR_METRICS['publications']:,}</strong><span>논문 총수 · Publications</span></a><a href="{e(SCHOLAR)}" target="_blank" rel="noopener noreferrer"><strong>{SCHOLAR_METRICS['citations']:,}</strong><span>총인용수 · Citations</span></a><a href="{e(SCHOLAR)}" target="_blank" rel="noopener noreferrer"><strong>{SCHOLAR_METRICS['h_index']}</strong><span>h-index · Google Scholar</span></a></div><p class="metrics-date">Google Scholar 전체 지표 · 확인일 / Checked {e(SCHOLAR_METRICS['checked_at'])} · <a href="{e(SCHOLAR)}" target="_blank" rel="noopener noreferrer">View profile ↗</a></p>'''
 out+='''<details class="journal-metrics-guide"><summary>About IF &amp; JCR · 지표 기준</summary><p lang="ko">IF와 JCR 순위는 모든 논문에 대해 게재연도의 전년도 저널 지표를 사용합니다. 예를 들어 2026년 논문에는 2025년, 2025년 논문에는 2024년 지표를 표시합니다. JCR 상위 %는 (분야 내 순위 ÷ 해당 분야 저널 수) × 100으로 계산하며, 여러 분야 중 가장 낮은 값을 표시합니다. IF는 소수 첫째 자리로 통일하며, 근거 자료를 확보한 항목만 표시합니다.</p><p>All papers use journal metrics from the year before publication: 2026 papers use 2025 metrics, and 2025 papers use 2024 metrics. JCR Top % is rank divided by category size × 100, using the lowest value across categories. IF values are shown to one decimal place. Sources and categories are available within each record.</p></details>'''
 out+='<div class="publication-controls" data-library><div class="publication-layout"><aside class="publication-sidebar"><span class="eyebrow">Explore the evidence<br><span lang="ko">연구 성과 찾아보기</span></span><div class="pub-filters"><label>SEARCH · 검색<input type="search" data-search placeholder="Title, author, journal · 제목, 저자, 학술지" autocomplete="off"></label><label>YEAR · 연도<select data-year><option value="">All years · 전체</option>'+''.join(f'<option>{y}</option>' for y in years)+'</select></label><label>JOURNAL · 학술지<select data-journal><option value="">All journals · 전체</option>'+''.join(f'<option>{e(j)}</option>' for j in journals)+'</select></label></div><div class="keyword-filters" aria-label="Title keyword filters">'
 for key,name,pattern in KEYWORDS:out+=f'<button type="button" class="keyword-filter" data-keyword="{key}" aria-pressed="false">{name}</button>'
 out+='</div><p class="keyword-help" lang="ko">키워드는 논문 제목을 기준으로 검색하며, Lithium/Li, Sodium/Na, Potassium/K, Zinc/Zn을 각각 함께 검색합니다. Calculation은 제일원리계산·계산·시뮬레이션 관련 제목을 검색합니다. 여러 개를 선택하면 하나 이상에 해당하는 논문을 표시합니다.</p></aside><div class="publication-records"><div class="publication-results"><p role="status" aria-live="polite" data-result-count>'+str(len(papers))+' publications</p><button type="button" data-reset>Reset filters · 초기화</button></div><p class="publication-legend">† / ‡ Equal contribution · * Corresponding author</p><p class="publication-empty" data-empty hidden>검색 결과가 없습니다. 검색어나 필터를 변경해 주세요.<br>No papers match these filters.</p><div class="publication-cards">'
 for i,p in enumerate(papers):
  tags=[key for key,_,pattern in KEYWORDS if re.search(pattern,p['title'],re.I)];key='esrl'+str(p['year'])+'paper'+str(i+1)
  cite=p['authors']+'. '+p['title']+'. '+p['citation']+'.';bib=bibtex(p,key);journal=p['citation'].split(',')[0]
  out+=f'<article class="publication-card" data-paper data-year="{p["year"]}" data-journal="{e(journal)}" data-keywords="{" ".join(tags)}"><span class="publication-number" aria-hidden="true">{len(papers)-i:03d}</span><div class="publication-card-top"><span>{e(p["citation"])}</span><span>{p["year"]}</span></div><h3>{publication_title(p)}</h3><p class="publication-authors">{e(p["authors"])}</p><div class="publication-tags">'+''.join(f'<span>{e(name.split(" · ")[0])}</span>' for key2,name,_ in KEYWORDS if key2 in tags)+'</div>'
  out+=journal_metrics(p)
  pdf=f'<a href="{e(p["pdf_url"])}" target="_blank" rel="noopener noreferrer">PDF ↗</a>' if p.get("pdf_url") else ""
  article_page=f'<a href="{e(p["url"])}" target="_blank" rel="noopener noreferrer">{e(p.get("link_label", "Article page ↗"))}</a>' if p.get("url") else ""
  out+=f'<div class="publication-links">{article_page}{pdf}<a href="https://scholar.google.com/scholar?q={quote(p["title"])}" target="_blank" rel="noopener noreferrer">Google Scholar ↗</a><button type="button" data-copy-citation>Copy citation</button></div>'
  out+=f'<details class="citation-details"><summary>Citation &amp; BibTeX · 인용 정보</summary><p class="citation-text">{e(cite)}</p><pre class="bibtex-text">{e(bib)}</pre><div class="citation-actions"><button type="button" data-copy-bib>Copy BibTeX</button><button type="button" data-download-bib data-filename="{key}.bib">Download .bib ↓</button></div></details>'
  if p.get('note'):out+=f'<p class="publication-note">{e(p["note"])}</p>'
  out+='</article>'
 return out+'</div><p class="copy-feedback" role="status" aria-live="polite"></p></div></div></div></div></section>'

def img(src,alt,cls='',eager=False):return f'<img src="{e(src)}" alt="{e(alt)}" class="{cls}" loading="{"eager" if eager else "lazy"}" decoding="async">'
def link(href,label,cls='text-link',external=False):return f'<a href="{e(href)}" class="{cls}"'+(' target="_blank" rel="noopener noreferrer"' if external else '')+f'>{label}{ARROW}</a>'
def shell(title,route,content,description=None):
 descriptions={'/':'리튬·소듐이온전지용 저가형 고성능 양극과 전고체전지용 고체전해질을 연구합니다. AI·제일원리계산·합성·실험을 연결하는 ESRL을 만나보세요.','/research/':'양극과 고체전해질의 소재 설계, 산화환원 반응, 이온 이동 및 계면 안정성 연구와 AI·cluster expansion 연구를 소개합니다.','/join/':'학부연구생·대학원생·박사후연구원 모집 안내. 등록금 전액·인건비 지원, 지원 서류, 문의 시기와 지원 절차를 확인하세요.','/professor/':'성균관대학교 김종순 교수의 연구 관심 분야, 경력, 학력, 수상, 학회 활동 및 국가 R&D 기획 이력을 소개합니다.','/people/':'ESRL 현재 구성원과 각 학생의 양극·고체전해질·제일원리계산·AI 연구주제를 소개합니다.','/people/alumni/':'ESRL 석사·박사 졸업생의 학위, 졸업 시기와 확인된 소속을 소개합니다.','/equipment/':'소재 합성, 전지 조립, 전기화학 평가 및 계산 연구에 활용하는 ESRL 장비 22종을 소개합니다.','/publications/':'ESRL 전체 논문 164편과 DOI·PDF 링크, 연도·저널·키워드 검색 및 전년도 IF·JCR 지표를 제공합니다.','/life/':'연구실 행사, 학회, 졸업식과 함께한 일상의 사진을 연도별 앨범으로 만나보세요.'}
 description=description or descriptions.get(route)
 if description is None:
  if route.startswith('/publications/'):description=title.replace('Publications · ','')+'년 ESRL 논문 목록과 논문 링크, 전년도 IF·JCR 지표를 확인하세요.'
  elif route.startswith('/life/albums/'):description=re.sub('<[^>]+>','',title)+' · ESRL 행사 사진 앨범입니다.'
  elif route.startswith('/life/'):description=title.replace('Lab life · ','')+'년 ESRL 연구실 행사와 일상 사진을 확인하세요.'
  else:description='ESRL 홈페이지에서 배터리 소재 연구와 연구실 소식을 확인하세요.'
 description='성균관대 김종순 교수 연구실 · '+description
 nav=navigation(route)
 return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} · 성균관대 김종순 교수 연구실 · ESRL</title><meta name="description" content="{e(description)}"><meta name="theme-color" content="#0a1d32"><link rel="icon" type="image/png" href="/assets/esrl-firefly-logo.png"><link rel="stylesheet" href="/style.css?v={STYLESHEET_VERSION}"><script src="/site.js?v={SCRIPT_VERSION}" defer></script></head><body>
 <a class="skip" href="#main">Skip to content</a><div class="topline"><div class="wrap"><span>SUNGKYUNKWAN UNIVERSITY</span><span lang="ko">성균관대학교 에너지 저장 연구실</span></div></div>
 <header class="site-header"><div class="wrap header-inner"><a class="brand" href="/" aria-label="ESRL home"><span class="brand-lockup"><span class="brand-mark">ESRL</span><span class="firefly-mark header-firefly"><img src="/assets/esrl-firefly-logo.png" alt="" width="48" height="48"></span></span><span class="brand-name">Energy Storage<br>Research Lab.</span></a><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="navigation">Menu ☰</button><nav id="navigation" class="nav" aria-label="Main navigation">{nav}<a class="join-link" href="/join/">Join us {ARROW}</a></nav></div></header>
 <main id="main">{content}</main>
 <footer class="site-footer"><div class="wrap"><div class="footer-main"><div><div class="footer-brand"><span class="firefly-mark footer-firefly"><img src="/assets/esrl-firefly-logo.png" alt="ESRL battery firefly logo" width="80" height="80" loading="lazy"></span><div class="footer-title">Energy Storage<br>Research Lab.</div></div><div>Sungkyunkwan University<br>Department of Energy Science</div></div><div><span class="footer-label">CONTACT</span><a href="mailto:jongsoonkim@skku.edu">jongsoonkim@skku.edu</a><br><a href="tel:+82312996271">+82 31 299 6271</a><br>N-Center, Room 86679</div><div><span class="footer-label">EXPLORE</span><a href="/equipment/">Equipment & facilities</a><br><a href="/professor/">Principal investigator</a><br><a href="/join/">Student & postdoctoral opportunities</a></div></div><div class="footer-bottom"><span>© 2026 Energy Storage Research Lab. Sungkyunkwan University.</span><span>Materials. Mechanisms. Energy.</span></div></div></footer></body></html>'''
def save(route,title,body):
 p=DIST/route.strip('/')/'index.html' if route!='/' else DIST/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(shell(title,route,body))
def title(label,heading,desc=''):return f'<section class="page-title"><div class="wrap"><span class="eyebrow">{label}</span><h1>{heading}</h1>'+ (f'<p>{desc}</p>' if desc else '')+'</div></section>'
def paper(p,authors=True):
 citation=p['citation'];journal=citation.split(',')[0];detail=citation[len(journal):].strip(', ')
 metric_p=dict(p,year=p.get('year') or re.search(r'(20\d{2})',citation)[1])
 pdf=f'<a href="{e(p["pdf_url"])}" target="_blank" rel="noopener noreferrer">PDF ↗</a>' if p.get('pdf_url') else ''
 read_link=f'<a class="paper-arrow" href="{e(p["url"])}" target="_blank" rel="noopener noreferrer" aria-label="Read {e(p["title"])}">{ARROW}</a>' if p.get('url') else ''
 return f'<article class="paper-row"><div class="paper-journal">{e(journal)}<span class="paper-year">{e(detail)}</span></div><div><h3 class="paper-title">{publication_title(p)}</h3>'+(f'<p class="paper-authors">{e(p["authors"])}</p>' if authors else '')+journal_metrics(metric_p)+(f'<div class="publication-links">{pdf}</div>' if pdf else '')+'</div>'+read_link+'</article>'

research=[('01','Lithium-ion batteries','리튬이온전지','고에너지밀도와 고속충전, 안정적인 수명을 위한 전극 소재를 설계합니다.','LAYERED OXIDES · OLIVINE · ROCKSALT'),('02','Beyond lithium','차세대 이차전지','소듐·포타슘 이온전지와 수계 아연전지 등 다양한 에너지 저장 시스템을 연구합니다.','Na-ION · K-ION · AQUEOUS Zn'),('03','Solid-state batteries','전고체전지','전극과 고체전해질 사이의 계면을 이해하고, 안정적인 이온 전달을 위한 소재를 개발합니다.','INTERFACES · COATINGS · ION TRANSPORT')]
cards='''<a href="/research/#cathodes" class="research-card core-card"><span class="number">01 / CORE EXPERTISE</span><h3>Cathodes for Li- and Na-ion batteries</h3><span class="card-name-ko" lang="ko">저가형 고성능 양극</span><p lang="ko">리튬이온전지와 소듐이온전지용 저가형 고성능 양극을 설계합니다. 조성·결정구조·산화환원 반응을 분석해 에너지밀도·출력·수명을 높이는 원리를 규명합니다.</p><span class="core-en">Cost-effective, high-performance cathodes for lithium-ion and sodium-ion batteries.</span><span class="card-footer">LAYERED OXIDES · PHOSPHATES · DISORDERED ROCKSALT ↗</span></a><a href="/research/#solid-electrolytes" class="research-card core-card"><span class="number">02 / CORE EXPERTISE</span><h3>Solid electrolytes</h3><span class="card-name-ko" lang="ko">전고체전지용 고체전해질</span><p lang="ko">전고체전지용 고체전해질의 이온 전도와 구조·화학적 안정성을 이해하고, 양극과 맞닿는 계면까지 함께 설계합니다.</p><span class="core-en">Solid electrolytes for all-solid-state batteries: ion transport, stability, and cathode interfaces.</span><span class="card-footer">SULFIDES · HALIDES · CATHODE–ELECTROLYTE INTERFACES ↗</span></a>'''

def profile_id(name):return 'researcher-'+re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')
def cta(href,label,cls='text-link'):return f'<a href="{e(href)}" class="{cls}">{label}</a>'
def story_paper(doi):return next(p for p in D['publications']+[p for archive in D['publication_archive'].values() for p in archive] if p.get('doi')==doi)
STUDENT_STORIES=[
 {'doi':'10.1021/acsenergylett.6c02530','topic':'Na-ion cathodes · Fe 이동 억제','question':'소듐 양극의 고전압 구조를 안정화하려면?','summary':'Fe 산화에 따른 구조 왜곡과 Fe 이동 경로를 분석하고 고전압 작동 안정성을 개선한 연구입니다.','people':[('Taegyu Kim','T. Kim','제1저자 · 김태규','current')]},
 {'doi':'10.1021/acsnano.5c22044','topic':'Li-ion cathodes · 리튬 양극','question':'리튬이 더 빠르게 움직이려면?','summary':'양이온 배열을 제어해 리튬이 이동하는 경로를 개선하는 양극 연구입니다.','people':[('Jinho Ahn','J. Ahn','공동 제1저자 · 졸업생','alumni'),('Bonyoung Ku','B. Ku','공동 제1저자','current')]},
 {'doi':'10.1016/j.ensm.2026.105375','topic':'Na-ion cathodes · 소듐 양극','question':'저가형 소듐 양극의 성능을 높이려면?','summary':'철·망간 중심 양극의 산화환원 반응을 조절해 초기 소듐 추출을 높이는 연구입니다.','people':[('Sunghyun Lim','S. Lim','제1저자','current')]},
 {'doi':'10.1002/aenm.202505121','topic':'Li-ion cathodes · Co-free·Ni 최소화 양극','question':'초저가 조성에서 높은 에너지밀도와 수명을 함께 얻으려면?','summary':'초기 충전 활성화와 전이금속 이동 억제를 연결해 초저가·고성능 양극을 구현한 연구입니다.','people':[('Jinho Ahn','J. Ahn','제1저자 · 졸업생','alumni')]},
 {'doi':'10.1039/d0ee02803g','topic':'Na-ion cathodes · Na₂Fe₂F₇ 최초 설계','question':'높은 성능과 낮은 가격을 함께 갖춘 새로운 양극을 설계하려면?','summary':'층상형 양극과 Fe계 polyanion 양극의 장점을 결합해 연구실이 최초로 설계·검증한 Na₂Fe₂F₇ 양극입니다.','people':[('Hyunyoung Park','H. Park','공동 제1저자 · 졸업생','alumni'),('Yongseok Lee','Y. Lee','공동 제1저자 · 졸업생','alumni')]},
 {'doi':'10.1016/j.ensm.2026.105167','topic':'All-solid-state batteries · 전고체전지','question':'전고체전지의 계면을 더 안정하게 만들려면?','summary':'양극과 고체전해질 사이의 접착력을 높이는 코팅으로 계면 안정성과 성능을 개선하는 연구입니다.','people':[('Junseong Kim','J. Kim','공동 제1저자','current'),('Hoseok Lee','H. Lee','공동 제1저자','current')]},
 {'doi':'10.1002/aenm.202506130','topic':'Li-ion cathodes · LMFP · LiF-less CEI','question':'고로딩 LMFP를 더 빠르게 충전하려면?','summary':'LiF-less CEI 설계로 전하 전달 저항을 낮춰 고로딩 LMFP의 고속충전 성능과 수명을 높인 연구입니다.','people':[('Bonyoung Ku','B. Ku','공동 제1저자','current'),('Lahyeon Jang','L. Jang','공동 제1저자 · 졸업생','alumni')]}
]
def student_stories():
 out='<section class="section student-section" aria-labelledby="student-heading"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">People behind the papers · 연구를 만든 사람들</span><h2 id="student-heading" lang="ko">질문이 연구가 되고,<br>연구가 논문이 됩니다.</h2></div><p lang="ko">학생과 졸업생이 함께 만든 연구 성과를 만나보세요.</p></div><div class="student-stories">'
 for item in STUDENT_STORIES:
  paper=story_paper(item['doi']); authors=paper['authors'].split(',')
  out+=f'<article class="student-story"><span class="story-topic">{e(item["topic"])}</span><h3 lang="ko">{e(item["question"])}</h3><p class="story-summary" lang="ko">{e(item["summary"])}</p><div class="story-researchers">'
  for name,initial,role,group in item['people']:
   person=next(m for m in D['alumni' if group=='alumni' else 'members'] if m['name']==name)
   assert any(initial in author for author in authors), 'Author mapping must match paper'
   route='/people/alumni/' if group=='alumni' else '/people/'
   out+=f'<a class="story-researcher" href="{route}#{profile_id(name)}">'+img(person['image'],name)+f'<span><strong>{e(name)}</strong><small lang="ko">{e(role)}</small></span></a>'
  out+='</div><div class="story-paper"><span class="story-citation">'+e(paper['citation'])+'</span><p class="story-paper-title" lang="en">'+e(paper['title'])+'</p>'+journal_metrics(dict(paper,year='2026'))+cta(paper['url'],'논문 보기 · Read paper','story-paper-link')+'</div></article>'
 return out+'</div></div></section>'
RESEARCH_INTERESTS=[
 ('make','01 / MAKE','배터리 핵심 소재를 직접 만들고 싶다','Design and synthesize core battery materials','저가형 고성능 양극부터 전고체전지용 고체전해질까지','조성과 합성 조건을 바꾸고, 결정구조와 배터리 성능을 비교하면서 새로운 소재를 설계합니다.','소재 설계 · 합성 · 전기화학 평가','research-drx-transport.png','리튬 이동 경로를 분석한 연구 그림','10.1021/acsnano.5c22044','/research/#cathodes'),
 ('understand','02 / UNDERSTAND','AI와 시뮬레이션으로 원리를 알고 싶다','Explore mechanisms with AI and simulations','AI와 시뮬레이션으로 배터리를 이해하기','제일원리계산과 시뮬레이션을 통해 구조 안정성, 전자구조, 이온 이동을 살펴보고 실험 결과와 연결합니다.','제일원리계산 · 구조·이온 이동 시뮬레이션 · 전자구조','research-sodium-redox.png','소듐 양극의 전자구조와 산소 전하밀도 연구 그림','10.1016/j.ensm.2026.105375','/research/#beyond-lithium'),
 ('improve','03 / IMPROVE','배터리 성능을 높이고 싶다','Improve battery performance','더 빠른 충전, 더 오래가는 배터리를 향해','전극과 계면을 설계하고 충·방전 특성과 구조 변화를 분석합니다. 고속충전 성능과 수명, 전고체전지의 계면 안정성을 함께 살펴봅니다.','전극 설계 · 계면 제어 · 성능·열화 분석','research-solid-interface.png','접착력 강화 코팅의 전고체전지 성능 비교 연구 그림','10.1016/j.ensm.2026.105167','/research/#solid-electrolytes')
]
def research_credits(paper):
 item=next((item for item in STUDENT_STORIES if item['doi']==paper.get('doi')),None)
 if not item:return ''
 out='<div class="story-researchers case-researchers">'
 for name,initial,role,group in item['people']:
  person=next(m for m in D['alumni' if group=='alumni' else 'members'] if m['name']==name)
  assert any(initial in author for author in paper['authors'].split(',')), 'Author mapping must match paper'
  route='/people/alumni/' if group=='alumni' else '/people/'
  out+=f'<a class="story-researcher" href="{route}#{profile_id(name)}">'+img(person['image'],name)+f'<span><strong>{e(name)}</strong><small lang="ko">{e(role)}</small></span></a>'
 return out+'</div>'

def materials_design_example():
 paper=story_paper('10.1021/acsnano.5c22044')
 return '<article class="material-case" aria-labelledby="material-case-acs-heading"><span class="material-case-label">Li-ion cathodes · 리튬이온전지 양극 설계 · ACS Nano (2026)</span><h4 id="material-case-acs-heading" lang="ko">양이온 배열을 바꿔 리튬 이동 경로를 설계하다</h4><p lang="ko">Ti를 도입해 양이온 간 크기와 전하 차이를 조절하고, 리튬 이동을 방해하는 국소 규칙 배열을 억제했습니다. 리튬이 갇히는 현상을 줄여 고용량과 출력 특성을 개선한 리튬 과잉 무질서 암염 양극 설계입니다.</p><p class="material-case-result" lang="ko">약 327 mAh g⁻¹ · 활물질 기준 에너지밀도 약 1,026 Wh kg⁻¹</p><p class="material-case-title" lang="en">'+e(paper['title'])+'</p><p class="material-case-citation">'+e(paper['citation'])+'</p>'+research_credits(paper)+cta(paper['url'],'ACS Nano 논문 보기','material-case-link')+'</article>'
def sodium_materials_design_example():
 paper=next(p for p in D['publication_archive']['2021'] if p.get('doi')=='10.1039/d0ee02803g')
 return '<article class="material-case" aria-labelledby="material-case-na-heading"><span class="material-case-label">Na-ion cathodes · 최초 양극 설계 · Energy &amp; Environmental Science (2021)</span><h4 id="material-case-na-heading" lang="ko">Na₂Fe₂F₇: 높은 성능과 낮은 가격을 함께 설계하다</h4><p lang="ko">연구실이 최초로 설계·검증한 소듐이온전지용 Na₂Fe₂F₇ 양극입니다. 층상형 양극의 높은 용량과 빠른 이온 이동, Fe계 polyanion 양극의 저렴한 원소 조성과 견고한 구조라는 장점을 하나의 설계에 결합했습니다. 3차원 Na⁺ 이동 경로와 작은 구조 변화를 제일원리계산·실험으로 검증해, 높은 용량·출력과 장수명을 경제적인 Fe 기반 조성에서 함께 구현했습니다.</p><p class="material-case-result" lang="ko">C/20에서 약 184 mAh g⁻¹ · 2C에서 1,000회 충·방전 후 약 88% 용량 유지</p><p class="material-case-title" lang="en">'+e(paper['title'])+'</p><p class="material-case-citation">'+e(paper['citation'])+'</p>'+research_credits(paper)+cta(paper['url'],'Na₂Fe₂F₇ 논문 보기','material-case-link')+'</article>'
def sodium_simulation_example():
 paper=story_paper('10.1016/j.ensm.2026.105375')
 return '<article class="material-case" aria-labelledby="simulation-na-heading"><span class="material-case-label">Na-ion cathodes · 소듐이온전지 · 제일원리 시뮬레이션 · Energy Storage Materials (2026)</span><h4 id="simulation-na-heading" lang="ko">전자구조로 이해하는 소듐 양극의 산소 산화환원</h4><p lang="ko">전자구조와 산소 전하밀도를 계산해 Mg 도입에 따라 산소 산화환원 반응이 어떻게 활성화되는지 살펴봤습니다. 계산 결과를 X선 흡수 분광과 작동 중 구조 분석에 연결해, 초기 소듐 추출과 구조 안정성이 함께 개선되는 원리를 규명했습니다.</p><p class="material-case-title" lang="en">'+e(paper['title'])+'</p><p class="material-case-citation">'+e(paper['citation'])+'</p>'+research_credits(paper)+cta(paper['url'],'소듐 양극 논문 보기','material-case-link')+'</article>'
def lithium_simulation_example():
 paper=story_paper('10.1002/aenm.202505121')
 return '<article class="material-case" aria-labelledby="simulation-li-heading"><span class="material-case-label">Li-ion cathodes · Co-free · Ni-minimized · Advanced Energy Materials (2026)</span><h4 id="simulation-li-heading" lang="ko">초기 활성화와 TM 이동 억제로 초저가·고성능 양극을 구현하다</h4><p lang="ko">Co를 배제하고 Ni 함량을 최소화한 Li·Mn-rich 양극에서, 초기 충전의 고전압 활성화(activation)로 산소 산화환원 반응을 활성화해 용량을 회복했습니다. 동시에 Mg 도입으로 전이금속 이동(TM migration)과 구조 무질서화를 억제했습니다. 제일원리계산·작동 중 구조 분석·전기화학 평가를 연결해, 저가 원소 중심의 조성에서 높은 에너지밀도와 안정적인 수명을 함께 구현했습니다.</p><p class="material-case-result" lang="ko">Co-free Ni 0.1 mol 초저가 LMR · 약 276.6 mAh g⁻¹ · 약 902.2 Wh kg⁻¹(활물질 기준) · 100회 후 93.4% 용량 유지</p><p class="material-case-title" lang="en">'+e(paper['title'])+'</p><p class="material-case-citation">'+e(paper['citation'])+'</p>'+research_credits(paper)+cta(paper['url'],'AEM 논문 보기','material-case-link')+'</article>'
def modeling_development(surface):
 heading_id='modeling-development-'+surface
 heading_tag='h4' if surface=='home' else 'h3'
 out=f'<aside class="modeling-development modeling-development-{surface}" aria-labelledby="{heading_id}"><{heading_tag} id="{heading_id}" lang="ko">AI로 찾는 안정한 원자 배열</{heading_tag}><p lang="ko">AI가 계산 데이터를 학습해, 수많은 원자 배열 중 가장 안정한 구조를 빠르게 찾아냅니다.</p>'
 if surface=='research':
  out+='<small class="modeling-method-note" lang="en">Cluster expansion (CASM) trained on first-principles data</small>'
 if surface=='join':
  out+='<p class="modeling-development-en" lang="en">AI learns from computational data to rapidly identify stable atomic arrangements.</p>'
 return out+'</aside>'
def performance_example():
 paper=story_paper('10.1016/j.ensm.2026.105167')
 return '<article class="material-case" aria-labelledby="performance-heading"><span class="material-case-label">All-solid-state batteries · 전고체전지 · Energy Storage Materials (2026)</span><h4 id="performance-heading" lang="ko">계면 접착력을 높여 출력과 수명을 개선하다</h4><p lang="ko">양극에 잘 붙는 코팅을 설계해 양극–고체전해질 계면을 안정화했습니다. NCM811 기반 전고체전지에서 Li 이동과 전극 접촉을 개선하고, 빠른 방전과 반복 충·방전 성능으로 설계 효과를 검증했습니다.</p><div class="case-metrics"><p><strong>73.4%</strong><span>2C 용량 / 0.1C 용량</span></p><p><strong>81.0%</strong><span>0.5C에서 100회 후 용량 유지율</span></p></div><p class="material-case-title" lang="en">'+e(paper['title'])+'</p><p class="material-case-citation">'+e(paper['citation'])+'</p>'+research_credits(paper)+cta(paper['url'],'전고체전지 코팅 논문 보기','material-case-link')+'</article>'

def case_figure(filename,alt,citation,doi):
 return '<figure class="case-figure"><a href="/assets/'+e(filename)+'" target="_blank" rel="noopener noreferrer" aria-label="'+e(alt)+' 크게 보기">'+img('/assets/'+filename,alt)+'</a><figcaption><span lang="ko">'+e(alt)+'</span><a href="https://doi.org/'+e(doi)+'" target="_blank" rel="noopener noreferrer">'+e(citation)+'</a></figcaption></figure>'

def additional_case(case,filename,alt,citation,doi,extra=''):
 return '<div class="additional-material-case"><div class="additional-case-grid">'+case+case_figure(filename,alt,citation,doi)+'</div>'+extra+'</div>'

def lmfp_performance_example():
 paper=story_paper('10.1002/aenm.202506130')
 return '<article class="material-case" aria-labelledby="performance-lmfp-heading"><span class="material-case-label">Li-ion cathodes · LMFP · LiF-less CEI · Advanced Energy Materials (2026)</span><h4 id="performance-lmfp-heading" lang="ko">LiF-less CEI로 고로딩 LMFP의 고속충전 성능을 높이다</h4><p lang="ko">고로딩 Mn-rich LMFP에서 빠른 충전을 제한하는 주요 원인이 계면의 전하 전달 저항임을 규명했습니다. LiF-less CEI 설계로 절연성 LiF의 축적을 줄여 Li⁺ 이동과 전하 전달을 개선하고, 높은 활물질 로딩에서도 고속충전 성능과 수명을 높였습니다.</p><p class="material-case-result" lang="ko">약 23 mg cm⁻² 로딩 · 5C 충전 시 용량 1.6배 · 2C에서 100회 후 약 87% 용량 유지</p><p class="material-case-title" lang="en">'+e(paper['title'])+'</p><p class="material-case-citation">'+e(paper['citation'])+'</p>'+research_credits(paper)+cta(paper['url'],'LMFP LiF-less CEI 논문 보기','material-case-link')+'</article>'

def research_explorer():
 out='<section class="section research-explorer" id="find-your-research" aria-labelledby="explorer-heading"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">Find your question · 관심에서 시작하는 연구</span><h2 id="explorer-heading" lang="ko">어떤 배터리 연구가<br>궁금한가요?</h2></div><p lang="ko">관심 있는 분야를 눌러 ESRL의 연구와 논문을 살펴보세요.</p></div><div class="research-choices">'
 for key,num,label,en,heading,desc,methods,image,alt,doi,route in RESEARCH_INTERESTS:
  paper=story_paper(doi)
  out+=f'<details class="research-choice" name="research-interest" id="interest-{key}"'+(' open' if key=='make' else '')+f'><summary><span class="choice-number">{num}</span><span class="choice-label"><strong lang="ko">{label}</strong><small lang="en">{en}</small></span><span class="choice-toggle" aria-hidden="true">+</span></summary><div class="choice-content"><div class="choice-copy"><h3 lang="ko">{heading}</h3><p lang="ko">{desc}</p><p class="choice-methods" lang="ko">{methods}</p>'+ (materials_design_example() if key=='make' else sodium_simulation_example() if key=='understand' else performance_example()) +'<div class="choice-links">'+cta(route,'관련 연구 보기','button dark')+(cta(paper['url'],'연결된 논문 보기','text-link') if key not in ('make','understand','improve') else '')+'</div></div><figure>'+img('/assets/'+image,alt)+f'<figcaption>'+('양이온 배열 제어에 따른 리튬 이동 경로 분석 · ' if key=='make' else '소듐 양극의 전자구조·산소 전하밀도 분석 · ' if key=='understand' else '')+e(paper["citation"])+'</figcaption></figure></div>'+(additional_case(sodium_materials_design_example(),'research-na2fe2f7-design.webp','Na₂Fe₂F₇의 3차원 구조와 Na⁺ 이동 경로','Energy & Environmental Science, 14, 1469–1479 (2021) · Fig. 1','10.1039/d0ee02803g') if key=='make' else additional_case(lithium_simulation_example(),'research-co-free-ni-minimized-lmr.webp','Co-free Ni 0.1 mol LMR의 전이금속 이동 억제와 구조 안정화','Advanced Energy Materials, 16, e05121 (2026) · Fig. 4a','10.1002/aenm.202505121',modeling_development('home')) if key=='understand' else additional_case(lmfp_performance_example(),'research-lmfp-lif-less-cei.webp','고로딩 LMFP의 LiF-less CEI 설계와 계면 Li⁺ 이동 개선','Advanced Energy Materials, 16, e06130 (2026) · Fig. 5','10.1002/aenm.202506130'))+'</details>'
 return out+'</div></div></section>'

RESEARCH_SUPPORT=[
 ('01','Full tuition support','대학원생 등록금 전액 지원','대학원생의 등록금 전액을 지원하여 연구와 학업에 집중할 수 있도록 돕습니다.','Full tuition support for graduate students.'),
 ('02','Research stipends','대학원생 인건비 지원','대학원생에게 연구 참여 인건비를 지원합니다. 학부연구생(인턴)에게도 재정 지원을 제공합니다.','Research stipends for graduate students, with financial support also available to undergraduate interns.'),
 ('03','Academic conferences','국내·국제 학회 참여','학회에서 연구 성과를 발표하고, 다양한 분야의 연구자들과 교류할 기회를 제공합니다.','Opportunities to present research and connect with researchers at domestic and international conferences.'),
 ('04','Battery industry collaboration','배터리 기업과의 산학 공동연구 참여','배터리 기업과의 공동연구에 참여하며, 소재 연구가 실제 배터리 기술로 이어지는 과정을 경험할 기회를 제공합니다.','Opportunities to participate in collaborative research with battery companies and explore practical battery challenges.')
]
def support_section():
 out='<section class="section support-section" aria-labelledby="support-heading"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">Research support · 연구 지원</span><h2 id="support-heading" lang="ko">연구에 몰입할 수 있도록.</h2><p class="support-heading-en" lang="en">Support for your next discovery.</p></div><p lang="ko">소재에 대한 호기심이 연구 성과로 이어질 수 있도록 지원합니다.</p></div><div class="support-grid">'
 for num,en,ko,desc,en_desc in RESEARCH_SUPPORT:
  out+=f'<article class="support-card"><span class="support-number">{num}</span><span class="support-label" lang="en">{en}</span><h3 lang="ko">{ko}</h3><p lang="ko">{desc}</p><p class="support-description-en" lang="en">{en_desc}</p></article>'
 return out+'</div></div></section>'

def research_impact(surface):
 count=SCHOLAR_METRICS['publications']
 out=f'<section class="research-impact research-impact-{surface}" aria-label="Research impact · 연구 성과"><div class="wrap"><div class="impact-grid"><a href="{SCHOLAR}" target="_blank" rel="noopener noreferrer"><strong>{count:,}</strong><span>논문 총수 · Publications</span></a><a href="{SCHOLAR}" target="_blank" rel="noopener noreferrer"><strong>{SCHOLAR_METRICS["citations"]:,}</strong><span>총인용수 · Citations</span></a><a href="{SCHOLAR}" target="_blank" rel="noopener noreferrer"><strong>{SCHOLAR_METRICS["h_index"]}</strong><span>h-index · Google Scholar</span></a></div><p class="metrics-date">Google Scholar 전체 지표 · 확인일: {e(SCHOLAR_METRICS["checked_at"])}</p>'
 if surface in ('home','join'):out+='<p class="alumni-careers" lang="ko">졸업생 주요 진로: LG에너지솔루션, 삼성SDI</p>'
 return out+'</div></section>'

def application_section():
 return '<section class="section application-section"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">How to apply · 지원 안내</span><h2 lang="ko">관심에서 첫 만남까지.</h2></div></div><div class="beginner-note"><strong lang="ko">실험에서 AI·계산까지, 배터리 소재를 이해하는 연구 역량을 넓혀갑니다.</strong><p lang="ko">AI·계산 분야에 새롭게 도전하는 학생도 환영합니다. 기초부터 실제 소재 설계까지 연결하며 연구 역량을 쌓아갑니다.</p><p lang="en">Build your research capabilities across experiments, AI, and computation. Students new to AI and computational research are welcome to develop their skills from the fundamentals to materials design.</p></div><div class="application-grid"><article><h3>지원 서류 · Documents</h3><p lang="ko">간단한 이력서(CV), 성적증명서, 관심 연구주제와 희망 시작 시기를 이메일로 보내 주세요. 박사후연구원은 연구 경력 및 주요 논문 목록을 함께 보내 주세요.</p><p lang="en">Email your CV, transcript, research interests, and preferred start date. Postdoctoral applicants should also include their research experience and publication list.</p></article><article><h3>지원 시기 · Timing</h3><p lang="ko">연구실 사전 문의는 상시 가능합니다. 대학원 진학 희망자는 성균관대학교 공식 모집 일정에 앞서 연락해 주세요. 학부연구생·박사후연구원의 시작 시기는 면담 후 협의합니다.</p><p lang="en">Lab inquiries are welcome throughout the year. Prospective graduate students should contact us before the official university application period. Start dates for undergraduate researchers and postdoctoral researchers are discussed individually.</p></article></div><ol class="application-steps"><li><strong>이메일 문의</strong><span>지원 서류와 관심 분야 전달</span></li><li><strong>서류 검토</strong><span>연구 관심과 참여 가능 시기 확인</span></li><li><strong>면담</strong><span>연구 방향·참여 과정 논의</span></li><li><strong>지원·합류</strong><span>대학원은 공식 입학 전형, 인턴·포닥은 개별 협의</span></li></ol></div></section>'

def publication_year(p):
 return int(p.get('year') or re.search(r'(20\d{2})',p['citation'])[1])

def featured_impact(p):
 journal=JOURNAL_METRICS['journals'].get(journal_key(p['citation'].split(',')[0]),{})
 year=publication_year(p)-1
 return float(journal.get('years',{}).get(str(year),{}).get('impact_factor') or 0)

def is_last_corresponding_author(p):
 last=p.get('authors','').split(',')[-1].strip()
 name=re.sub(r'[\s.†‡*]+','',last).casefold()
 return '*' in last and name in ('jkim','jongsoonkim')

def featured_publications(papers,year):
 eligible=[]
 seen=set()
 for p in papers:
  key=p.get('doi') or p['title'].casefold()
  if key in seen or not is_last_corresponding_author(p) or featured_impact(p)<=0:continue
  seen.add(key)
  eligible.append(p)
 current=sorted((p for p in eligible if publication_year(p)==year),key=featured_impact,reverse=True)[:3]
 previous=sorted((p for p in eligible if publication_year(p)==year-1),key=featured_impact,reverse=True)
 return current+previous[:3-len(current)]

from datetime import datetime
from zoneinfo import ZoneInfo
CURRENT_YEAR=datetime.now(ZoneInfo('Asia/Seoul')).year
available_papers=D['publications']+[dict(p,year=p.get('year',year)) for year,papers in D['publication_archive'].items() for p in papers]
selected=featured_publications(available_papers,CURRENT_YEAR)
selected_years=' · '.join(dict.fromkeys(str(publication_year(p)) for p in selected)) or str(CURRENT_YEAR)
home=f'''<section class="hero"><div class="wrap hero-inner"><div class="hero-copy"><span class="eyebrow">Materials × Computation × Energy</span><h1 class="student-hero-title" lang="ko">배터리의 다음 질문,<br><span>우리가 함께 풀어갑니다.</span></h1><p class="hero-question-en" lang="en">Together, we tackle the next questions in batteries.</p><p class="hero-ko" lang="ko">소재를 만들고, 원리를 밝히고,<br>미래의 배터리를 함께 설계합니다.</p><p class="hero-desc hero-intro-ko" lang="ko">리튬·소듐이온전지용 저가형 고성능 양극과 전고체전지용 고체전해질. 제일원리계산·합성·실험을 연결해 배터리의 성능과 안정성을 높이는 소재 및 전극을 설계합니다.</p><p class="hero-desc hero-intro-en" lang="en">Cost-effective cathodes for Li- and Na-ion batteries, and solid electrolytes for all-solid-state batteries — connecting materials design, calculations, and experiments.</p><div class="hero-actions">{cta('#find-your-research','<span lang="ko">우리 연구 둘러보기</span>','button')}{cta('/join/','<span lang="ko">연구실 지원 안내</span>','text-link')}</div><a class="hero-recruit" href="/join/"><span class="hero-recruit-content"><span class="hero-recruit-title"><span lang="ko">모집 안내</span><span lang="en">Join ESRL</span></span><span class="hero-recruit-audience" lang="ko">학부연구생 · 대학원생 · 포닥 모집</span><span class="hero-recruit-audience-en" lang="en">Undergraduate · Graduate · Postdoctoral opportunities</span></span><span class="hero-recruit-arrow" aria-hidden="true">↗</span></a></div><div class="hero-visual">{img('/assets/ai-battery-ev-wide.png','Conceptual illustration connecting computation servers, atomic battery materials, rechargeable cells and an electric vehicle',eager=True)}<div class="visual-caption"><span>ENERGY STORAGE RESEARCH LAB<br><span lang="ko">성균관대학교 에너지 저장 연구실</span></span><span>Cathodes × Solid electrolytes<br><span lang="ko">소재·계산·실험으로 연결하는 연구</span></span></div></div></div></section>
 <section class="join-section" id="recruitment" aria-labelledby="recruitment-heading"><div class="wrap join-inner"><div><span class="eyebrow">Join ESRL <span lang="ko">· 함께할 연구자를 찾습니다</span></span><h2 id="recruitment-heading">Let’s ask the next question.</h2><p lang="ko"><strong>학부연구생 · 대학원생 · 박사후연구원(포닥)을 모집합니다.</strong><br>양극·고체전해질 설계, 제일원리계산, 실험·분석을 통해 차세대 이차전지 연구에 함께할 분들의 문의를 환영합니다.</p><p class="join-en" lang="en"><strong>We are recruiting undergraduate researchers, graduate students, and postdoctoral researchers.</strong><br>Explore next-generation rechargeable batteries with us through cathode and solid-electrolyte design, first-principles calculations, and experimental research.</p><div class="recruit-support" aria-label="Graduate student support"><span class="recruit-support-label" lang="ko">대학원생 연구 지원</span><div class="recruit-support-items"><span><strong lang="ko">등록금 전액 지원</strong><small lang="en">Full tuition support</small></span><span><strong lang="ko">인건비 지원</strong><small lang="en">Research stipends</small></span></div><p class="recruit-support-more" lang="ko">국내·국제 학회 참여 · 산학 공동연구 기회</p></div></div>{link('/join/','<span><span lang="ko">모집 안내</span><small lang="en">Recruitment details</small></span>','button dark join-section-cta')}</div></section>
 <div class="research-strip"><div class="wrap strip-inner"><div class="strip-item"><b class="strip-number">01</b><div><strong>Materials design</strong><br><span lang="ko">전극 소재 설계·합성</span></div></div><div class="strip-item"><b class="strip-number">02</b><div><strong>Computation & simulations</strong><br><span lang="ko">제일원리계산 · 구조·이온 이동 시뮬레이션</span></div></div><div class="strip-item"><b class="strip-number">03</b><div><strong>Advanced characterization</strong><br><span lang="ko">구조·반응 메커니즘 규명</span></div></div></div></div>
 <section class="section"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">Our research <span lang="ko">· 연구 분야</span></span><h2>Two materials pillars<br>One connected approach</h2></div><p lang="ko">양극과 고체전해질에 대한 소재 전문성을 바탕으로, 제일원리계산·합성·고도분석을 하나의 연구 흐름으로 연결합니다.</p></div><div class="research-grid core-grid">{cards}</div><div class="core-connection"><span>Materials design</span><b aria-hidden="true">↔</b><span>First-principles insight</span><b aria-hidden="true">↔</b><span>Synthesis &amp; validation</span></div></div></section>
 <section class="section paper-section"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">Selected publications <span lang="ko">· 주요 논문</span> · {selected_years}</span><h2>Ideas into evidence.</h2></div>{link('/publications/','<span lang="ko">전체 논문 보기</span>')}</div>{''.join(paper(p,False) for p in selected)}</div></section>
 <section class="section"><div class="wrap people-feature"><div>{img('/assets/esrl-group-samsung-library-wide.png','ESRL group photograph in front of Samsung Library at Sungkyunkwan University')}<p class="photo-credit">ESRL at Sungkyunkwan University · Samsung Library</p></div><div><span class="eyebrow">Our people <span lang="ko">· 연구실 구성원</span></span><h2>Different perspectives.<br>A shared curiosity.</h2><p lang="ko">성균관대학교 김종순 교수의 에너지 저장 연구실은 서로 다른 전문성을 가진 연구자들이 함께 소재 설계, 계산, 실험을 연결하며 이차전지 소재의 가능성을 넓혀갑니다.</p><div class="hero-actions">{link('/people/','<span lang="ko">구성원 소개</span>')}{link('/life/','<span lang="ko">연구실 일상</span>')}</div></div></div></section>
'''
recruitment=re.search(r' <section class="join-section".*?</section>',home,re.S)[0]
home=home.replace(recruitment,'')
insert_at=home.index(' <section class="section">')
home=re.sub(r'<a class="hero-recruit".*?</a>','',home,flags=re.S)
insert_at=home.index(' <section class="section">')
home=home[:insert_at]+research_impact('home')+research_explorer()+recruitment+home[insert_at:]
save('/','Energy Storage Research Lab',home)

def research_paper(doi):
 papers=D['publications']+[p for archive in D['publication_archive'].values() for p in archive]
 p=next(p for p in papers if p.get('doi')==doi)
 return dict(p,year=str(p.get('year') or re.search(r'(20\d{2})',p['citation'])[1]))

RESEARCH_CASES={
 'lmfp':('10.1002/aenm.202506130','고로딩 Mn-rich 양극의 고속충전을 계면 설계로 개선하다','Mn-rich LMFP 전극에서 빠른 충전을 제한하는 전하 전달 저항을 분석했습니다. CEI의 LiF 형성을 줄여 계면 반응을 개선하고, 높은 활물질 로딩에서도 고속충전 성능과 수명을 높였습니다.','약 23 mg cm⁻² 로딩 · 5C 용량 1.6배 · 2C에서 100회 후 약 87% 용량 유지'),
 'fe-migration':('10.1021/acsenergylett.6c02530','Fe 이동을 억제해 소듐 양극의 고전압 구조를 안정화하다','Fe 산화에 따른 국소 구조 왜곡이 Fe의 소듐층 이동과 비가역 구조 변화로 이어지는 경로를 규명했습니다. Fe 함량과 금속–산소 골격, 원자 이동 경로를 함께 설계하여 고전압 작동 안정성을 개선했습니다.','177.96 mAh g⁻¹ · 초기 쿨롱 효율 94.1%'),
 'bimodal':('10.1021/acsenergylett.5c03923','입자 크기를 조합해 전고체 복합양극의 이온 이동과 응력 분산을 개선하다','큰 다결정 입자와 작은 단결정 입자를 조합한 복합양극에서 충전 밀도와 공극 구조를 제어했습니다. 이온 이동 경로와 응력 분산을 분석하여 활물질 비율이 높은 전극의 출력과 반복 충·방전 안정성을 개선한 공동연구입니다.','활물질 90 wt% · 0.5C에서 200회 후 87.8% 용량 유지')
}
def additional_research_case(key):
 doi,heading,summary,result=RESEARCH_CASES[key]
 p=research_paper(doi)
 return f'<article class="material-case" aria-labelledby="research-case-{key}"><span class="material-case-label">{e(p["citation"].split(",")[0])} · {p["year"]}</span><h4 id="research-case-{key}" lang="ko">{e(heading)}</h4><p lang="ko">{e(summary)}</p><p class="material-case-result" lang="ko">{e(result)}</p><p class="material-case-title" lang="en">{e(p["title"])}</p><p class="material-case-citation">{e(p["citation"])}</p>'+research_credits(p)+cta(p['url'],'논문 보기 · Read paper','material-case-link')+'</article>'

def research_publications(section):
 cases={
  '01':[(materials_design_example(),'10.1021/acsnano.5c22044'),(lithium_simulation_example(),'10.1002/aenm.202505121'),(lmfp_performance_example(),'10.1002/aenm.202506130')],
  '02':[(sodium_simulation_example(),'10.1016/j.ensm.2026.105375'),(sodium_materials_design_example(),'10.1039/d0ee02803g'),(additional_research_case('fe-migration'),'10.1021/acsenergylett.6c02530')],
  '03':[(performance_example(),'10.1016/j.ensm.2026.105167'),(additional_research_case('bimodal'),'10.1021/acsenergylett.5c03923')]
 }[section]
 out=f'<div class="research-paper-section" aria-labelledby="research-papers-{section}"><h3 id="research-papers-{section}">Selected studies <span lang="ko">· 대표 연구 논문</span></h3><div class="research-paper-grid">'
 for case,doi in cases:
  p=research_paper(doi)
  case=case.replace('class="material-case"','class="material-case research-paper-card"',1)
  case=case.replace(e(p['title']),publication_title(p),1)
  links=f'<div class="research-paper-files">{link(p["pdf_url"],"PDF",external=True)}</div>' if p.get('pdf_url') else ''
  case=case.removesuffix('</article>')+journal_metrics(p)+links+'</article>'
  out+=case
 return out+'</div></div>'

details=[('01','Li','Cathodes for lithium-ion batteries','Electrode materials that connect energy, power, and durability.','We study layered oxides, olivine-type cathodes, and disordered rocksalt materials. Our research connects composition and crystal structure with redox behavior, ion transport, and electrochemical performance.'),('02','Na / K','Cathodes beyond lithium','Alternative chemistries for a wider range of energy-storage needs.','We investigate sodium- and potassium-ion electrode materials and aqueous zinc systems. Materials design and mechanistic analysis guide our work on reversible reactions, structural stability, and ion transport.'),('03','SSE','Solid electrolytes & interfaces','Connecting ion transport, electrolyte stability, and cathode compatibility.','We study solid electrolytes and their compatibility with cathode materials, connecting ion transport and electrolyte stability with interfacial reactions. Experiments and calculations guide electrolyte design, cathode coatings, and interface control for all-solid-state batteries.')]
body=title('Our expertise · 핵심 연구','Cathodes, solid electrolytes<br>and the interface between','양극과 고체전해질의 설계·합성·반응 메커니즘을 연구하고, 계산·합성·실험을 연결하여 소재와 계면을 함께 이해합니다.')+'<section class="section research-pillars"><div class="wrap research-grid core-grid">'+cards+'</div></section>'
research_visuals={
 '01':('research-drx-transport.png','STEM-HAADF intensity maps and lithium transport pathways in Li-excess disordered rocksalt cathodes','양이온 배열 제어를 통한 Li 이동 경로 개선','J. Ahn et al. · ACS Nano 20, 10556–10569 (2026) · Fig. 2i–j','https://doi.org/10.1021/acsnano.5c22044'),
 '02':('research-sodium-redox.png','Calculated electronic density of states and oxygen charge densities in sodium layered cathodes','전자구조·산소 산화환원 반응을 활용한 소듐 양극 설계','S. Lim et al. · Energy Storage Materials 90, 105375 (2026) · Fig. 2c–e','https://doi.org/10.1016/j.ensm.2026.105375'),
 '03':('research-solid-interface.png','Comparison of cathode-adhesion-enhanced and conventional coatings in sulfide-based all-solid-state batteries','접착력 강화 코팅을 통한 전극–고체전해질 계면 안정화','J. Kim et al. · Energy Storage Materials 89, 105167 (2026) · Fig. 6','https://doi.org/10.1016/j.ensm.2026.105167')
}
body+='<section class="section research-illustrated"><div class="wrap">'+''.join(f'<article class="research-detail illustrated" id="{n}"><span id="{dict({'01':'cathodes','02':'beyond-lithium','03':'solid-electrolytes'})[n]}" class="section-anchor" aria-hidden="true"></span><figure class="research-figure paper-figure"><a class="figure-zoom" href="/assets/{research_visuals[n][0]}" target="_blank" rel="noopener noreferrer" aria-label="Open full-size research figure: {research_visuals[n][1]}">'+img('/assets/'+research_visuals[n][0],research_visuals[n][1])+f'<span class="figure-zoom-label">View full size · 크게 보기</span></a><figcaption><strong lang="ko">{research_visuals[n][2]}</strong><a class="figure-source" href="{research_visuals[n][4]}" target="_blank" rel="noopener noreferrer">{research_visuals[n][3]}</a></figcaption></figure><div class="research-explanation"><span class="eyebrow">Research {n} / {s}</span><h2>{h}<small>{short}</small></h2><p>{p}</p><p class="research-summary-ko" lang="ko">{research_visuals[n][2]}</p></div>'+research_publications(n)+'</article>' for n,s,h,short,p in details)+'</div></section>'
body+='''<section class="section paper-section"><div class="wrap"><span class="eyebrow">How we work</span><h2>Learn. Design. Understand.</h2><figure class="research-flow" aria-label="Connected research approach: first-principles calculations, materials design, and experimental validation"><img class="research-flow-art" width="1942" height="809" src="/assets/research-ai-servers-materials.png" alt="Conceptual illustration connecting computation servers and data networks with atomistic materials design and battery experiments" loading="lazy" decoding="async"><div class="flow-nodes"><div><span class="flow-label">01 / PREDICT</span><strong>Computation &amp; simulations</strong><span lang="ko">제일원리계산 · 물리 기반 모델링</span></div><div><span class="flow-label">02 / DESIGN</span><strong>Materials design</strong><span lang="ko">소재 설계 · 합성</span></div><div><span class="flow-label">03 / UNDERSTAND</span><strong>Experiments &amp; analysis</strong><span lang="ko">전기화학 평가 · 구조 분석</span></div></div><figcaption lang="ko">예측과 설계, 실험과 분석을 연결하여 소재의 작동 원리를 이해합니다.<small>계산 · 소재 설계 · 실험을 연결하는 연구 접근법의 컨셉 이미지</small></figcaption></figure><div class="method-grid"><article><h3>Materials & electrochemistry</h3><p>Synthesis, electrode preparation, and electrochemical measurements connect a material’s structure with its battery behavior.</p></article><article><h3>First-principles calculations &amp; physics-based modeling</h3><p>First-principles calculations reveal structural stability, electronic structure, operating voltage, and ion-diffusion pathways. We connect these atomic-scale insights with synthesis and experimental validation.</p></article><article><h3>Advanced structural analysis</h3><p>X-ray and neutron methods, X-ray absorption spectroscopy, and electron microscopy reveal how materials change during battery operation.</p></article></div>'''+modeling_development('research')+'''<div class="hero-actions">'''+link('/equipment/','Equipment & facilities')+link('/publications/','Explore publications')+'</div></div></section>'
save('/research/','Research',body)

scholar='https://scholar.google.co.kr/citations?hl=en&user=bTPbWeIAAAAJ&view_op=list_works&sortby=pubdate'
body=title('Principal investigator','Jongsoon Kim','김종순 · Associate Professor with tenure · Sungkyunkwan University')
body+='<section class="section"><div class="wrap"><div class="professor-intro">'+img(D['professor'],'Professor Jongsoon Kim','professor-photo',True)+'''<div><span class="eyebrow">Energy Storage Research Lab</span><h2 class="professor-name">Jongsoon Kim, Ph.D.</h2><p class="professor-role">Associate Professor with tenure</p><div class="professor-info">Department of Energy<br>Department of Energy Science<br>Department of Future Energy Engineering<br>Sungkyunkwan University</div><p>Research interests include cathode materials and solid electrolytes for rechargeable batteries, first-principles calculations, and structural analysis using X-ray and neutron diffraction.</p><div class="professor-info"><a href="mailto:jongsoonkim@skku.edu">jongsoonkim@skku.edu</a><br>+82 31 299 6271<br>N-Center, Room 86679</div>'''+link(scholar,'Google Scholar',external=True)+'</div></div>'
def timeline(rows):return '<div class="timeline">'+''.join(f'<div class="timeline-item"><time>{year}</time><div><strong>{name}</strong><span>{place}</span></div></div>' for year,name,place in rows)+'</div>'
body+='<div class="career-grid"><section><h2>Appointments</h2>'+timeline([('2021–present','Associate Professor with tenure','Department of Energy Science & Department of Energy, SKKU'),('2023–present','Associate Professor','Department of Future Energy Engineering, SKKU'),('2022–present','Associate Professor','SKKU Institute of Energy Science and Technology'),('2017–2021','Assistant Professor','Sejong University'),('2014–2017','Senior Researcher','Neutron Science Research Center, Korea Atomic Energy Research Institute')])+'</section><section><h2>Education</h2>'+timeline([('2011–2014','Ph.D., Materials Science and Engineering','Seoul National University · Advisor: Prof. Kisuk Kang'),('2008–2011','M.S./Ph.D. program, Materials Science and Engineering','KAIST · Advisor: Prof. Kisuk Kang'),('2004–2008','B.S., Materials Science and Engineering','KAIST')])+'</section></div><div class="career-grid"><section><h2>Honors & awards</h2>'+timeline([('2025','DAEJOO Young Scientist Award','Korea Ceramic Society'),('2023','Rechargeable Battery Young Researcher Award','Korea Electrochemical Society'),('2022','Emerging Investigators','Journal of Materials Chemistry A'),('2020','Academic Advancement Award','Korea Ceramic Society'),('2014','Best Ph.D. Graduation Award','Department of Materials Science and Engineering, SNU')])+'</section><section><h2>Academic service</h2>'+timeline([('Current · 현재','한국전기화학회 총무위원','Korean Electrochemical Society'),('Current · 현재','한국전기화학회 이차전지분과 실무위원','Rechargeable Battery Division, Korean Electrochemical Society'),('Current · 현재','한국세라믹학회 학술운영이사','The Korean Ceramic Society'),('2026','이차전지 재료 심포지엄 Organizer','한국세라믹학회 추계학술대회'),('2026','국가 R&D 기획 · K-BIG Project 제1간사','이차전지 핵심 소재 R&D 기획'),('2022–present','Review board','Research Grants Council of Hong Kong')])+'</section></div></div></section>'
body+=research_impact('professor')
save('/professor/','Professor',body)

all_papers=[dict(p,year=str(p.get('year',re.search(r'(20\d{2})',p['citation'])[1]))) for p in D['publications']]+[dict(p,year=year) for year,papers in D['publication_archive'].items() for p in papers]
for label,years in [('All',None)]+PUBLICATION_GROUPS:
 route='/publications/' if label=='All' else pubroute(label)
 papers=all_papers if years is None else [p for p in all_papers if p['year'] in years]
 body=title('ESRL publications · 연구 성과','The science behind<br>better batteries','양극과 고체전해질, 소재의 발견에서 작동 원리의 이해까지 — ESRL의 연구 기록').replace('class="page-title"','class="page-title publication-title"')+publication_library(papers,label)
 save(route,'Publications'+('' if label=='All' else ' · '+label),body)

body=title('Our people','Curiosity is a team effort.','Meet the researchers exploring materials, mechanisms, and energy storage at ESRL.')
body+='<section class="section"><div class="wrap">'+people_tabs('current')+'<div class="section-heading"><h2>Current members</h2>'+link('/professor/','Prof. Jongsoon Kim')+'</div>'
for group in dict.fromkeys(m['group'] for m in D['members']):
 body+=f'<section class="member-group"><h2>{group}</h2><div class="members-grid">'
 for m in D['members']:
  if m['group']!=group:continue
  body+=f'<article class="member" id="{profile_id(m["name"])}">'+img(m['image'],m['name'])+f'<h3>{e(m["name"])}</h3><div class="course">{e(m["course"])}</div><p class="field">{e(m["field"])}</p>'+(f'<a class="member-email" href="mailto:{e(m["email"])}" aria-label="Email {e(m["name"])}">Email ↗</a>' if m['email'] else '')+'</article>'
 body+='</div></section>'
body+='</div></section>'
save('/people/','People',body)

body=title('Our people · Alumni','Once ESRL, always ESRL.','졸업 후에도 이어지는 연구와 인연 — meet our alumni and explore their next chapters.')
body+='<section class="section"><div class="wrap">'+people_tabs('alumni')
for degree,ko in [('Ph.D.','박사 졸업생'),('M.S.','석사 졸업생')]:
 body+=f'<section class="member-group"><h2>{degree} alumni <span class="alumni-degree-ko" lang="ko">{ko}</span></h2><div class="members-grid alumni-grid">'
 for m in D['alumni']:
  if m['degree']!=degree:continue
  portrait=img(m['image'],m['name']) if m.get('image') else '<div class="alumni-name-mark" aria-hidden="true">'+e(m['degree'])+'</div>'
  body+=f'<article class="member alumni-member" id="{profile_id(m["name"])}">'+portrait+f'<h3>{e(m["name"])}</h3>'+(f'<p class="alumni-name-ko" lang="ko">{e(m["name_ko"])}</p>' if m.get('name_ko') else '')+f'<div class="course">{e(m["degree"])} · {e(m["graduated"])}</div>'
  if m.get('organization'):body+=f'<p class="alumni-organization">{e(m["organization"])}</p>'
  if m.get('email'):body+=f'<a class="member-email" href="mailto:{e(m["email"])}" aria-label="Email {e(m["name"])}">Email ↗</a>'
  body+='</article>'
 body+='</div></section>'
body+='</div></section>'
save('/people/alumni/','Alumni',body)


body=title('Equipment & facilities','Built for discovery.','Our facilities support materials synthesis, battery assembly, electrochemical testing, and computational research.')
body+='<section class="section"><div class="wrap equipment-grid">'+''.join('<article class="equipment">'+img(q['image'],q['name'])+f'<h3>{e(q["name"])}</h3><p lang="ko">{e(q["description"])}</p></article>' for q in D['equipment'])+'</div></section>'
save('/equipment/','Equipment & facilities',body)

life_years=sorted({a['year'] for a in LAB_LIFE['albums']},reverse=True)
def life_tabs(active):
 choices=[('All','/life/','All albums · 전체')]+[(y,'/life/'+y+'/',y) for y in life_years]
 return '<nav class="year-nav life-years" aria-label="Lab life year">'+''.join(f'<a href="{url}"'+(' aria-current="page"' if key==active else '')+f'>{label}</a>' for key,url,label in choices)+'</nav>'
def album_route(album):return '/life/albums/'+album['slug']+'/'
def photo_count(album):return str(len(album['photos']))+(' photo' if len(album['photos'])==1 else ' photos')
for year in ['All',*life_years]:
 albums=[a for a in LAB_LIFE['albums'] if year=='All' or a['year']==year]
 body=title('Life at ESRL · 연구실 일상','Science brings us together.','함께 연구하고, 함께 성장하는 우리의 순간들.<br>Celebrations, shared meals, and moments beyond the lab.')
 body+='<section class="section life-archive"><div class="wrap">'+life_tabs(year)+f'<div class="life-overview"><p><strong>{len(albums)}</strong> albums · 행사 앨범</p><span>2022–2026 · ESRL memories</span></div><div class="album-grid">'
 for a in albums:
  body+=f'<article class="album-card"><a class="album-cover" href="{album_route(a)}">'+img(a['cover'],a['title_ko']+' · '+a['date_label'])+f'<span class="album-count">{photo_count(a)} <span aria-hidden="true">↗</span></span></a><div class="album-card-copy"><time>{e(a["date_label"])}</time><h2><a href="{album_route(a)}">{e(a["title_ko"])}</a></h2><p lang="en">{e(a["title"])}</p></div></article>'
 body+='</div></div></section>'
 save('/life/' if year=='All' else '/life/'+year+'/','Lab life'+('' if year=='All' else ' · '+year),body)
for a in LAB_LIFE['albums']:
 body=title('Life at ESRL · '+a['date_label'],e(a['title_ko']),e(a['title']))
 body+='<section class="section album-detail"><div class="wrap"><div class="album-toolbar">'+link('/life/'+a['year']+'/',a['year']+' 앨범 목록 · Back to albums')+f'<p>{photo_count(a)} · 사진을 누르면 크게 볼 수 있습니다.</p></div><div class="photo-grid album-photos">'
 for i,p in enumerate(a['photos'],1):
  caption=a['title_ko']+' · '+a['date_label']+f' · {i} / {len(a["photos"])}'
  body+=f'<figure class="photo-item"><a class="photo-open" href="{e(p["image"])}" data-lightbox data-caption="{e(caption)}" aria-label="{e(caption)} 크게 보기">'+img(p['image'],a['title_ko']+f' · Photo {i}')+f'<span class="photo-zoom" aria-hidden="true">크게 보기 ↗</span></a><figcaption><span>{i:02d}</span></figcaption></figure>'
 body+='''</div></div></section><dialog class="photo-dialog" aria-label="사진 크게 보기 · Photo viewer"><div class="photo-dialog-shell"><div class="photo-dialog-top"><p data-photo-caption aria-live="polite"></p><button type="button" data-photo-close aria-label="닫기 · Close">Close ×</button></div><div class="photo-dialog-stage"><button type="button" data-photo-prev aria-label="이전 사진 · Previous photo">‹</button><img data-photo-image alt=""><button type="button" data-photo-next aria-label="다음 사진 · Next photo">›</button></div><p class="photo-dialog-hint">← → Previous / Next · ESC Close</p></div></dialog>'''
 save(album_route(a),a['title_ko']+' · '+a['date_label'],body)

body=title('Join ESRL','Your next question<br>could start here.','We are recruiting undergraduate researchers, graduate students, and postdoctoral researchers interested in energy-storage materials.')
body+=research_impact('join')+support_section()+application_section()
body+='''<section class="section"><div class="wrap contact-grid"><div><span class="eyebrow">Research opportunities</span><h2>Connect experiments<br>with understanding.</h2><p class="recruit-highlight" lang="ko">학부연구생 · 대학원생 · 박사후연구원(포닥) 모집</p><p>Our group connects cathode and solid-electrolyte design, first-principles calculations, synthesis, and advanced characterization to understand materials and their behavior in rechargeable batteries.</p><p>Research opportunities span lithium-ion batteries, sodium- and potassium-ion batteries, aqueous zinc systems, and all-solid-state batteries.</p><p lang="ko">성균관대학교 에너지 저장 연구실에서 학부연구생, 대학원생 및 박사후연구원(포닥)을 모집합니다. 양극·고체전해질의 설계·합성, 제일원리계산 및 고도분석 연구에 관심 있는 분들은 김종순 교수에게 문의해 주시기 바랍니다.</p>'''+link('mailto:jongsoonkim@skku.edu','Contact Prof. Kim','button dark')+'''</div><aside class="contact-details"><span class="eyebrow">Get in touch</span><h3>Email</h3><p><a href="mailto:jongsoonkim@skku.edu">jongsoonkim@skku.edu</a></p><h3>Principal investigator</h3><p>Prof. Jongsoon Kim<br>김종순 교수</p><h3>Office</h3><p>N-Center, Room 86679<br>Sungkyunkwan University</p><h3>Telephone</h3><p><a href="tel:+82312996271">+82 31 299 6271</a></p></aside></div></section>'''
save('/join/','Join us',body)
(DIST/'404.html').write_text(shell('Page not found','', '<section class="not-found"><span class="eyebrow">404</span><h1>Page not found.</h1><p>Let’s get you back to the lab.</p>'+link('/','Back to home','button dark')+'</section>'))
print('Created',len(list(DIST.rglob('index.html'))),'pages and a 404 page.')
