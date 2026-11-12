"""Rótulos dibujados con la rutina "inmediata" de 16 bits (no pasan por la tabla de mensajes):
- A_R9S1: subtítulos de la historia inicial (escena 9,1), una función por rótulo (tabla en 0x06074d84).
- A_R4S5: tarjeta negra antes de la Techno Mask (ブオポスのへやのなかで / テンポとケイティはおやつのじかん).
Las funciones originales montan el texto en la pila con instrucciones mov #imm; aquí se reescriben enteras
para que pasen un puntero a una cadena inglesa de 8 bits, y la rutina pasa a leer bytes y avanzar 8 px."""
import struct
BASE=0x06060000
# rutina inmediata: lectura u16 -> u8 y avance 16 -> 8 px (offsets relativos al inicio de la rutina)
def routine_patches(entry):
    o=entry-BASE
    return [(o+0x66,0x311c,0x0009,2),   # add r1,r1          -> nop
            (o+0x68,0x011d,0x011c,2),   # mov.w @(r0,r1),r1  -> mov.b
            (o+0x6a,0x671d,0x671c,2),   # extu.w r1,r7       -> extu.b
            (o+0xbc,0x00100000,0x00080000,4)]

# (entrada, límite del espacio reutilizable, [(texto, y), ...]); x se centra en 320 px
R9S1_ROUTINE=0x060728c4
R9S1=[
 (0x6073e60,0x6073ec8,[('~ Marchen Ginza ~',128)]),
 (0x6073ec8,0x6073f2c,[('This is',240)]),
 (0x6073f2c,0x6073f64,[('the super-peaceful "Marchen Ginza".',240)]),
 (0x6073f64,0x6073fe4,[("Marchen Ginza's prince,",240)]),
 (0x6073fe4,0x607405c,[('"Kanteimaru",',240)]),
 (0x607405c,0x60740ec,[('hands out fortunes every day.',240)]),
 (0x60740ec,0x6074184,[('With his sloppy appraisals,',240)]),
 (0x6074184,0x6074228,[("he's made everyone super rich.",240)]),
 (0x6074228,0x60742c4,[('But then, out of nowhere,',240)]),
 (0x60742c4,0x6074360,[('the machine planet "Technotch"',240)]),
 (0x6074360,0x60743c4,[('appeared and turned Marchen Ginza',240)]),
 (0x60743c4,0x607448c,[('into a scary land of brutes.',240)]),
 (0x607448c,0x60744c4,[('What a disaster!',240)]),
 (0x60744c4,0x60745bc,[('~',104,32),('~',104,280),('Meanwhile, over in',96),('Music World...',112)]),
 (0x60745bc,0x6074664,[('Katy the match-selling butterfly',240)]),
 (0x6074664,0x6074704,[('were as broke as ever.',240)]),
 (0x6074704,0x60747b4,[('Just then, a',96),('bluebird flew by...',112)]),
 (0x60747b4,0x607483c,[('"If we chase that bluebird,',240)]),
 (0x607483c,0x60748e4,[('maybe we can live a life of ease!"',240)]),
 (0x60748e4,0x6074978,[('With that thought, the broke pair',240)]),
 (0x6074978,0x6074a20,[('dashed off after the bluebird!',240)]),
 (0x6074a20,0x6074a94,[('Before they knew it, the two',240)]),
 (0x6074a94,0x6074b34,[('had wandered deep into',240)]),
 (0x6074b34,0x6074bd0,[('the "Mezzoforte Forest".',240)]),
 (0x6074bd0,0x6074c08,[('There they came across',240)]),
 (0x6074c08,0x6074c9c,[('"Buopos", a mysterious house',240)]),
 (0x6074c9c,0x6074cfc,[('from Marchen Ginza.',240)]),
 (0x6074cfc,0x6074d84,[('Tempo the grasshopper and',240)]),
]
R4S5_ROUTINE=0x06072728
R4S5=[(0x6072dc0,0x6072ecc,[("In Buopos's room,",96),('Tempo and Katy were having a snack.',128)])]

