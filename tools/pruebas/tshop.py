import sys; sys.path.insert(0,'/root/v2/test'); sys.path.insert(0,'/root/v2/tools')
from sh2sim import CPU
import font8
DEC={v:k for k,v in font8.CHAR2CODE.items()}
for f,fn,actp,cnt,na,nb in [('A_R8S5.BIN',0x60752c4,0x608ae08,0x608a870,6,7),('A_R8S6.BIN',0x6073b58,0x6086818,0x6086528,3,7)]:
    b=open(f'/root/v2/out/files/{f}','rb').read()
    # localizar inicio real de la rutina (push r8) antes del bloque
    print(f)
    for tab,n in (('A',na),('B',nb)):
        for idx in range(n):
            c=CPU(); c.load(0x6060000,b); c.r[15]=0x60ff000; log=[]
            c.wl(0x6060828,0x6100200); c.ww(0x6100200,0x200 if tab=='A' else 0)
            c.wl(actp,0x6100000); c.ww(0x61000a4,idx); c.ww(0x6100002,0)
            c.stubs[0x6078994]=lambda c:(c.r.__setitem__(0,c.r[4]),c.r.__setitem__(1,0))
            for a in (0x60783f8,0x6078a20,0x607bce8,0x6074c70,0x6075298): c.stubs[a]=lambda c:None
            c.stubs[0x60783f8]=lambda c:None
            def sp(c,log=log): log.append((c.rl(c.r[15]),c.r[4]))
            c.stubs[0x60706a4]=sp
            xs=[]
            for k in range(45):
                c.ww(cnt,k); n0=len(log)
                c.stubs[0x6078994 if f=='A_R8S5.BIN' else 0x607520c]=lambda c,xs=xs:(xs.append(c.r[4]),c.r.__setitem__(0,c.r[4]),c.r.__setitem__(1,0))
                c.call(fn)
                if len(log)==n0: break
            s=''.join(DEC.get(code,'{%x}'%code) for code,t in log)
            print(f'  {tab}{idx} n={len(log)} x={xs[:2]}..{xs[-1:]} |{s}|')
