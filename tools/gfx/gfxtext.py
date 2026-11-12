"""Rótulos ingleses para sprites 4bpp: texto con relleno, sombra y contorno de 1 px."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
FONTS={'black':'/usr/share/fonts/opentype/inter/Inter-Black.otf',
       'xbold':'/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf',
       'bold':'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'}
def mask(text,size,font='black',track=0,sx=1.0):
    f=ImageFont.truetype(FONTS[font],size*4)
    chars=[]; 
    for ch in text:
        im=Image.new('L',(size*8,size*6),0); d=ImageDraw.Draw(im); d.text((size,size),ch,font=f,fill=255)
        a=np.array(im); chars.append((ch,a,f.getlength(ch)))
    W=int(sum(l for _,_,l in chars)+track*4*len(text))+size*4; H=size*6
    big=np.zeros((H,W+size*8),np.uint8); x=0
    for ch,a,l in chars:
        big[:, x:x+a.shape[1]]=np.maximum(big[:, x:x+a.shape[1]],a); x+=int(l+track*4)
    ys,xs=np.nonzero(big>100); big=big[ys.min():ys.max()+1, xs.min():xs.max()+1]
    h,w=big.shape
    im=Image.fromarray(big).resize((max(1,round(w/4*sx)),max(1,round(h/4))),Image.LANCZOS)
    return np.array(im)>110
def fit(text,maxw,maxh,font='black',track=0,sx=1.0):
    """mayor tamaño cuyo relleno (sin contorno) cabe en maxw-2 x maxh-2"""
    best=None
    for s in range(6,60):
        m=mask(text,s,font,track,sx)
        if m.shape[1]<=maxw-2 and m.shape[0]<=maxh-2: best=m
        elif best is not None: break
    return best
def colorize(m,fill,outline,shade=None,hi=None):
    h,w=m.shape; M=np.zeros((h+2,w+2),bool); M[1:-1,1:-1]=m
    out=np.zeros(M.shape,np.uint8)
    dil=M.copy()
    for dy in (-1,0,1):
        for dx in (-1,0,1): dil|=np.roll(np.roll(M,dy,0),dx,1)
    out[dil]=outline; out[M]=fill
    if shade is not None:
        below=np.roll(M,-1,0); right=np.roll(M,-1,1)
        out[M&~(below)]=shade; out[M&~right&below]=shade if False else out[M&~right&below]
    if hi is not None:
        above=np.roll(M,1,0); out[M&~above]=hi
    return out
def blit(canvas,img,x,y,center_w=None):
    h,w=img.shape
    if center_w: x+= (center_w-w)//2
    reg=canvas[y:y+h,x:x+w]; reg[img>0]=img[img>0]
def _render(text,size,font,track,sx,ref='ÁgjpqyQ|'):
    f=ImageFont.truetype(FONTS[font],size*4)
    W=int(f.getlength(text)+track*4*len(text))+size*8; H=size*8
    im=Image.new('L',(W,H),0); d=ImageDraw.Draw(im); x=size*2
    for ch in text: d.text((x,size*2),ch,font=f,fill=255); x+=f.getlength(ch)+track*4
    r=Image.new('L',(int(f.getlength(ref))+size*8,H),0); ImageDraw.Draw(r).text((size*2,size*2),ref,font=f,fill=255)
    ys=np.nonzero(np.array(r).max(1)>100)[0]; top,bot=ys.min(),ys.max()+1
    a=np.array(im)[top:bot]; xs=np.nonzero(a.max(0)>100)[0]
    a=a[:,xs.min():xs.max()+1] if len(xs) else a[:,:4]
    h,w=a.shape
    return np.array(Image.fromarray(a).resize((max(1,round(w/4*sx)),max(1,round(h/4))),Image.LANCZOS))>110
def fixed(text,maxh,font='black',track=0,sx=1.0,ref='ÁgjpqyQ|'):
    """como fit, pero con el mismo tamaño y línea base para cualquier texto (alto fijo = maxh-2)"""
    best=None
    for s in range(6,80):
        if _render('A',s,font,track,sx,ref).shape[0]<=maxh-2: best=s
        else: break
    return _render(text,best,font,track,sx,ref)
