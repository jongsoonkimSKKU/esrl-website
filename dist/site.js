const toggle=document.querySelector('.menu-toggle');
const nav=document.querySelector('.nav');
const groups=[...document.querySelectorAll('.nav-group')];
toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));toggle.textContent=open?'Close ×':'Menu ☰';nav.classList.toggle('open',open);if(!open)groups.forEach(group=>group.open=false)});
groups.forEach(group=>group.addEventListener('toggle',()=>{if(group.open)groups.filter(other=>other!==group).forEach(other=>other.open=false)}));
document.addEventListener('click',event=>{groups.forEach(group=>{if(!group.contains(event.target))group.open=false})});
document.addEventListener('keydown',event=>{if(event.key!=='Escape')return;const openGroup=groups.find(group=>group.open);if(openGroup){openGroup.open=false;openGroup.querySelector('summary').focus()}else if(toggle?.getAttribute('aria-expanded')==='true'){toggle.click();toggle.focus()}});
nav?.addEventListener('click',event=>{if(event.target.closest('a')&&toggle?.getAttribute('aria-expanded')==='true')toggle.click()});

const library=document.querySelector('[data-library]');
if(library){
 const cards=[...library.querySelectorAll('[data-paper]')];
 const search=library.querySelector('[data-search]'),year=library.querySelector('[data-year]'),journal=library.querySelector('[data-journal]');
 const keywords=[...library.querySelectorAll('[data-keyword]')];
 const normalize=s=>s.toLowerCase().normalize('NFKC').replace(/[‐‑–−]/g,'-');
 const searchable=new Map(cards.map(card=>[card,normalize(card.querySelector('h3').textContent+' '+card.querySelector('.publication-authors').textContent+' '+card.dataset.journal)]));
 function filter(){
  const terms=normalize(search.value).trim().split(/\s+/).filter(Boolean),selected=keywords.filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.dataset.keyword);
  let count=0;
  cards.forEach(card=>{const show=(!year.value||card.dataset.year===year.value)&&(!journal.value||card.dataset.journal===journal.value)&&terms.every(term=>searchable.get(card).includes(term))&&(!selected.length||selected.some(key=>card.dataset.keywords.split(' ').includes(key)));card.hidden=!show;if(show)count++});
  library.querySelector('[data-result-count]').textContent=`${count} / ${cards.length} publications · 논문`;
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
