"""Extrae / reinserta el guion de Super Tempo (codificación de 16 bits, punteros absolutos 0x0606xxxx)."""
import struct,json
BASE=0x06060000
ROWS=["あいうえおかきくけこさしすせそた","ちつてとなにぬねのはひふへほまみ","むめもやゆよらりるれろわをんがぎ","ぐげござじずぜぞだぢづでどばびぶ","べぼぱぴぷぺぽぁぃぅぇぉゃゅょっ",
"アイウエオカキクケコサシスセソタ","チツテトナニヌネノハヒフヘホマミ","ムメモヤユヨラリルレロワヲンガギ","グゲゴザジズゼゾダヂヅデドバビブ","ベボパピプペポァィゥェォャュョッ",
"ABCDEFGHIJKLMNOP","QRSTUVWXYZabcdef","ghijklmnopqrstuv","wxyz0123456789!?",".、。「」ー～"]
TABLE="".join(ROWS)
CTRL={0xef:'{n}',0xee:'{w}',0xf0:'{e}',0xf1:'{f1}'}
def decode(ws):
    o=''
    for x in ws:
        if x in CTRL: o+=CTRL[x]
        elif 1<=x<=len(TABLE): o+=TABLE[x-1]
        else: o+='{%02x}'%x
    return o
REGIONS={'A_R0S0.BIN':[(0x1f180,0x1f1dc)],'A_R0S1.BIN':[(0x1cc04,0x1e4c4)],
         'A_R4S5.BIN':[(0x239a4,0x23c62)],'A_R9S2.BIN':[(0x24e04,0x25ca6)],'A_R9S5.BIN':[(0x2a704,0x2a97c),(0x2a9b6,0x2b028),(0x2a97c,0x2a9b6)]}
def find_ptrs(b,regs):
    out=[]
    for o in range(0,len(b)-3,2):
        v=struct.unpack('>I',b[o:o+4])[0]-BASE
        for ri,(s,e) in enumerate(regs):
            if s<=v<e: out.append((o,v,ri))
    return out
def extract(fdir):
    res={}
    for f,regs in REGIONS.items():
        b=open(f'{fdir}/{f}','rb').read()
        ptrs=find_ptrs(b,regs)
        msgs=[]
        for ri,(s,e) in enumerate(regs):
            targets=sorted(set([s]+[v for o,v,r in ptrs if r==ri]))
            for k,t in enumerate(targets):
                end=targets[k+1] if k+1<len(targets) else e
                ws=struct.unpack('>%dH'%((end-t)//2),b[t:end])
                msgs.append({'id':f'{f}:{t:05x}','region':ri,'off':t,'ja':decode(ws),
                             'ptrs':[o for o,v,r in ptrs if v==t and r==ri]})
        res[f]=msgs
    return res

def insert(fdir, msgs_by_file, encode=None):
    """msgs_by_file: salida de extract() con 'data' (bytes ya codificados) y 'align' (1 o 2) en cada mensaje.
    Reescribe cada región en orden y actualiza punteros. Devuelve {fichero: bytes}."""
    out={}
    for f,msgs in msgs_by_file.items():
        b=bytearray(open(f'{fdir}/{f}','rb').read())
        regs=REGIONS[f]
        for ri,(s,e) in enumerate(regs):
            b[s:e]=b'\0'*(e-s)
            pos=s
            for m in [m for m in msgs if m['region']==ri]:
                if m.get('align',2)==2 and pos%2: pos+=1
                data=m['data']
                if pos+len(data)>e: raise ValueError(f'{f}: región {ri} llena en {m["id"]} (faltan {pos+len(data)-e} bytes)')
                b[pos:pos+len(data)]=data
                for p in m['ptrs']: b[p:p+4]=struct.pack('>I',BASE+pos)
                pos+=len(data)
            m_free=e-pos
            print(f'{f} región {ri}: {m_free} bytes libres')
        out[f]=bytes(b)
    return out
