"""Reescribe rótulos compuestos por piezas de sprite (SPRxx.BIN + SPRxx_SP.BIN).

SP: punteros a objetos -> lista de punteros a frames; frame = n u16, cabecera de 14 bytes y n registros de 16 bytes
(pieza relativa a la base del objeto, 0, 0, ancho, x, 0, y, 0; x,y = centro). Tabla de piezas en 0x160: 8 bytes
(ancho, alto, srca en unidades de 8 bytes de VRAM VDP1, tamaño (ancho/8)<<8|alto); el SPR se carga en VRAM 0x10FE0.
Las piezas que solo usan los frames reescritos se liberan y su VRAM se reparte entre las tiras del texto inglés."""
import struct, collections
import numpy as np
from . import gfxtext as G
B0=0x608f000; PT=0x160; VBASE=0x10fe0
def parts(t):
    out=[]; k=0
    while PT+8*k+8<=len(t):
        w,h,a,sz=struct.unpack('>HHHH',t[PT+8*k:PT+8*k+8])
        if w==0 or h==0 or (sz>>8)*8!=w or (sz&0xff)!=h: break
        out.append((w,h,a,sz)); k+=1
    return out
def load_base(t):
    """dirección de RAM donde se carga el SP (casi siempre 0x0608F000)"""
    ptr=[]; o=0
    while 0x6080000<=struct.unpack('>I',t[o:o+4])[0]<0x60c0000: ptr.append(struct.unpack('>I',t[o:o+4])[0]); o+=4
    def score(X):
        n=0
        for p in set(ptr):
            q=p-X
            if 0<=q<=len(t)-4 and X<=struct.unpack('>I',t[q:q+4])[0]<X+len(t): n+=1
        return n
    return max(range(0x6080000,0x6091000,0x1000),key=lambda X:(score(X),X==B0))
def objects(t,B=None):
    B0_=B or load_base(t)
    ptr=[]; o=0
    while 0x6080000<=struct.unpack('>I',t[o:o+4])[0]<0x60c0000: ptr.append(struct.unpack('>I',t[o:o+4])[0]); o+=4
    res={}
    for k,p in enumerate(ptr):
        q=p-B0_; fr=[]
        while 0<=q and q+4<=len(t):
            a=struct.unpack('>I',t[q:q+4])[0]
            if not (B0_<=a<B0_+len(t)): break
            f=a-B0_; n=struct.unpack('>H',t[f:f+2])[0]
            if n>64: break
            fr.append(f); q+=4
        res[k]=fr
    return res
def records(t,f):
    n=struct.unpack('>H',t[f:f+2])[0]
    return [struct.unpack('>HHHHhHhH',t[f+16+16*j:f+32+16*j]) for j in range(n)]
def base_of(t,P,fr):
    ps=[r for f in fr for r in records(t,f)]
    c=[b for b in range(len(P)) if all(b+r[0]<len(P) and P[b+r[0]][0]==r[3] for r in ps)]
    return c
