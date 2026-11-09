D="#1d1d1d"
W,H=1600,1380
def brain(id,c):
    cs=[(36,40,18),(64,40,18),(30,62,16),(70,62,16),(50,66,16),(50,34,16)]
    s=f'<symbol id="{id}" viewBox="0 0 100 100">'
    s+=''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{D}" stroke="{D}" stroke-width="6"/>' for x,y,r in cs)
    s+=''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x,y,r in cs)
    s+=f'<path d="M50 20 C42 38 58 46 50 64 M33 48 C42 50 44 56 37 62 M67 48 C58 50 56 56 63 62 M40 30 C46 32 46 38 42 40 M60 30 C54 32 54 38 58 40" fill="none" stroke="{D}" stroke-width="2.6" stroke-linecap="round"/>'
    s+=f'<path d="M46 80 L46 92 L54 92 L54 80" fill="{c}" stroke="{D}" stroke-width="3"/></symbol>'
    return s
def mag(cx,cy,r):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#ffffff" fill-opacity=".55" stroke="{D}" stroke-width="3.5"/>'
            f'<line x1="{cx+r*.7}" y1="{cy+r*.7}" x2="{cx+r+12}" y2="{cy+r+12}" stroke="{D}" stroke-width="8" stroke-linecap="round"/>')
