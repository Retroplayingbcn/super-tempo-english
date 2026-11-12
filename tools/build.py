"""Construye la versión inglesa: texto + avance de 8 px + fuente estrecha -> pista 1 nueva."""
import sys,os,re,struct,shutil,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import script,cdbuild,font8,gfx,subs
MAXLEN=32
CTRL_TOK={'{n}':0xef,'{w}':0xee,'{e}':0xf0,'{f1}':0xf1}
def encode(s):
    out=[]
    for tok in re.findall(r'\{[^}]+\}|.',s,re.S):
        if tok in CTRL_TOK: out.append(CTRL_TOK[tok])
        elif tok.startswith('{['): out.append(font8.PAIR2CODE[tok[2:-2]])
        elif tok.startswith('{'): out.append(int(tok[1:-1],16))
        elif tok in font8.CHAR2CODE: out.append(font8.CHAR2CODE[tok])
        else: raise ValueError(f'carácter sin glifo: {tok!r} en {s!r}')
    return out
def suffix(ja):
    m=re.search(r'((?:\{(?:n|w|e)\})+)$',ja); return m.group(1) if m else ''
def load_en(path):
    en={}
    for line in open(path,encoding='utf-8'):
        if line.startswith('#') or not line.strip(): continue
        key,_,txt=line.rstrip('\n').partition('\t')
        f,i=key.split(); en[(f+'.BIN',int(i) if i.isdigit() else i)]=txt
    return en
# Parches de código: avance horizontal del texto 16 px -> 8 px
# Rutina de diálogo (A_R0S1 0x06060e10; misma rutina en A_R4S5 en 0x060727e8):
# lectura de 16 bits -> 8 bits y avance de 16 px -> 8 px.
DIALOG=[(0x2e,0x6191,0x6190,2),   # mov.w @r9,r1        -> mov.b
        (0x36,0x300c,0x0009,2),   # add r0,r0           -> nop
        (0x38,0x019d,0x019c,2),   # mov.w @(r0,r9),r1   -> mov.b
        (0x3a,0x611d,0x611c,2),   # extu.w r1,r1        -> extu.b
        (0x56,0x300c,0x0009,2),
        (0x58,0x079d,0x079c,2),   # mov.w @(r0,r9),r7   -> mov.b
        (0x66,0x677d,0x677c,2),   # extu.w r7,r7        -> extu.b
        (0xbc,0x300c,0x0009,2),
        (0xbe,0x019d,0x019c,2),
        (0xc2,0x611d,0x611c,2),
        (0x154,0xff11,0x0011,2),  # constante para detectar 0xEF/0xF0 con signo extendido
        (0x168,0x00100000,0x00080000,4)]  # avance X 16.0 -> 8.0
CODE_PATCHES={
  'A_R0S1.BIN':[(0xe10+o,a,b,n) for o,a,b,n in DIALOG]+[
     # Elección きく/きかない (escuchar la explicación) -> HEAR / SKIP (glifos de dos letras)
     (0x19ec,0xe707,0xe70c,2),(0x19f4,0xe108,0xe10d,2),(0x1a14,0x2171,0x2131,2),
     (0x1a1a,0xe106,0xe128,2),(0x1a22,0xe115,0xe129,2),(0x1a2a,0xe102,0xe101,2)],
  'A_R4S5.BIN':[(0x127e8+o,a,b,n) for o,a,b,n in DIALOG],
  'A_R9S5.BIN':[(0x12afe,0x6101,0x6100,2),(0x12b08,0x311c,0x0009,2),(0x12b0a,0x011d,0x011c,2),
                (0x12b0c,0x611d,0x611c,2),(0x12b40,0x311c,0x0009,2),(0x12b42,0x061d,0x061c,2),
                (0x12b50,0x676d,0x676c,2),(0x12c2c,0xff11,0x0011,2),
                (0x12b56,0x4508,0x4500,2),    # shll2 r5 -> shll r5 (avance 8 px)
                # rutina de dibujo inmediato 0x060729b8 ("Hmm! This is...!!" y notas de tasación)
                (0x12a14,0x6101,0x6100,2),(0x12a1e,0x311c,0x0009,2),(0x12a20,0x011d,0x011c,2),
                (0x12a22,0x611d,0x611c,2),(0x12a36,0x311c,0x0009,2),(0x12a38,0x011d,0x011c,2),
                (0x12a3a,0x671d,0x671c,2),(0x12a8c,0x00100000,0x00080000,4)],
}
R9S5_TYPE=[(0x12afe,0x6101,0x6100,2),(0x12b08,0x311c,0x0009,2),(0x12b0a,0x011d,0x011c,2),
           (0x12b0c,0x611d,0x611c,2),(0x12b40,0x311c,0x0009,2),(0x12b42,0x061d,0x061c,2),
           (0x12b50,0x676d,0x676c,2),(0x12c2c,0xff11,0x0011,2),(0x12b56,0x4508,0x4500,2)]
