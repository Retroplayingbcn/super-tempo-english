"""Pistas del pájaro en el jefe 1 (SPR23, objeto 44): el texto japonés son 24 piezas de 16x16, una por carácter,
colocadas por dos frames. Se redibujan como tiras de 32x16 con la fuente estrecha y se reescriben los frames."""
import struct,os,sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from font8 import FNT
HINTS=["Beat the tadpoles!","Turn into Muscle Tempo, tweet!"]
OBJ=44; BASE=1993; NPARTS=24; PIECE_W=32; VBASE=0x10fe0; PT=0x160
def strip(text):
    """texto -> matriz de índices (relleno 2, contorno 1, sombra 3) de alto 16"""
    w=6*len(text)+4; m=Image.new('1',(w,16),0); ImageDraw.Draw(m).text((2,1),text,font=FNT,fill=1)
    f=np.array(m,bool); out=np.zeros(f.shape,np.uint8)
    for dy in (-1,0,1,2):
        for dx in (-1,0,1,2):
            if (dy==2 or dx==2) and not (dy>=0 and dx>=0): continue
            s=np.roll(np.roll(f,dy,0),dx,1); out[s&~f]=1
    out[f]=2
    below=np.roll(f,-1,0); out[f&~below]=3
    W=(out.shape[1]+PIECE_W-1)//PIECE_W*PIECE_W; o=np.zeros((16,W),np.uint8); o[:,:out.shape[1]]=out
    return o
def pack(a): return bytes(((a[:,0::2]<<4)|a[:,1::2]).astype(np.uint8).reshape(-1))
def patch(spr,sp,hints=HINTS):
    spr=bytearray(spr); sp=bytearray(sp)
    w0,h0,a0,_=struct.unpack('>HHHH',sp[PT+8*BASE:PT+8*BASE+8])
    off0=a0*8-VBASE; area=NPARTS*128
    assert all(struct.unpack('>H',sp[PT+8*(BASE+k)+4:PT+8*(BASE+k)+6])[0]==a0+16*k for k in range(NPARTS))
    spr[off0:off0+area]=bytes(area)
    B=0x608f000; po=struct.unpack('>I',sp[4*OBJ:4*OBJ+4])[0]-B
    part=0; vpos=0
    for fi,text in enumerate(hints):
        s=strip(text); n=s.shape[1]//PIECE_W
        f=struct.unpack('>I',sp[po+4*fi:po+4*fi+4])[0]-B
        slots=struct.unpack('>H',sp[f:f+2])[0]; assert n<=slots,(text,n,slots)
        sp[f:f+2]=struct.pack('>H',n)
        for j in range(slots): sp[f+16+16*j:f+32+16*j]=bytes(16)
        for j in range(n):
            a=s[:,j*PIECE_W:(j+1)*PIECE_W]; data=pack(a); k=BASE+part
            assert vpos+len(data)<=area,'no cabe'
            spr[off0+vpos:off0+vpos+len(data)]=data
            sp[PT+8*k:PT+8*k+8]=struct.pack('>HHHH',PIECE_W,16,a0+vpos//8,(PIECE_W//8)<<8|16)
            x=-s.shape[1]//2+PIECE_W*j+PIECE_W//2
            sp[f+16+16*j:f+32+16*j]=struct.pack('>HHHHhHhH',part,0,0,PIECE_W,x,0,-8,0)
            part+=1; vpos+=len(data)
    assert part<=NPARTS
    return bytes(spr),bytes(sp)
