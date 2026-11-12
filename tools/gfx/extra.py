"""Rótulos de la v1.0: bocadillos del gallo-robot, canción de las ranas, carteles de pared y columnas ドレミ.
Los que son una sola pieza se localizan por su contenido original y se sustituyen en todos los SPR que la repiten."""
import struct
import numpy as np
from . import gfxtext as G
from .relabel import Relabel, pixels, VBASE
def _px(img):
    return bytes(((img[:,0::2]<<4)|img[:,1::2]).astype(np.uint8).reshape(-1))
def _unpx(b,w,h):
    d=np.frombuffer(b,np.uint8); return np.stack([d>>4,d&15],1).reshape(h,w)
def _dil(m,r):
    o=m.copy()
    for _ in range(r):
        p=np.pad(o,1); o=p[1:-1,1:-1]|p[:-2,1:-1]|p[2:,1:-1]|p[1:-1,:-2]|p[1:-1,2:]
    return o
def retext(px,text,glyph,erase,bg,fill,out,shade=None,h=16,font="black",sx=1.0,box=None,dil=2,region=None,track=0.3):
    """borra el texto (colores glyph, más los colores erase a su alrededor) pintando bg y escribe text centrado;
    region=(y0,y1,x0,x1) limita el borrado y el centrado a esa zona"""
    px=px.copy(); g=np.isin(px,glyph)
    if region:
        y0,y1,x0,x1=region; z=np.zeros_like(g); z[y0:y1,x0:x1]=True; g&=z
    if g.any():
        m=_dil(g,dil)&np.isin(px,tuple(glyph)+tuple(erase))
        if region: m&=z
        px[m]=bg
        ys,xs=np.nonzero(g); cy,cx=(ys.min()+ys.max()+1)/2,(xs.min()+xs.max()+1)/2
        if region: cy,cx=(y0+y1)/2,(x0+x1)/2
    else: cy,cx=px.shape[0]/2,px.shape[1]/2
    if box: cx,cy=box
    maxw=(region[3]-region[2]) if region else px.shape[1]-2
    m=G.fixed(text,h,font,track=track,sx=sx,ref='A')
    while m.shape[1]+2>maxw and sx>0.5: sx-=0.05; m=G.fixed(text,h,font,track=track,sx=sx,ref='A')
    img=G.colorize(m,fill,out,shade=shade); ih,iw=img.shape
    y=int(round(cy-ih/2)); x=int(round(cx-iw/2)); y=max(0,min(y,px.shape[0]-ih)); x=max(0,min(x,px.shape[1]-iw))
    reg=px[y:y+ih,x:x+iw]; reg[img>0]=img[img>0]
    return px
