import sys,json,struct,os
sys.path.insert(0,'/mnt/project-files/traduccion/herramientas'); import cdbuild
# mkdisc.py outdir src_r src_s dst_r dst_s [base=en]
out,sr,ss,dr,ds=sys.argv[1],*map(int,sys.argv[2:6]); base=sys.argv[6] if len(sys.argv)>6 else 'en'
os.chdir('/root/st')
idx={k:tuple(v) for k,v in json.load(open('idx.json')).items()}
t1=f'{base}/Super Tempo (Japan) (Track 1).bin'
d=open(t1,'rb').read()
l,s=idx['0']; b=bytearray(b''.join(d[(l+i)*2352+16:(l+i)*2352+16+2048] for i in range((s+2047)//2048))[:s])
T=0x604439c-0x06004000
b[T+4*(sr*10+ss):T+4*(sr*10+ss)+4]=b[T+4*(dr*10+ds):T+4*(dr*10+ds)+4]
os.makedirs(out,exist_ok=True)
for f in ['Track 2','Track 3']:
    dst=f'{out}/Super Tempo (Japan) ({f}).bin'
    if not os.path.exists(dst): os.symlink(os.path.abspath(f'{base}/Super Tempo (Japan) ({f}).bin'),dst)
open(f'{out}/Super Tempo (Japan).cue','w').write(open('en/Super Tempo (Japan).cue').read())
cdbuild.patch_track(t1,f'{out}/Super Tempo (Japan) (Track 1).bin',idx,{'0':bytes(b)})
