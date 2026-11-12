import struct,os
F='/root/st/files/'; BASE=0x10fe0
def entries(spr,sp):
    v=open(F+spr,'rb').read(); t=open(F+sp,'rb').read()
    o=0
    while o+4<=len(t) and 0x6080000<=struct.unpack('>I',t[o:o+4])[0]<0x60c0000: o+=4
    o+=4; out=[]; i=0
    while o+8<=len(t):
        a,sz,cx,cy=struct.unpack('>HHHH',t[o:o+8]); w=(sz>>8)*8; h=sz&0xff; off=a*8-BASE
        if not (w and h) or (a>>8) in (0x06,) and cx<0x100 and sz>0x8000: break
        if 0<=off and off+w*h//2<=len(v): out.append((i,o,off,w,h,cx,cy))
        o+=8; i+=1
    return out,v
def pairs():
    res=[]
    for f in sorted(os.listdir(F)):
        if f.startswith('SPR') and 'SP' not in f[3:]:
            for sp in (f[:-4]+'_SP.BIN',f[:-4]+'SP.BIN'):
                if os.path.exists(F+sp): res.append((f,sp)); break
    return res
if __name__=='__main__':
    for f,sp in pairs():
        e,v=entries(f,sp); print(f,sp,len(e),'entradas', 'fin', hex(e[-1][1]+8) if e else '-', len(open(F+sp,'rb').read()))