def pixels(v,P,k):
    w,h,a,_=P[k]; off=a*8-VBASE; d=np.frombuffer(v[off:off+w*h//2],np.uint8)
    return np.stack([d>>4,d&15],1).reshape(h,w)
def colors(v,P,ks):
    edge=collections.Counter(); inner=collections.Counter()
    for k in ks:
        px=pixels(v,P,k); z=np.pad(px==0,1,constant_values=True)
        near=z[:-2,1:-1]|z[2:,1:-1]|z[1:-1,:-2]|z[1:-1,2:]
        edge.update(px[(px>0)&near].tolist()); inner.update(px[(px>0)&~near].tolist())
    out=edge.most_common(1)[0][0]; fill=[c for c,_ in inner.most_common() if c!=out][0]
    return fill,out
class Relabel:
    def __init__(s,spr,sp):
        s.v=bytearray(spr); s.t=bytearray(sp); s.P=parts(s.t); s.O=objects(s.t)
        s.bases={}
        for k,fr in s.O.items():
            c=base_of(s.t,s.P,fr) if fr else []
            if len(c)==1: s.bases[k]=c[0]
    def used_elsewhere(s,targets):
        used=set()
        for k,fr in s.O.items():
            if k not in s.bases: continue
            for fi,f in enumerate(fr):
                if (k,fi) in targets: continue
                used.update(s.bases[k]+r[0] for r in records(s.t,f))
        return used
    def apply(s,obj,texts,keep=(),style=None,height=None,maxw=64,align='center',gap=2,font='black',sx=1.0,track=0.3,split_words=True,ref='AgjpqyQ|'):
        """texts {frame: texto}; keep = piezas globales que se conservan (p.ej. una flecha)"""
        base=s.bases[obj]; fr=s.O[obj]; targets={(obj,fi) for fi in texts}
        old={fi:records(s.t,fr[fi]) for fi in texts}
        mine={base+r[0] for rs in old.values() for r in rs}
        pool=sorted(mine-set(keep)-s.used_elsewhere(targets)-{base+r[0] for k2 in () for r in ()})
        # VRAM libre: rangos de las piezas liberadas
        rng=sorted({(s.P[k][2]*8, s.P[k][2]*8+s.P[k][0]*s.P[k][1]//2) for k in pool})
        free=[]
        for a,b in rng:
            if free and a<=free[-1][1]: free[-1][1]=max(free[-1][1],b)
            else: free.append([a,b])
        fstyle={fi:(style or colors(s.v,s.P,[base+r[0] for r in old[fi] if base+r[0] not in keep])) for fi in texts}
        for a,b in free: s.v[a-VBASE:b-VBASE]=bytes(b-a)
        s.last_pool=(len(pool),sum(b-a for a,b in free),[(hex(a),b-a) for a,b in free])
        partfree=list(pool); cache={}
        for fi,text in texts.items():
            rs=old[fi]; f=fr[fi]; slots=len(rs)
            kept=[r for r in rs if base+r[0] in keep]
            boxes=[(r[4]-s.P[base+r[0]][0]//2, r[6]-s.P[base+r[0]][1]//2, s.P[base+r[0]][0], s.P[base+r[0]][1]) for r in rs if base+r[0] not in keep]
            x0=min(b[0] for b in boxes); y0=min(b[1] for b in boxes); x1=max(b[0]+b[2] for b in boxes); y1=max(b[1]+b[3] for b in boxes)
            fill,out=fstyle[fi]
            opt=dict(text=text) if not isinstance(text,dict) else dict(text)
            text=opt['text']; H=opt.get('h',height or (y1-y0)); maxw_t=opt.get('w',None); sx_t=opt.get('sx',sx)
            while True:
                if isinstance(text,np.ndarray): words=[(None,text)]
                else:
                    toks=text.split(' ') if split_words else [text]
                    words=[(wd,G.colorize(G.fixed(wd,H,font,track=track,sx=sx_t,ref=opt.get('ref',ref)),fill,out)) for wd in toks]
                sp_w=max(3,H//4)
                w=sum(im.shape[1] for _,im in words)+sp_w*(len(words)-1)
                if not maxw_t or w<=maxw_t or sx_t<0.5: break
                sx_t-=0.05
            if align=='left': left=x0
            elif align=='after' and kept:
                left=max(kr[4]+s.P[base+kr[0]][0]//2 for kr in kept)+gap
            else: left=(x0+x1)//2-w//2
            cy=(y0+y1)//2 if not (align=='after' and kept) else round(sum(r[6] for r in kept)/len(kept))
            new=list(kept); x=left
            for wd,img in words:
                key=(wd,img.shape,fill,out)
                if wd is None or key not in cache:
                    h,ww=img.shape; h2=h+(h&1); W=(ww+7)//8*8; a=np.zeros((h2,W),np.uint8); a[:h,:ww]=img
                    pcs=[]
                    for xs in range(0,W,maxw):
                        pw=min(maxw,W-xs); piece=a[:,xs:xs+pw]
                        if not piece.any(): continue
                        n=pw*h2//2
                        for fr_ in free:
                            st=(fr_[0]+7)//8*8
                            if st+n<=fr_[1]: break
                        else: raise ValueError(f'sin VRAM para "{text}"')
                        fr_[0]=st+n
                        k=partfree.pop(0)
                        s.v[st-VBASE:st-VBASE+n]=bytes(((piece[:,0::2]<<4)|piece[:,1::2]).astype(np.uint8).reshape(-1))
                        s.t[PT+8*k:PT+8*k+8]=struct.pack('>HHHH',pw,h2,st//8,(pw//8)<<8|h2)
                        s.P[k]=(pw,h2,st//8,(pw//8)<<8|h2)
                        pcs.append((k,pw,xs))
                    cache[key]=pcs
                for k,pw,xs in cache[key]:
                    new.append((k-base,0,0,pw,x+xs+pw//2,0,cy,0))
                x+=img.shape[1]+sp_w
            if len(new)>slots: raise ValueError(f'"{text}": {len(new)} piezas > {slots} huecos')
            s.t[f:f+2]=struct.pack('>H',len(new))
            for j in range(slots):
                s.t[f+16+16*j:f+32+16*j]=struct.pack('>HHHHhHhH',*new[j]) if j<len(new) else bytes(16)
        return sum(b-a for a,b in free)
    def result(s): return bytes(s.v),bytes(s.t)
    def redraw(s,k,img,bg=0):
        """redibuja una pieza en su sitio (mismo tamaño) con img centrada sobre un fondo de color bg"""
        w,h,a,_=s.P[k]; c=np.full((h,w),bg,np.uint8); ih,iw=img.shape
        assert ih<=h and iw<=w,(img.shape,(h,w))
        y=(h-ih)//2; x=(w-iw)//2; reg=c[y:y+ih,x:x+iw]; reg[img>0]=img[img>0]
        off=a*8-VBASE; s.v[off:off+w*h//2]=bytes(((c[:,0::2]<<4)|c[:,1::2]).astype(np.uint8).reshape(-1))
    def text(s,txt,maxw,maxh,fill,out,font='black',sx=1.0,track=0.3,shade=None):
        return G.colorize(G.fit(txt,maxw,maxh,font,track=track,sx=sx),fill,out,shade=shade)