S=f'stroke="{D}" stroke-width="3" stroke-linejoin="round"'
sym=[]
sym.append(f'''<symbol id="person" viewBox="0 0 100 100">
<path d="M16 98 C16 72 32 62 50 62 C68 62 84 72 84 98 Z" fill="#6c4de6" {S}/>
<circle cx="50" cy="36" r="20" fill="#f7c9a1" {S}/>
<path d="M30 34 C28 12 72 12 70 34 C62 24 40 24 30 34Z" fill="#5a3fd0" {S}/>
<circle cx="42" cy="40" r="6.5" fill="#bfe8ff" {S}/><circle cx="58" cy="40" r="6.5" fill="#bfe8ff" {S}/>
<line x1="48.5" y1="40" x2="51.5" y2="40" stroke="{D}" stroke-width="2.5"/>
<path d="M44 50 Q50 56 56 50" fill="none" stroke="{D}" stroke-width="2.5" stroke-linecap="round"/>
<rect x="28" y="70" width="44" height="22" rx="3" fill="#ecebf6" {S}/><circle cx="50" cy="81" r="4.5" fill="#6c4de6"/>
<rect x="22" y="92" width="56" height="6" rx="3" fill="#cfcfe0" {S}/></symbol>''')
sym.append(brain('brain_g','#4cc15a')); sym.append(brain('brain_p','#8f7bf0'))
sym.append(f'''<symbol id="folder" viewBox="0 0 100 100">
<path d="M8 24 h30 l8 9 h44 a4 4 0 0 1 4 4 v48 a4 4 0 0 1 -4 4 H12 a4 4 0 0 1 -4 -4 Z" fill="#35b772" {S}/>
<rect x="20" y="30" width="58" height="36" fill="#fff" transform="rotate(-5 50 50)" {S}/>
<path d="M8 50 h88 l-6 40 a4 4 0 0 1 -4 3 H14 a4 4 0 0 1 -4 -4 Z" fill="#5fdc9c" {S}/></symbol>''')
dots=''.join(f'<circle cx="{x}" cy="{y}" r="2.6" fill="{c}"/>' for y in (25,51,77) for x,c in ((24,'#19b394'),(32,D)))
sym.append(f'''<symbol id="db" viewBox="0 0 100 100">
<rect x="12" y="12" width="66" height="24" rx="7" fill="#d9e2ee" {S}/><rect x="12" y="39" width="66" height="24" rx="7" fill="#d9e2ee" {S}/><rect x="12" y="66" width="66" height="24" rx="7" fill="#d9e2ee" {S}/>
{dots}<line x1="56" y1="24" x2="70" y2="24" stroke="{D}" stroke-width="3" stroke-linecap="round"/><line x1="56" y1="51" x2="70" y2="51" stroke="{D}" stroke-width="3" stroke-linecap="round"/><line x1="56" y1="78" x2="70" y2="78" stroke="{D}" stroke-width="3" stroke-linecap="round"/>
<path d="M88 4 l4 9 9 4 -9 4 -4 9 -4 -9 -9 -4 9 -4 z" fill="#ffd23f" {S}/></symbol>''')
sym.append(f'''<symbol id="server" viewBox="0 0 100 100"><rect x="12" y="14" width="76" height="72" rx="14" fill="#19b394" {S}/>
<path d="M56 24 L32 54 H47 L42 78 L68 44 H53 Z" fill="#fff" {S}/></symbol>''')
sym.append(f'''<symbol id="browser" viewBox="0 0 100 100"><rect x="8" y="14" width="84" height="72" rx="9" fill="#fff" {S}/>
<path d="M8 23 a9 9 0 0 1 9 -9 h66 a9 9 0 0 1 9 9 v9 H8 Z" fill="#7fd8f0" {S}/>
<circle cx="19" cy="23" r="3" fill="#ff6b6b"/><circle cx="29" cy="23" r="3" fill="#ffd23f"/><circle cx="39" cy="23" r="3" fill="#4cc15a"/>
<rect x="20" y="58" width="12" height="22" fill="#ff9bb3" {S}/><rect x="38" y="48" width="12" height="32" fill="#ffd23f" {S}/><rect x="56" y="40" width="12" height="40" fill="#8f7bf0" {S}/><rect x="74" y="52" width="10" height="28" fill="#4cc15a" {S}/></symbol>''')
sym.append(f'''<symbol id="sql" viewBox="0 0 100 100"><rect x="8" y="14" width="64" height="56" rx="5" fill="#fff" {S}/>
<path d="M8 19 a5 5 0 0 1 5 -5 h54 a5 5 0 0 1 5 5 v13 H8 Z" fill="#ffd666" {S}/>
<path d="M8 51 H72 M30 14 V70 M51 14 V70" stroke="{D}" stroke-width="2.5" fill="none"/>
{mag(66,62,17)}</symbol>''')
sc=''.join(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{c}" stroke="{D}" stroke-width="2"/>' for x,y,c in((22,28,'#8f7bf0'),(34,48,'#ff6b6b'),(52,30,'#4cc15a'),(26,58,'#ffa94d'),(46,56,'#8f7bf0'),(60,44,'#ff6b6b')))
sym.append(f'''<symbol id="vec" viewBox="0 0 100 100"><rect x="8" y="14" width="64" height="56" rx="5" fill="#fff" {S}/>{sc}{mag(66,62,17)}</symbol>''')
sym.append(f'''<symbol id="cards" viewBox="0 0 100 100"><rect x="22" y="14" width="50" height="66" rx="5" fill="#8f7bf0" transform="rotate(-12 47 47)" {S}/>
<rect x="26" y="14" width="50" height="66" rx="5" fill="#ff9bb3" transform="rotate(8 50 47)" {S}/>
<rect x="22" y="18" width="52" height="68" rx="5" fill="#fff" {S}/>
<path d="M32 36 l5 5 9 -10" fill="none" stroke="#19b394" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M52 36 H66 M32 54 H66 M32 68 H58" stroke="{D}" stroke-width="3" stroke-linecap="round"/></symbol>''')
sym.append(f'''<symbol id="watch" viewBox="0 0 100 100"><rect x="38" y="4" width="24" height="92" rx="6" fill="#4a4a55" {S}/>
<circle cx="50" cy="50" r="30" fill="#ff5a3c" {S}/><circle cx="50" cy="50" r="21" fill="#fff" {S}/>
<path d="M50 50 V36 M50 50 L60 56" stroke="{D}" stroke-width="3.5" stroke-linecap="round"/><circle cx="50" cy="50" r="2.5" fill="{D}"/></symbol>''')
rays=''.join(f'<line x1="50" y1="50" x2="{50+ (30 if i%2==0 else 22)*__import__("math").cos(i*0.7854):.1f}" y2="{50+(30 if i%2==0 else 22)*__import__("math").sin(i*0.7854):.1f}" stroke="#fff" stroke-width="7" stroke-linecap="round"/>' for i in range(8))
sym.append(f'<symbol id="claude" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="#d97757" {S}/>{rays}</symbol>')
teeth=''.join(f'<rect x="43" y="8" width="14" height="22" rx="3" fill="#4b8bbe" transform="rotate({k*45} 50 50)" {S}/>' for k in range(8))
sym.append(f'<symbol id="gear" viewBox="0 0 100 100">{teeth}<circle cx="50" cy="50" r="28" fill="#4b8bbe" {S}/><circle cx="50" cy="50" r="11" fill="#ffd43b" {S}/></symbol>')

sym.append(f'''<symbol id="lock" viewBox="0 0 100 100"><path d="M32 46 V32 a18 18 0 0 1 36 0 V46" fill="none" stroke="{D}" stroke-width="9" stroke-linecap="round"/>
<path d="M32 46 V32 a18 18 0 0 1 36 0 V46" fill="none" stroke="#c9ced6" stroke-width="4" stroke-linecap="round"/>
<rect x="20" y="44" width="60" height="46" rx="9" fill="#ffd23f" {S}/><circle cx="50" cy="62" r="6" fill="{D}"/><rect x="47" y="64" width="6" height="14" rx="2" fill="{D}"/></symbol>''')
sym.append(f'''<symbol id="shield" viewBox="0 0 100 100"><path d="M50 8 L86 22 V50 C86 74 68 88 50 94 C32 88 14 74 14 50 V22 Z" fill="#4cc15a" {S}/>
<path d="M32 52 L46 66 L70 36" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></symbol>''')
sym.append(f'''<symbol id="nocode" viewBox="0 0 100 100"><rect x="10" y="22" width="80" height="56" rx="8" fill="#fff" {S}/>
<path d="M36 38 L24 50 L36 62 M64 38 L76 50 L64 62 M55 34 L45 66" fill="none" stroke="{D}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="50" cy="50" r="40" fill="none" stroke="#ff5a5a" stroke-width="7"/><line x1="22" y1="78" x2="78" y2="22" stroke="#ff5a5a" stroke-width="7" stroke-linecap="round"/></symbol>''')
sym.append(f'''<symbol id="stop" viewBox="0 0 100 100"><path d="M34 8 H66 L92 34 V66 L66 92 H34 L8 66 V34 Z" fill="#ff5a5a" {S}/>
<rect x="44" y="26" width="12" height="32" rx="6" fill="#fff"/><circle cx="50" cy="72" r="6.5" fill="#fff"/></symbol>''')
sym.append(f'''<symbol id="receipt" viewBox="0 0 100 100"><path d="M20 8 H80 V92 L70 84 L60 92 L50 84 L40 92 L30 84 L20 92 Z" fill="#fff" {S}/>
<path d="M32 28 H68 M32 44 H68 M32 60 H54" stroke="{D}" stroke-width="4" stroke-linecap="round"/><path d="M60 66 l6 6 12 -14" fill="none" stroke="#19b394" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></symbol>''')

o=[]; a=o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('<defs>'+''.join(sym)+f'''
<filter id="noise" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .07 0"/></filter>
<marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1,1 L9,5 L1,9" fill="none" stroke="{D}" stroke-width="1.8" stroke-linecap="round"/></marker>
<marker id="ab" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1,1 L9,5 L1,9" fill="none" stroke="#2f8fe0" stroke-width="1.8" stroke-linecap="round"/></marker>
<style>@import url("https://fonts.googleapis.com/css2?family=Kalam:wght@700&family=Patrick+Hand&display=swap");
.k{{font-family:'Kalam',cursive;font-weight:700}} .p{{font-family:'Patrick Hand',cursive;fill:{D}}}
.lb{{font-size:25px}} .ls{{font-size:20px;fill:#555}}</style></defs>''')
a(f'<rect width="{W}" height="{H}" fill="#fff"/>')
# header
a('<rect x="30" y="24" width="18" height="76" rx="9" fill="#cdb8ff" stroke="#b79cf5" stroke-width="2"/>')
a(f'<rect x="64" y="20" width="250" height="84" rx="16" fill="#12a36a" stroke="{D}" stroke-width="3"/>')
a('<text x="189" y="82" text-anchor="middle" class="k" font-size="58" fill="#fff">COROS</text>')
a(f'<text x="336" y="84" class="k" font-size="64" fill="{D}">Chat Architecture</text>')
a(f'<text x="1570" y="70" text-anchor="end" class="p" font-size="26" fill="#555">100% local · no training data leaves the machine</text>')
def panel(y,h,title,tw):
    a(f'<rect x="30" y="{y}" width="1540" height="{h}" rx="26" fill="#f1f1f1" stroke="{D}" stroke-width="4"/>')
    a(f'<rect x="58" y="{y+20}" width="{tw}" height="58" rx="29" fill="#7c6af2"/>')
    a(f'<text x="{58+tw/2}" y="{y+61}" text-anchor="middle" class="k" font-size="36" fill="#fff">{title}</text>')
def icon(i,cx,top,s=110): a(f'<use xlink:href="#{i}" x="{cx-s/2}" y="{top}" width="{s}" height="{s}"/>')
def label(cx,y,l1,l2=None,anchor="middle"):
    a(f'<text x="{cx}" y="{y}" text-anchor="{anchor}" class="p lb">{l1}</text>')
    if l2: a(f'<text x="{cx}" y="{y+24}" text-anchor="{anchor}" class="p ls">{l2}</text>')
def arr(d,blue=False):
    c="#2f8fe0" if blue else D; m="ab" if blue else "ah"
    a(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round" marker-end="url(#{m})"/>')
def arr2(d):
    a(f'<path d="{d}" fill="none" stroke="{D}" stroke-width="3" stroke-linecap="round" marker-end="url(#ah)" marker-start="url(#ah)"/>')

# PANEL 1
panel(130,570,"Ask (runtime)",270)
T=280
icon('person',145,T); label(145,T+140,"User question","Vietnamese / English")
icon('browser',415,T); label(415,T+140,"React UI","Recharts draws chart spec")
icon('server',685,T); label(685,T+140,"FastAPI","+ chat loop")
icon('brain_g',985,T); label(985,T+140,"Ollama LLM","qwen3:14b, picks tools")
arr(f"M205 {T+55} C250 {T+45}, 290 {T+65}, 352 {T+55}")
arr(f"M477 {T+55} C520 {T+45}, 560 {T+65}, 622 {T+55}")
arr2(f"M747 {T+55} C800 {T+45}, 850 {T+65}, 925 {T+55}")
arr(f"M670 {T-6} C600 {T-70}, 230 {T-70}, 150 {T-6}",blue=True)
a(f'<text x="590" y="{T-56}" text-anchor="middle" class="p lb" fill="#2f8fe0" style="fill:#2f8fe0">answer + sources + chart</text>')
# sticky
a(f'<g transform="rotate(-2 1330 320)"><rect x="1160" y="262" width="350" height="112" rx="10" fill="#fff3b0" stroke="{D}" stroke-width="3"/>'
  f'<text x="1335" y="305" text-anchor="middle" class="p" font-size="27">numbers → SQL columns</text>'
  f'<text x="1335" y="345" text-anchor="middle" class="p" font-size="27">meaning → vectors</text></g>')
# tools belt
a(f'<rect x="330" y="515" width="720" height="165" rx="20" fill="#fff" fill-opacity=".6" stroke="{D}" stroke-width="3" stroke-dasharray="10 8"/>')
a(f'<text x="350" y="508" class="p lb" style="fill:#555">tools the model can call</text>')
arr(f"M685 {T+190} C690 {T+215}, 684 {T+225}, 685 512")
for cx,i,l1,l2 in((480,'sql',"SQL tools","read-only, guarded"),(690,'vec',"Vector search","bge-m3 embeddings"),(900,'cards',"Guidance cards","expert sources")):
    icon(i,cx,530,85); label(cx,640,l1); 
    a(f'<text x="{cx}" y="664" text-anchor="middle" class="p ls">{l2}</text>')
icon('db',1330,500,130); label(1330,660,"Postgres + pgvector"); a(f'<text x="1330" y="684" text-anchor="middle" class="p ls">chatbot role: SELECT only</text>')
arr("M1052 598 C1120 585, 1180 612, 1262 600")

# PANEL 2
panel(730,290,"Load (on demand)",350)
Y=830
items=[(145,'watch',"COROS connector","read-only"),(420,'claude',"Claude session","pulls by date, retries"),(695,'folder',"Raw files","kept exactly as received"),(970,'gear',"Python parsers","idempotent by id"),(1245,'brain_p',"Embeddings","bge-m3 summaries"),(1470,'db',"Postgres","+ pgvector")]
for cx,i,l1,l2 in items:
    icon(i,cx,Y,100); label(cx,Y+138,l1,l2)
xs=[c for c,*_ in items]
for k in range(5):
    x1=xs[k]+62; x2=xs[k+1]-62
    arr(f"M{x1} {Y+50} C{x1+30} {Y+42}, {x2-30} {Y+58}, {x2} {Y+50}")

# PANEL 3
panel(1050,300,"Guardrails (why trust it)",440)
Y=1150
g=[(145,'lock',"Read-only role","SELECT only, 5 s timeout"),(420,'shield',"Guarded SQL","checked before it runs"),(695,'nocode',"Charts from a spec","model never writes code"),(970,'cards',"Sourced advice","14 cards with source links"),(1245,'stop',"Scope rule","declines medical, off-topic"),(1450,'receipt',"Traceable","shows the tools used")]
for cx,i,l1,l2 in g:
    icon(i,cx,Y,100); label(cx,Y+138,l1,l2)
a('</svg>')
open('architecture_sketch.svg','w').write('\n'.join(o))