def assemble(entry,limit,lines,routine,encode,alloc):
    """Escribe en buf la función nueva en entry; las cadenas van a su propio hueco o a otro libre (alloc)."""
    lines=[(t,y,x if x is not None else 160-4*len(t)) for t,y,*rest in lines for x in [rest[0] if rest else None]]
    n=len(lines)
    ncode=1+7*n+3
    words_at=entry+2*ncode
    longs_at=(words_at+4*n+3)&~3
    free=longs_at+4*(1+n)
    assert free<=limit,(hex(entry),free-limit)
    alloc.append([free,limit])
    ins=[0x4f22]                       # sts.l pr,@-r15
    def pc(): return entry+2*len(ins)
    def movl(addr,rn):
        d=(addr-((pc()+4)&~3))//4; assert 0<=d<256 and addr%4==0; return 0xd000|rn<<8|d
    def movw(addr,rn):
        d=(addr-(pc()+4))//2; assert 0<=d<256; return 0x9000|rn<<8|d
    encs=[]
    for k,(t,y,x) in enumerate(lines):
        e=bytes(encode(t)); assert 0<len(e)<=40 and 0<=x<320, t; encs.append(e)
        ins.append(movl(longs_at,1))                   # mov.l rutina,r1
        ins.append(movl(longs_at+4+4*k,6))             # mov.l cadena,r6
        ins.append(0xe700|len(e))                      # mov #n,r7
        ins.append(movw(words_at+4*k+2,5))             # mov.w y,r5
        ins.append(movw(words_at+4*k,4))               # mov.w x,r4
        ins.append(0x410b)                             # jsr @r1
        ins.append(0x0009)                             # nop
    ins+= [0x4f26,0x000b,0x0009]                       # lds.l @r15+,pr / rts / nop
    assert len(ins)==ncode
    data=[(entry,struct.pack('>%dH'%len(ins),*ins)),(longs_at,struct.pack('>I',routine))]
    for k,(t,y,x) in enumerate(lines): data.append((words_at+4*k,struct.pack('>HH',x,y)))
    ptrs=[(longs_at+4+4*k,e) for k,e in enumerate(encs)]
    return data,ptrs

def patch(new_get,encode):
    """new_get(f) -> bytes actuales del fichero; devuelve {fichero: bytes}"""
    out={}
    for f,routine,table,extra in (('A_R9S1.BIN',R9S1_ROUTINE,R9S1,True),('A_R4S5.BIN',R4S5_ROUTINE,R4S5,False)):
        b=bytearray(new_get(f))
        for off,old,val,size in routine_patches(routine):
            fmt='>I' if size==4 else '>H'
            assert struct.unpack(fmt,b[off:off+size])[0]==old,(f,hex(off))
            b[off:off+size]=struct.pack(fmt,val)
        alloc=[]; ptrs=[]
        for entry,limit,lines in table:
            b[entry-BASE:limit-BASE]=bytes(limit-entry)
            d,p=assemble(entry,limit,lines,routine,encode,alloc)
            for a,x in d: b[a-BASE:a-BASE+len(x)]=x
            ptrs+=p
        for slot,e in sorted(ptrs,key=lambda q:-len(q[1])):   # cadenas: primer hueco libre que quepa
            for fr in alloc:
                if fr[1]-fr[0]>=len(e):
                    a=fr[0]; fr[0]+=len(e); break
            else: raise AssertionError('sin sitio para %r'%e)
            b[a-BASE:a-BASE+len(e)]=e; b[slot-BASE:slot-BASE+4]=struct.pack('>I',a)
        if extra:
            # PRESS START BUTTON del título: copia 36 bytes desde 0x06073bd8 y dibuja 18 caracteres en x=24
            o=0x6073bd8-BASE; e=bytes(encode('PRESS START BUTTON')); assert len(e)==18
            b[o:o+36]=e+bytes(18)
            o=0x6073d4c-BASE; assert b[o:o+2]==b'\xe4\x18'; b[o+1]=160-4*18
        out[f]=bytes(b)
    return out
