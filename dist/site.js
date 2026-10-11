const toggle=document.querySelector('.menu-toggle');
const nav=document.querySelector('.nav');
const groups=[...document.querySelectorAll('.nav-group')];
toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));toggle.textContent=open?'Close ×':'Menu ☰';nav.classList.toggle('open',open);if(!open)groups.forEach(group=>group.open=false)});
groups.forEach(group=>group.addEventListener('toggle',()=>{if(group.open)groups.filter(other=>other!==group).forEach(other=>other.open=false)}));
document.addEventListener('click',event=>{groups.forEach(group=>{if(!group.contains(event.target))group.open=false})});
document.addEventListener('keydown',event=>{if(event.key!=='Escape')return;const openGroup=groups.find(group=>group.open);if(openGroup){openGroup.open=false;openGroup.querySelector('summary').focus()}else if(toggle?.getAttribute('aria-expanded')==='true'){toggle.click();toggle.focus()}});
nav?.addEventListener('click',event=>{if(event.target.closest('a')&&toggle?.getAttribute('aria-expanded')==='true')toggle.click()});

// One shared name card keeps full names out of copied citations and author text.
const authorTriggers=[...document.querySelectorAll('.author-name-trigger')];
if(authorTriggers.length){
 const tooltip=document.createElement('div');
 tooltip.id='author-name-tooltip';tooltip.className='author-name-tooltip';tooltip.setAttribute('role','tooltip');tooltip.hidden=true;
 const korean=document.createElement('span'),english=document.createElement('span');
 korean.className='author-name-ko';korean.lang='ko';english.className='author-name-en';english.lang='en';
 tooltip.append(korean,english);document.body.append(tooltip);
 let active=null,pinned=false,closeTimer=null;
 const cancelClose=()=>{clearTimeout(closeTimer);closeTimer=null};
 function hideAuthorName(){
  cancelClose();
  if(active){active.setAttribute('aria-expanded','false');active.removeAttribute('aria-describedby')}
  active=null;pinned=false;tooltip.hidden=true;
 }
 function showAuthorName(trigger,pin=false){
  cancelClose();
  if(active&&active!==trigger){active.setAttribute('aria-expanded','false');active.removeAttribute('aria-describedby')}
  active=trigger;pinned=pin;
  korean.textContent=trigger.dataset.authorKo;english.textContent=trigger.dataset.authorEn;
  tooltip.hidden=false;trigger.setAttribute('aria-expanded','true');trigger.setAttribute('aria-describedby',tooltip.id);
  const anchor=trigger.getBoundingClientRect(),card=tooltip.getBoundingClientRect(),margin=12,gap=9;
  const left=Math.max(margin,Math.min(anchor.left+(anchor.width-card.width)/2,window.innerWidth-card.width-margin));
  const below=anchor.bottom+gap;
  const top=below+card.height<=window.innerHeight-margin?below:Math.max(margin,anchor.top-card.height-gap);
  tooltip.style.left=`${left}px`;tooltip.style.top=`${top}px`;
 }
 function scheduleClose(){
  cancelClose();if(pinned)return;
  closeTimer=setTimeout(()=>{
   if(active===document.activeElement||active?.matches(':hover')||tooltip.matches(':hover'))return;
   hideAuthorName();
  },160);
 }
 authorTriggers.forEach(trigger=>{
  trigger.setAttribute('aria-controls',tooltip.id);
  trigger.addEventListener('pointerenter',event=>{if(event.pointerType!=='touch')showAuthorName(trigger)});
  trigger.addEventListener('pointerleave',scheduleClose);
  trigger.addEventListener('focus',()=>{if(trigger.matches(':focus-visible'))showAuthorName(trigger)});
  trigger.addEventListener('blur',()=>{if(active===trigger){pinned=false;scheduleClose()}});
  trigger.addEventListener('click',()=>{if(active===trigger&&pinned)hideAuthorName();else showAuthorName(trigger,true)});
 });
 tooltip.addEventListener('pointerenter',cancelClose);tooltip.addEventListener('pointerleave',scheduleClose);
 document.addEventListener('click',event=>{if(!event.target.closest('.author-name-trigger')&&!tooltip.contains(event.target))hideAuthorName()});
 document.addEventListener('keydown',event=>{if(event.key==='Escape')hideAuthorName()});
 document.addEventListener('input',hideAuthorName);document.addEventListener('change',hideAuthorName);
 window.addEventListener('scroll',hideAuthorName,{passive:true,capture:true});window.addEventListener('resize',hideAuthorName);
}