# Final (A_R9S2): la rutina de máquina de escribir es la de A_R9S5 desplazada 0x74 bytes
CODE_PATCHES['A_R9S2.BIN']=[(o+0x74,a,b,n) for o,a,b,n in R9S5_TYPE]+[
    # dibujo inmediato 0x06072a14 (carta, selector de ronda, "THE END" y créditos)
    (0x12a70,0x61d1,0x61d0,2),(0x12a78,0x300c,0x0009,2),(0x12a7a,0x01dd,0x01dc,2),(0x12a7c,0x611d,0x611c,2),
    (0x12a8c,0x300c,0x0009,2),(0x12a8e,0x01dd,0x01dc,2),(0x12aa2,0x300c,0x0009,2),(0x12aa4,0x01dd,0x01dc,2),
    (0x12aa6,0x671d,0x671c,2),
    (0x12af4,0x00008000,0x00000000,4),   # bit 0x8000 (coma bajada 11 px): ya no existe en 8 bits
    (0x12b00,0x00100000,0x00080000,4),
    # rótulos del 長者番付 0x06073488 (código + 0x1000)
    (0x134e4,0x6101,0x6100,2),(0x134ee,0x311c,0x0009,2),(0x134f0,0x011d,0x011c,2),(0x134f2,0x611d,0x611c,2),
    (0x13506,0x311c,0x0009,2),(0x13508,0x031d,0x031c,2),(0x1350a,0x623d,0x623c,2),
    (0x1351a,0x313c,0x312c,2),           # add r3,r1 -> add r2,r1 (código sin signo)
    (0x13570,0x00100000,0x00080000,4)]
# Tiendas: registros fijos, código = índice de fuente (código de diálogo - 1), terminador 0xFF.
# La rutina pinta un carácter por fotograma en X = contador*20+16.
def _shop(read):
    return [(read,0x311c,0x0009,2),(read+4,0x012d,0x012c,2),(read+6,0x691d,0x691c,2)]
CODE_PATCHES['A_R8S5.BIN']=_shop(0x1530e)+[(0x153a8,0xe114,0xe108,2)]
CODE_PATCHES['A_R8S6.BIN']=_shop(0x13ba2)+[(0x13c08,0xe114,0xe108,2)]
SHOP_TABLES={'A_R8S5.BIN':{'A':(0x2a6c4,34,6),'B':(0x2a790,30,7)},
             'A_R8S6.BIN':{'A':(0x263d0,40,3),'B':(0x26448,30,7)}}
def shop_patch(fdir,f,en):
    b=bytearray(open(f'{fdir}/{f}','rb').read()); problems=[]
    for t,(off,size,n) in SHOP_TABLES[f].items():
        for i in range(n):
            txt=en.get((f,f'{t}{i}'))
            if txt is None: problems.append(f'falta {f} {t}{i}'); continue
            codes=[c-1 for c in encode(txt)]+[0xff]
            if len(codes)>size: problems.append(f'{f} {t}{i}: demasiado largo'); continue
            b[off+i*size:off+(i+1)*size]=bytes(codes)+b'\0'*(size-len(codes))
    return bytes(b),problems
# Mensajes que siguen en 16 bits (los leen otras rutinas)
WORD16={('A_R0S0.BIN',i) for i in range(6)}|{('A_R9S5.BIN',i) for i in range(62,78)}
def build(fdir, en_path, src_dir, out_dir, iso_path):
    msgs=script.extract(fdir); en=load_en(en_path); problems=[]
    for f,ms in msgs.items():
        for i,m in enumerate(ms):
            t=en.get((f,i))
            if t is None: problems.append(f'falta {f} {i}'); t=m['ja']; full=t
            elif t.startswith('='): full=t[1:]
            else: full=t+suffix(m['ja'])
            for part in re.split(r'\{(?:w|e)\}',full):
                visible=re.sub(r'\{f1\}','',part); visible=re.sub(r'\{[^}]+\}','#',visible)
                if len(visible)>MAXLEN: problems.append(f'{f} {i}: {len(visible)} caracteres: {part}')
            codes=encode(full)
            if (f,i) in WORD16: m['data']=struct.pack('>%dH'%len(codes),*codes); m['align']=2
            else: m['data']=bytes(codes); m['align']=1
    new=script.insert(fdir,msgs)
    for f in SHOP_TABLES:
        new[f],p=shop_patch(fdir,f,en); problems+=p
    for f,patches in CODE_PATCHES.items():
        b=bytearray(new[f])
        for off,old,val,size in patches:
            fmt='>I' if size==4 else '>H'
            assert struct.unpack(fmt,b[off:off+size])[0]==old,(f,hex(off))
            b[off:off+size]=struct.pack(fmt,val)
        new[f]=bytes(b)
    # rótulos de la rutina inmediata (historia inicial A_R9S1 y tarjeta de la Techno Mask)
    new.update(subs.patch(lambda f: new[f] if f in new else open(f'{fdir}/{f}','rb').read(),encode))
    for f,base in font8.FONT_COPIES.items():
        new[f]=font8.patch_font(open(f'{fdir}/{f}','rb').read(),base)
    # rótulos gráficos (sprites)
    def get(f):
        if f is None: return os.listdir(fdir)
        return new[f] if f in new else open(f'{fdir}/{f}','rb').read()
    new.update(gfx.patch_all(get))
    idx=cdbuild.iso_index_from(iso_path)
    os.makedirs(out_dir,exist_ok=True)
    if os.environ.get('DUMP'):
        os.makedirs(f'{out_dir}/files',exist_ok=True)
        for f,d in new.items(): open(f'{out_dir}/files/{f}','wb').write(d)
    name='Super Tempo (English)'
    cdbuild.patch_track(f'{src_dir}/Super Tempo (Japan) (Track 1).bin',f'{out_dir}/{name} (Track 1).bin',idx,new)
    for t in (2,3): shutil.copy(f'{src_dir}/Super Tempo (Japan) (Track {t}).bin',f'{out_dir}/{name} (Track {t}).bin')
    cue=open(f'{src_dir}/Super Tempo (Japan).cue').read().replace('Super Tempo (Japan)',name)
    open(f'{out_dir}/{name}.cue','w').write(cue)
    return problems
if __name__=='__main__':
    p=build(*sys.argv[1:6])
    print('\n'.join(p) if p else 'sin avisos')
