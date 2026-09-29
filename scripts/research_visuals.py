"""Qualitative research illustrations; no measured data or crystal models."""
from pathlib import Path
from html import escape

OUT=Path(__file__).resolve().parents[1]/'dist/assets'
def label(x,y,text,size=24,color='#d6e4ee',anchor='middle'):
 return f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" font-size="{size}" font-family="Arial,sans-serif">{escape(text)}</text>'
def circle(x,y,r=13,color='url(#ion)'):
 return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'
def line(x1,y1,x2,y2,color='#7195aa',width=3,extra=''):
 return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width="{width}" fill="none" {extra}/>'
def svg(name,title,body):
 defs='''<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#0a1d32"/><stop offset="1" stop-color="#173c4b"/></linearGradient><radialGradient id="ion" cx=".3" cy=".25"><stop stop-color="#f0ffc9"/><stop offset="1" stop-color="#a8d558"/></radialGradient><radialGradient id="atom" cx=".3" cy=".25"><stop stop-color="#a1ebf5"/><stop offset="1" stop-color="#38809c"/></radialGradient><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#a3d6e5" stroke-opacity=".055"/></pattern><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto-start-reverse"><path d="M0 0L7 4L0 8" fill="none" stroke="#c6f36b" stroke-width="1.5"/></marker></defs>'''
 (OUT/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="560" viewBox="0 0 900 560" role="img"><title>{escape(title)}</title>{defs}<rect width="900" height="560" rx="20" fill="url(#bg)"/><rect width="900" height="560" fill="url(#grid)"/>'+body+'</svg>')

# Intercalation host: deliberately a conceptual lattice, not a crystal structure.
b=label(45,55,'01  /  LITHIUM-ION',22,'#c6f36b','start')
for y in [155,265,375]:
 b+=f'<path d="M95 {y}L420 {y}L510 {y-48}L185 {y-48}Z" fill="#295266" stroke="#5d9aae" stroke-width="2"/>'
 for x in range(120,440,63): b+=circle(x,y-7,17,'url(#atom)')
for y in [206,316]:
 for x in [175,280,385]: b+=circle(x,y,14)
 b+=line(565,y,435,y,'#c6f36b',3,'marker-start="url(#arrow)" marker-end="url(#arrow)"')
b+=circle(620,250,34)+label(620,259,'Li⁺',25,'#0a1d32')
b+=label(680,333,'Reversible',25)+label(680,366,'ion transport',25)
b+=label(300,445,'Electrode host',26)+label(450,513,'Composition  /  Structure  /  Redox',24,'#c6f36b')
svg('research-lithium.svg','Conceptual lithium-ion insertion and extraction in an electrode host',b)

# Separate systems, not a mixed-ion cell.
b=label(45,55,'02  /  BEYOND LITHIUM',22,'#c6f36b','start')
for x,ion,title,sub in [(165,'Na⁺','Sodium-ion','Electrode design'),(450,'K⁺','Potassium-ion','Ion transport'),(735,'Zn²⁺','Aqueous zinc','Reversible reactions')]:
 b+=f'<rect x="{x-118}" y="103" width="236" height="350" rx="15" fill="#ffffff" fill-opacity=".035" stroke="#537889"/>'
 b+=circle(x,187,47)+label(x,197,ion,31,'#0a1d32')
 b+=f'<rect x="{x-77}" y="283" width="24" height="84" rx="4" fill="#65adbf"/><rect x="{x+53}" y="283" width="24" height="84" rx="4" fill="#c6f36b"/>'
 if ion=='Zn²⁺':
  b+=f'<path d="M{x-43} 349Q{x-22} 331 {x} 349T{x+43} 349" fill="none" stroke="#75c7e0" stroke-width="4"/>'
 b+=line(x-39,314,x+37,314,'#c6f36b',2.5,'marker-start="url(#arrow)" marker-end="url(#arrow)"')
 b+=label(x,404,title,24)+label(x,434,sub,18,'#a9c8d6')
b+=label(450,513,'Alternative chemistries  /  Shared materials insight',24,'#c6f36b')
svg('research-beyond-lithium.svg','Three separate research systems: sodium-ion, potassium-ion and aqueous zinc batteries',b)

# Solid-state interface, with a magnified conceptual coating region.
b=label(45,55,'03  /  SOLID-STATE',22,'#c6f36b','start')
for x,w,color in [(115,220,'#315971'),(335,23,'#c6f36b'),(358,242,'#457f8e'),(600,130,'#9baeb7')]:
 b+=f'<rect x="{x}" y="150" width="{w}" height="210" fill="{color}" rx="3"/>'
for x,y in [(160,200),(220,270),(280,195),(170,322),(300,320)]: b+=circle(x,y,24,'url(#atom)')
for x,y in [(400,200),(470,255),(545,310)]: b+=circle(x,y,11)
b+=line(185,255,673,255,'#c6f36b',3,'marker-end="url(#arrow)"')
b+=label(240,408,'Cathode',24)+label(480,404,'Solid',24)+label(480,433,'electrolyte',24)+label(665,408,'Anode',24)
b+=line(347,150,347,111,'#c6f36b',2)+label(347,98,'Protective coating',23,'#c6f36b')
b+=label(450,513,'Interface stability  /  Coatings  /  Ion transport',24,'#c6f36b')
svg('research-solid-state.svg','Conceptual solid-state battery with a protective cathode coating and lithium-ion transport',b)
