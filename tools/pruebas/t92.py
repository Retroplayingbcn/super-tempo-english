import sys,struct; sys.path.insert(0,'/root/v2/test'); sys.path.insert(0,'/root/v2/tools')
from sh2sim import CPU
import font8,script
DEC={v:k for k,v in font8.CHAR2CODE.items()}; DEC[0xef]='_'
def setup(f):
    c=CPU(); c.load(0x6060000,open(f'/root/v2/out/files/{f}','rb').read())
    c.r[15]=0x060ff000
    c.log=[]
    c.stubs[0x60755e4]=lambda c:(c.r.__setitem__(0,(c.r[4]<<16)&0xffffffff),c.r.__setitem__(1,0))
    c.stubs[0x6075048]=lambda c:None
    c.stubs[0x6075670]=lambda c:None
    def spawn(c): c.log.append((c.r[7]&0xffff,(c.r[5]>>16)&0xffff,(c.r[6]>>16)&0xffff)); c.r[0]=1
    c.stubs[0x6070754]=spawn
    def spawn2(c): c.log.append((c.rl(c.r[15]+0)&0xffff,(c.r[5]>>16)&0xffff,(c.r[6]>>16)&0xffff,'t%d'%c.r[4])); 
    c.stubs[0x60706a4]=spawn2
    for a in (0x6072910,0x6070ac8,0x6078574): c.stubs[a]=lambda c:None
    c.wl(0x6086ea8,0x6100000); c.wl(0x6060828,0x6100200); c.wl(0x6060644,0x6100210); c.wl(0x6060544,0x6100220); c.wl(0x606054c,0x6100230)
    return c
def show(log,base=0):
    rows={}
    for e in log:
        rows.setdefault(e[2],[]).append(e)
    for y,es in sorted(rows.items()):
        line=''.join(DEC.get(e[0]-base,'{%x}'%e[0]) for e in es)
        print(f'  y={y} x0={es[0][1]} dx={(es[1][1]-es[0][1]) if len(es)>1 else 0} n={len(es)} |{line}|')
def ptr(c,addr): return c.rl(addr)
f='A_R9S2.BIN'
# carta: funciones 0x607313c...
c=setup(f)
for fn in range(0x607313c,0x6073320,0x24):
    if c.rw(fn)==0x2fe6: c.call(fn)
print('carta'); show(c.log)
# selector de ronda: llamadas directas como el juego
c=setup(f)
for p,x,y in [(0x6074488,80,64),(0x6074490,32,88),(0x6074494,32,112),(0x6074498,32,136),(0x607449c,32,160)]:
    c.call(0x6072a14,r4=x,r5=y,r6=c.rl(p))
print('selector'); show(c.log)
c=setup(f); c.call(0x6072a14,r4=104,r5=100,r6=c.rl(0x60743d4)); print('fin'); show(c.log)
# créditos: algunas cadenas
c=setup(f)
for k in range(0,40,3):
    c.log=[]; n=c.call(0x6072a14,r4=0,r5=200,r6=c.rl(0x6086b0c+4*k)); 
    if c.log: show(c.log)
# rangos 長者番付
c=setup(f)
for p in range(0x607381c,0x6073834,4): c.call(0x6073488,r4=156,r5=(p-0x607381c)*10,r6=c.rl(p))
print('rangos'); show(c.log,0x1000)
# máquina de escribir: でちゅ y narración
def tw(c,p,x=16,y=200):
    act=0x6100000
    for i in range(80):
        c.ww(act+0xa2,0)
        c.call(0x6072b0c,r4=x,r5=y,r6=p)
        if c.rw(act+0xa6)==1: break
for k in range(12):
    c=setup(f); tw(c,c.rl(0x608698c+4*k)); show(c.log)
for p in [c.rl(0x6074078),c.rl(0x60743ac),c.rl(0x60743b4),c.rl(0x60743c0)]+[c.rl(0x6086adc+4*k) for k in range(12)]:
    c=setup(f); tw(c,p,32); show(c.log)