def _piece(cur,spr,k):
    v=cur(spr+'.BIN'); sp=cur(spr+'_SP.BIN'); R=Relabel(v,sp); w,h,a,_=R.P[k]; off=a*8-VBASE
    return v[off:off+w*h//2],w,h
# canción de las ranas (カエルノウタガ キコエテクルヨ): una sílaba por bocadillo, en romaji
FROGS=[(694,'KA'),(699,'E'),(700,'RU'),(701,'NO'),(702,'U'),(703,'TA'),(704,'GA'),(705,'KI'),(706,'KO'),(707,'TE'),(708,'KU'),(709,'YO')]
def jobs(cur):
    """[(bytes originales, bytes nuevos)] de piezas sueltas"""
    out=[]
    for k,txt in FROGS:
        b,w,h=_piece(cur,'SPR22',k)
        out.append((b,_px(retext(_unpx(b,w,h),txt,(0xc,0xd),(1,0xa),9,0xc,1,shade=0xd,h=17,dil=6))))
    # carteles de pared de la ronda de la mansión: ぢ (chiste de almorranas) y マース
    b,w,h=_piece(cur,'SPR62',695)
    out.append((b,_px(_sign(_unpx(b,w,h),'PILES'))))
    b,w,h=_piece(cur,'SPR62',696)
    out.append((b,_px(_sign2(_unpx(b,w,h),'MARS'))))
    # pintada de los músicos de Bremen (ぶれ〜めんば)
    for k,txt in ((1503,'BREMEN'),(1504,'BAND')):
        b,w,h=_piece(cur,'SPR31',k)
        out.append((b,_px(_chalk(_unpx(b,w,h),txt))))
    # cartel 入る / べからず (ronda de Bremen, noche): tablas de madera; texto en colores 3 y 2
    for k in (1505,1508,1510,1511,1513):
        b,w,h=_piece(cur,'SPR31',k)
        out.append((b,_px(_keepout(_unpx(b,w,h),k))))
    return out
def _inpaint(px,mask):
    px=px.copy(); m=mask.copy()
    for _ in range(20):
        if not m.any(): break
        for dx in (-1,1,-2,2):
            ok=m&~np.roll(m,dx,1); px[ok]=np.roll(px,dx,1)[ok]; m=m&~ok
    return px
def _keepout(px,k):
    px=_inpaint(px,np.isin(px,(2,3)))
    boards={1505:((3,19,4,60),(20,37,4,60),13),1508:((3,19,4,60),(20,37,4,60),13),1510:((2,15,2,46),(15,29,2,46),11)}
    if k not in boards: return px          # trozos del cartel roto: solo se borra el texto
    *bs,hh=boards[k]
    for (y0,y1,x0,x1),t in zip(bs,('KEEP','OUT!')):
        m=G.fixed(t,hh,'black',track=0.5); sx=1.0
        while m.shape[1]+2>x1-x0 and sx>0.5: sx-=0.05; m=G.fixed(t,hh,'black',track=0.5,sx=sx)
        img=G.colorize(m,3,2); ih,iw=img.shape
        y=int(round((y0+y1)/2-ih/2)); x=int(round((x0+x1)/2-iw/2))
        reg=px[y:y+ih,x:x+iw]; reg[img>0]=img[img>0]
    return px
def _sign(px,text):
    return retext(px,text,(0xb,),(7,6,8),1,0xb,7,h=13,region=(9,39,8,40),dil=3,track=0)
def _sign2(px,text):
    return retext(px,text,(0xb,),(7,6,8),4,0xb,7,h=16,region=(4,27,3,38),dil=3,track=0)
def _chalk(px,text,maxh=8):
    """tiza: trazo de 1 px en los colores a/9 sobre transparente"""
    from PIL import Image, ImageDraw, ImageFont
    h,w=px.shape; best=None
    for s in range(8,30):
        f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
        im=Image.new('L',(w*3,h*3),0); ImageDraw.Draw(im).text((2,2),text,font=f,fill=255)
        a=np.array(im)>110; ys,xs=np.nonzero(a); a=a[ys.min():ys.max()+1,xs.min():xs.max()+1]
        if a.shape[1]<=w-2 and a.shape[0]<=min(h-4,maxh): best=a
        else: break
    out=np.zeros_like(px); ih,iw=best.shape; y=(h-ih)//2; x=(w-iw)//2
    yy,xx=np.nonzero(best); out[yy+y,xx+x]=np.where((yy*7+xx*3)%5==0,9,0xa)
    return out
def patch(cur,files):
    out={}
    js=jobs(cur)
    for f in files:
        d=cur(f); nd=bytearray(d); hit=False
        for a,b in js:
            assert len(a)==len(b)
            p=nd.find(a)
            while p>=0:
                nd[p:p+len(a)]=b; hit=True; p=nd.find(a,p+len(a))
        if hit: out[f]=bytes(nd)
    # bocadillos del gallo-robot (ヅーーッ / コケッ / ケッコー / ケコーッ)
    R=Relabel(out.get('SPR42.BIN') or cur('SPR42.BIN'),cur('SPR42_SP.BIN'))
    R.apply(17,{0:'ZZZT!',1:'CLUCK!',2:'BAWK!',3:'BAWK!'},keep=(1794,1795,1796,1797),style=(3,15),height=20,sx=0.9,split_words=False)
    out['SPR42.BIN'],out['SPR42_SP.BIN']=R.result()
    return out