const library=document.querySelector('[data-library]');
if(library){
 const cards=[...library.querySelectorAll('[data-paper]')];
 const search=library.querySelector('[data-search]'),year=library.querySelector('[data-year]'),journal=library.querySelector('[data-journal]');
 const keywords=[...library.querySelectorAll('[data-keyword]')];
 const normalize=s=>s.toLowerCase().normalize('NFKC').replace(/[‐‑–−]/g,'-');
 const searchable=new Map(cards.map(card=>[card,normalize(card.querySelector('h3').textContent+' '+card.querySelector('.publication-authors').textContent+' '+[...card.querySelectorAll('.publication-authors .author-name-trigger')].map(author=>author.dataset.authorKo+' '+author.dataset.authorEn).join(' ')+' '+card.dataset.journal)]));
 function updateImpactSummary(){
  if(!library.querySelector('[data-if-sum]'))return;
  const scopeCards=cards.filter(card=>!year.value||card.dataset.year===year.value);
  const impacts=scopeCards.map(card=>card.dataset.if).filter(value=>value!==undefined&&value!=='').map(Number).filter(value=>Number.isFinite(value)&&value>=0);
  const tenths=impacts.reduce((sum,value)=>sum+Math.round(value*10),0);
  library.querySelector('[data-if-sum]').textContent=impacts.length?(tenths/10).toLocaleString('en-US',{minimumFractionDigits:1,maximumFractionDigits:1}):'—';
  library.querySelector('[data-if-average]').textContent=impacts.length?(Math.round(tenths*10/impacts.length)/100).toFixed(2):'—';
  const coverage=library.querySelector('[data-if-coverage]'),missing=impacts.length!==scopeCards.length;
  coverage.hidden=!missing;coverage.textContent=`IF 확인 ${impacts.length} / ${scopeCards.length}편`;
  const label=year.value||library.dataset.ifYearLabel;
  const scope=label==='All'?'전체 연도':`${label}년`;
  const basis=/^\d{4}$/.test(label)?`${Number(label)-1}년 IF`:'논문 게재연도의 전년도 IF';
  library.querySelector('[data-if-scope]').textContent=`${scope}${label==='All'?' 논문':' 전체 논문'} 기준 · ${basis}${missing?' · IF가 확인된 논문만 집계':''}`;
 }
 function filter(){
  const terms=normalize(search.value).trim().split(/\s+/).filter(Boolean),selected=keywords.filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.dataset.keyword);
  let count=0;
  cards.forEach(card=>{const show=(!year.value||card.dataset.year===year.value)&&(!journal.value||card.dataset.journal===journal.value)&&terms.every(term=>searchable.get(card).includes(term))&&(!selected.length||selected.some(key=>card.dataset.keywords.split(' ').includes(key)));card.hidden=!show;if(show)count++});
  library.querySelector('[data-result-count]').textContent=`${count} / ${cards.length} publications · 논문`;
  updateImpactSummary();
  library.querySelector('[data-empty]').hidden=count!==0;
 }
 search.addEventListener('input',filter);year.addEventListener('change',filter);journal.addEventListener('change',filter);
 keywords.forEach(button=>button.addEventListener('click',()=>{button.setAttribute('aria-pressed',String(button.getAttribute('aria-pressed')!=='true'));filter()}));
 library.querySelector('[data-reset]').addEventListener('click',()=>{search.value='';year.value='';journal.value='';keywords.forEach(b=>b.setAttribute('aria-pressed','false'));filter()});
 library.addEventListener('click',async event=>{
  const button=event.target.closest('[data-copy-citation],[data-copy-bib],[data-download-bib]');if(!button)return;
  const card=button.closest('[data-paper]');
  const bib=card.querySelector('.bibtex-text').textContent;
  if(button.hasAttribute('data-download-bib')){const url=URL.createObjectURL(new Blob([bib+'\n'],{type:'application/x-bibtex;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=button.dataset.filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);return}
  const text=button.hasAttribute('data-copy-citation')?card.querySelector('.citation-text').textContent:bib;
  try{await navigator.clipboard.writeText(text);button.textContent='Copied ✓';setTimeout(()=>button.textContent=button.hasAttribute('data-copy-citation')?'Copy citation':'Copy BibTeX',1800)}catch{card.querySelector('details').open=true;library.querySelector('.copy-feedback').textContent='인용 정보를 펼쳤습니다. 텍스트를 선택해 복사해 주세요. Select the citation text to copy.'}
 });
 filter();
}

const photoDialog=document.querySelector('.photo-dialog');
if(photoDialog&&typeof photoDialog.showModal==='function'){
 const links=[...document.querySelectorAll('[data-lightbox]')];
 const image=photoDialog.querySelector('[data-photo-image]');
 const caption=photoDialog.querySelector('[data-photo-caption]');
 let current=0,opener=null;
 const show=index=>{current=(index+links.length)%links.length;const link=links[current];image.src=link.href;image.alt=link.querySelector('img').alt;caption.textContent=link.dataset.caption};
 links.forEach((link,index)=>link.addEventListener('click',event=>{if(event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;event.preventDefault();opener=link;show(index);photoDialog.showModal();document.body.classList.add('photo-dialog-open')}));
 photoDialog.querySelector('[data-photo-close]').addEventListener('click',()=>photoDialog.close());
 photoDialog.querySelector('[data-photo-prev]').addEventListener('click',()=>show(current-1));
 photoDialog.querySelector('[data-photo-next]').addEventListener('click',()=>show(current+1));
 photoDialog.addEventListener('keydown',event=>{if(event.key==='ArrowLeft'){event.preventDefault();show(current-1)}if(event.key==='ArrowRight'){event.preventDefault();show(current+1)}});
 photoDialog.addEventListener('click',event=>{if(event.target===photoDialog){const r=photoDialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)photoDialog.close()}});
 photoDialog.addEventListener('close',()=>{document.body.classList.remove('photo-dialog-open');opener?.focus()});
 if(links.length<2){photoDialog.querySelector('.photo-dialog-stage').classList.add('single-photo');photoDialog.querySelector('[data-photo-prev]').hidden=true;photoDialog.querySelector('[data-photo-next]').hidden=true}
}

// Keep one research interest open, including browsers without details grouping.
const researchChoices=[...document.querySelectorAll('.research-choice')];
researchChoices.forEach(choice=>choice.addEventListener('toggle',()=>{
 if(choice.open)researchChoices.filter(other=>other!==choice).forEach(other=>{other.open=false});
}));

