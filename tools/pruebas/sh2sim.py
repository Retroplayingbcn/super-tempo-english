"""Intérprete SH-2 mínimo para ejecutar las rutinas de texto parcheadas y registrar los glifos que crean."""
import struct
M32=0xffffffff
def sx8(v): v&=0xff; return v-0x100 if v&0x80 else v
def sx16(v): v&=0xffff; return v-0x10000 if v&0x8000 else v
class Stop(Exception): pass
class CPU:
    def __init__(s):
        s.mem={}; s.r=[0]*16; s.pc=0; s.pr=0; s.t=0; s.macl=0; s.mach=0; s.stubs={}; s.steps=0
    def load(s,addr,data):
        for i,b in enumerate(data): s.mem[addr+i]=b
    def rb(s,a): return s.mem.get(a&M32,0)
    def rw(s,a): return (s.rb(a)<<8)|s.rb(a+1)
    def rl(s,a): return (s.rw(a)<<16)|s.rw(a+2)
    def wb(s,a,v): s.mem[a&M32]=v&0xff
    def ww(s,a,v): s.wb(a,v>>8); s.wb(a+1,v)
    def wl(s,a,v): s.ww(a,v>>16); s.ww(a+2,v)
    def call(s,addr,**regs):
        for k,v in regs.items(): s.r[int(k[1:])]=v&M32
        s.r[15]=s.r[15] or 0x060ffff0
        s.pr=0xdead0000; s.pc=addr
        while s.pc!=0xdead0000:
            s.step()
        return s.r[0]
    def branch(s,target,delay):
        if delay: s.exec_one(s.pc+2)
        s.pc=target
    def step(s):
        if s.pc in s.stubs:
            s.stubs[s.pc](s); s.pc=s.pr; return
        s.exec_one(s.pc,top=True)
    def exec_one(s,pc,top=False):
        s.steps+=1
        if s.steps>2_000_000: raise Stop('demasiados pasos')
        op=s.rw(pc); r=s.r
        n=(op>>8)&15; m=(op>>4)&15; i8=op&0xff
        nxt=pc+2
        def done():
            if top: s.pc=nxt
        hi=op>>12
        if op==0x0009: return done()
        if op==0x0008: s.t=0; return done()
        if op==0x0018: s.t=1; return done()
        if op==0x0019: s.m=s.q=s.t=0; return done()
        if op==0x000b:  # rts
            s.exec_one(pc+2); s.pc=s.pr; return
        if hi==0xe: r[n]=sx8(i8)&M32; return done()
        if hi==0x9: r[n]=sx16(s.rw(pc+4+i8*2))&M32; return done()
        if hi==0xd: r[n]=s.rl(((pc+4)&~3)+i8*4); return done()
        if hi==0x7: r[n]=(r[n]+sx8(i8))&M32; return done()
        if hi==0xa or hi==0xb:
            d=op&0xfff; d=d-0x1000 if d&0x800 else d
            tgt=pc+4+d*2
            if hi==0xb: s.pr=pc+4
            s.exec_one(pc+2); s.pc=tgt; return
        if hi==0x8:
            sub=n
            d=sx8(i8); tgt=pc+4+d*2
            if sub==0x9 or sub==0xb:  # bt / bf
                take=(s.t==1) if sub==0x9 else (s.t==0)
                s.pc=tgt if take else nxt; return
            if sub==0xd or sub==0xf:  # bt.s / bf.s
                take=(s.t==1) if sub==0xd else (s.t==0)
                s.exec_one(pc+2); s.pc=tgt if take else pc+4; return
            if sub==0x8: s.t=int((r[0]&M32)==(sx8(i8)&M32)); return done()
            if sub==0x0: s.wb(r[m]+(op&15),r[0]); return done()
            if sub==0x1: s.ww(r[m]+(op&15)*2,r[0]); return done()
            if sub==0x4: r[0]=sx8(s.rb(r[m]+(op&15)))&M32; return done()
            if sub==0x5: r[0]=sx16(s.rw(r[m]+(op&15)*2))&M32; return done()
        if hi==0xc:
            sub=n
            if sub==0xb: r[0]|=i8; return done()
            if sub==0x9: r[0]&=i8; return done()
            if sub==0x8: s.t=int((r[0]&i8)==0); return done()
        if hi==0x5: r[n]=s.rl(r[m]+(op&15)*4); return done()
        if hi==0x1: s.wl(r[n]+(op&15)*4,r[m]); return done()
        lo=op&15
        if hi==0x6:
            v=r[m]
            if lo==3: r[n]=v
            elif lo==0: r[n]=sx8(s.rb(v))&M32
            elif lo==1: r[n]=sx16(s.rw(v))&M32
            elif lo==2: r[n]=s.rl(v)
            elif lo==4: r[n]=sx8(s.rb(v))&M32; r[m]=(r[m]+1)&M32 if n!=m else r[n]
            elif lo==5: r[n]=sx16(s.rw(v))&M32; r[m]=(r[m]+2)&M32 if n!=m else r[n]
            elif lo==6: val=s.rl(v); r[m]=(r[m]+4)&M32; r[n]=val
            elif lo==0xc: r[n]=v&0xff
            elif lo==0xd: r[n]=v&0xffff
            elif lo==0xe: r[n]=sx8(v)&M32
            elif lo==0xf: r[n]=sx16(v)&M32
            elif lo==0xb: r[n]=(-v)&M32
            elif lo==0x7: r[n]=(~v)&M32
            elif lo==0x8: r[n]=(v&0xffff0000)|((v&0xff)<<8)|((v>>8)&0xff)
            elif lo==0x9: r[n]=((v>>16)|(v<<16))&M32
            elif lo==0xa: w=-v-s.t; s.t=int(w<0 and (v!=0 or s.t)); r[n]=w&M32
            else: raise Stop(f'op {op:04x} en {pc:08x}')
            return done()
        if hi==0x2:
            if lo==0: s.wb(r[n],r[m])
            elif lo==1: s.ww(r[n],r[m])
            elif lo==2: s.wl(r[n],r[m])
            elif lo==4: r[n]=(r[n]-1)&M32; s.wb(r[n],r[m])
            elif lo==5: r[n]=(r[n]-2)&M32; s.ww(r[n],r[m])
            elif lo==6: r[n]=(r[n]-4)&M32; s.wl(r[n],r[m])
            elif lo==8: s.t=int((r[n]&r[m])==0)
            elif lo==9: r[n]&=r[m]
            elif lo==0xa: r[n]^=r[m]
            elif lo==0xb: r[n]|=r[m]
            elif lo==0xe: s.macl=((r[n]&0xffff)*(r[m]&0xffff))&M32
            elif lo==0xf: s.macl=(sx16(r[n])*sx16(r[m]))&M32
            elif lo==0xd: r[n]=((r[n]>>16)|(r[m]<<16))&M32
            elif lo==0x7: s.q=r[n]>>31; s.m=r[m]>>31; s.t=int(s.q!=s.m)
            else: raise Stop(f'op {op:04x} en {pc:08x}')
            return done()
        if hi==0x3:
            a,b=r[n],r[m]
            if lo==0: s.t=int(a==b)
            elif lo==2: s.t=int(a>=b)
            elif lo==6: s.t=int(a>b)
            elif lo==3: s.t=int(sx32(a)>=sx32(b))
            elif lo==7: s.t=int(sx32(a)>sx32(b))
            elif lo==0xc: r[n]=(a+b)&M32
            elif lo==0xe: v=a+b+s.t; s.t=v>>32; r[n]=v&M32
            elif lo==0x5: p=a*b; s.macl=p&M32; s.mach=(p>>32)&M32
            elif lo==0x4:
                old_q=s.q; s.q=(a>>31)&1; a=((a<<1)|s.t)&M32
                if old_q==s.m:
                    v=a-b; tmp=int(v<0); a=v&M32
                else:
                    v=a+b; tmp=int(v>M32); a=v&M32
                s.q=(s.q^tmp) if old_q==0 else (s.q^(1-tmp)) if False else s.q
                # versión simple: recalcular q según la especificación
                r[n]=a; s.t=int(s.q==s.m)
            elif lo==8: r[n]=(a-b)&M32
            elif lo==0xd:
                p=sx32(a)*sx32(b); s.macl=p&M32; s.mach=(p>>32)&M32
            elif lo==0xa:
                v=a-b-s.t; s.t=int(v<0); r[n]=v&M32
            else: raise Stop(f'op {op:04x} en {pc:08x}')
            return done()
        if hi==0x4:
            low8=op&0xff
            if low8==0x22: r[n]=(r[n]-4)&M32; s.wl(r[n],s.pr)
            elif low8==0x26: s.pr=s.rl(r[n]); r[n]=(r[n]+4)&M32
            elif low8==0x0b: s.pr=pc+4; s.exec_one(pc+2); s.pc=r[n]&M32 if True else 0; return
            elif low8==0x2b: s.exec_one(pc+2); s.pc=r[n]; return
            elif low8==0x08: r[n]=(r[n]<<2)&M32
            elif low8==0x00: s.t=r[n]>>31; r[n]=(r[n]<<1)&M32
            elif low8==0x18: r[n]=(r[n]<<8)&M32
            elif low8==0x28: r[n]=(r[n]<<16)&M32
            elif low8==0x09: r[n]>>=2
            elif low8==0x01: s.t=r[n]&1; r[n]>>=1
            elif low8==0x19: r[n]>>=8
            elif low8==0x29: r[n]>>=16
            elif low8==0x21: s.t=r[n]&1; r[n]=(sx32(r[n])>>1)&M32
            elif low8==0x20: s.t=r[n]>>31; r[n]=(r[n]<<1)&M32
            elif low8==0x15: s.t=int(sx32(r[n])>0)
            elif low8==0x11: s.t=int(sx32(r[n])>=0)
            elif low8==0x10: r[n]=(r[n]-1)&M32; s.t=int(r[n]==0)
            elif low8==0x04: s.t=r[n]>>31; r[n]=((r[n]<<1)|s.t)&M32
            elif low8==0x05: s.t=r[n]&1; r[n]=(r[n]>>1)|(s.t<<31)
            elif low8==0x24: t=s.t; s.t=r[n]>>31; r[n]=((r[n]<<1)|t)&M32
            elif low8==0x25: t=s.t; s.t=r[n]&1; r[n]=(r[n]>>1)|(t<<31)
            else: raise Stop(f'op {op:04x} en {pc:08x}')
            return done()
        if hi==0x0:
            if lo==0xc: r[n]=sx8(s.rb(r[0]+r[m]))&M32
            elif lo==0xd: r[n]=sx16(s.rw(r[0]+r[m]))&M32
            elif lo==0xe: r[n]=s.rl(r[0]+r[m])
            elif lo==4: s.wb(r[0]+r[n],r[m])
            elif lo==5: s.ww(r[0]+r[n],r[m])
            elif lo==6: s.wl(r[0]+r[n],r[m])
            elif lo==7: s.macl=(r[n]*r[m])&M32
            elif (op&0xff)==0x1a: r[n]=s.macl
            elif (op&0xff)==0x0a: r[n]=s.mach
            elif (op&0xff)==0x29: r[n]=s.t
            elif (op&0xff)==0x2a: r[n]=s.pr
            else: raise Stop(f'op {op:04x} en {pc:08x}')
            return done()
        raise Stop(f'op {op:04x} en {pc:08x}')
def sx32(v): v&=M32; return v-(1<<32) if v&0x80000000 else v
