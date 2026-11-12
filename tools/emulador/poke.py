import sys;sys.path.insert(0,'/root/st/sh');import mcs
src,dst=sys.argv[1],sys.argv[2]
d=mcs.load(src)
def w32(a,v): mcs.w16(d,a,v>>16); mcs.w16(d,a+2,v&0xffff)
for arg in sys.argv[3:]:
    a,v,n=arg.split(':'); a=int(a,16); v=int(v,16)
    w32(a,v) if n=="4" else mcs.w16(d,a,v)
mcs.save(dst,d)
# desactiva la caché de ambos SH-2 para que los cambios en RAM se vean
d=mcs.load(dst)
i=0
while True:
    i=d.find(b'\x03CCR\x01\x00\x00\x00',i)
    if i<0: break
    d[i+8]&=0xFE; i+=1
mcs.save(dst,d)
