import gzip,struct,sys
def load(p):
    d=gzip.open(p).read() if open(p,'rb').read(2)==b'\x1f\x8b' else open(p,'rb').read()
    return bytearray(d)
def find_ram(d):
    # look for variable named WorkRAMH or similar
    for nm in [b'WorkRAMH',b'WorkRAM_H',b'WRAMH']:
        i=d.find(nm)
        if i>=0: return nm,i
    return None,-1
if __name__=='__main__':
    d=load(sys.argv[1]); print(len(d), d[:32])
    import re
    for m in re.finditer(rb'[A-Za-z_]{4,}',d[:2000000]):
        pass
    i=0
    names=set()
    for m in re.finditer(rb'(?<=[\x01-\x40])[A-Za-z][A-Za-z0-9_\.\[\]]{3,30}(?=.{4})',bytes(d)):
        names.add(m.group())
    print(sorted(n for n in names if b'RAM' in n.upper() or b'MAIN' in n)[:50])
def ram_off(d):
    i=d.find(b'\x08WorkRAMH'); sz=struct.unpack('<I',d[i+9:i+13])[0]; return i+13,sz
def r16(d,addr):
    o,_=ram_off(d); a=addr&0xFFFFF; return d[o+a]|(d[o+a+1]<<8)
def w16(d,addr,v):
    o,_=ram_off(d); a=addr&0xFFFFF; d[o+a]=v&0xff; d[o+a+1]=v>>8
def save(p,d): open(p,'wb').write(gzip.compress(bytes(d)))
