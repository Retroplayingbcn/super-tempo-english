"""Prueba: intercambia la extensión (LBA y tamaño) de dos ficheros en el directorio raíz de la pista 1."""
import sys,struct
sys.path.insert(0,__file__.rsplit('/',1)[0]); import cdbuild
def swap(bin_path, a, b):
    data=bytearray(open(bin_path,'rb').read())
    sec=lambda l: data[l*2352+16:l*2352+16+2048]
    pvd=sec(16); root=pvd[156:156+34]
    rlba=struct.unpack('<I',root[2:6])[0]; rsize=struct.unpack('<I',root[10:14])[0]
    recs={}
    for k in range((rsize+2047)//2048):
        s=sec(rlba+k); o=0
        while o<2048 and s[o]:
            ln=s[o]; nl=s[o+32]; name=bytes(s[o+33:o+33+nl]).decode().split(';')[0]
            recs[name]=(rlba+k,o)
            o+=ln
    def get(n):
        l,o=recs[n]; s=sec(l); return bytes(s[o+2:o+18])
    def put(n,v):
        l,o=recs[n]; p=l*2352+16+o+2; data[p:p+16]=v
    va,vb=get(a),get(b); put(a,vb); put(b,va)
    for n in (a,b):
        l,_=recs[n]; data[l*2352:(l+1)*2352]=cdbuild.fix_mode1(data[l*2352:(l+1)*2352])
    open(bin_path,'wb').write(data)
if __name__=='__main__': swap(*sys.argv[1:4])
