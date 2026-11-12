"""Genera glifos estrechos (avance 8 px) con el estilo del juego: relleno 1, contorno y sombra 4."""
import gzip,io,os
from PIL import PcfFontFile, ImageFont, Image, ImageDraw
HERE=os.path.dirname(os.path.abspath(__file__))
PIL_FONT=os.path.join(HERE,'6x13B.pil')
if not os.path.exists(PIL_FONT):
    PcfFontFile.PcfFontFile(io.BytesIO(gzip.open('/usr/share/fonts/X11/misc/6x13B.pcf.gz').read())).save(PIL_FONT[:-4])
FNT=ImageFont.load(PIL_FONT)
# código del juego -> carácter
SLOTS={}
for i,c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!?."): SLOTS[0xA1+i]=c
for code,c in {0x01:' ',0x02:',',0x03:"'",0x04:'-',0x05:'"',0x06:':',0x07:'(',0x08:')',0x09:'&',0x0A:'~',0x0B:'/'}.items(): SLOTS[code]=c
CHAR2CODE={c:k for k,c in SLOTS.items()}
# Glifos de dos letras para rutinas que siguen avanzando 16 px (elección HEAR/SKIP)
for code,c in {0x0C:'HE',0x0D:'AR',0x0E:'NO'}.items(): SLOTS[code]=c
# Más glifos de dos letras para el menú del título (avance 16 px)
_PAIRS=[' G','AM','E ','ST','AR','T ','OP','TI','ON',' L','EV','EL',' S','UP','ER',' E','AS','Y ','SU','PE','R ','RM','AL','HA','RD','SK','IP',
        # categorías de la tasación final (A_R9S5)
        'MA','NG','A ','FI','SH','TO','YS','CA','ME','RA','PO','TS',' A','RT','OL','D ','RS',' O','LD','RO','YA','L ','DO','LL','S ','MU','SI','C ','BO','NU']
for k,c in enumerate(_PAIRS): SLOTS[0x0F+k]=c
PAIR2CODE={c:k for k,c in SLOTS.items() if len(c)==2}
PAIR2CODE['  ']=0x01
def glyph(c, dx=1, dy=2):
    m=Image.new('1',(16,16),0)
    for k,ch in enumerate(c): ImageDraw.Draw(m).text((dx+8*k,dy),ch,font=FNT,fill=1)
    fill=[[m.getpixel((x,y)) for x in range(16)] for y in range(16)]
    px=[[0]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            if fill[y][x]:
                for yy in range(y-1,y+3):
                    for xx in range(x-1,x+3):
                        # contorno de 1 px + sombra 1 px abajo/derecha
                        if 0<=yy<16 and 0<=xx<16 and (yy<=y+1 and xx<=x+1 or (yy==y+2 and xx>=x) or (xx==x+2 and yy>=y)):
                            if not fill[yy][xx]: px[yy][xx]=4
    for y in range(16):
        for x in range(16):
            if fill[y][x]: px[y][x]=1
    out=bytearray(128)
    for y in range(16):
        for x in range(0,16,2): out[y*8+x//2]=(px[y][x]<<4)|px[y][x+1]
    return bytes(out)
def patch_font(data, base):
    b=bytearray(data)
    for code,c in SLOTS.items():
        o=base+(code-1)*0x80
        b[o:o+0x80]=glyph(c)
    return bytes(b)
FONT_COPIES={'SPR0.BIN':0x5f60,'SPR0K.BIN':0x5f60,'SPR01.BIN':0x1e9c0,'SPR10.BIN':0x28bc0,'SPR8.BIN':0x28060,'SPR85.BIN':0x26be0,'SPR9.BIN':0x11da0}
