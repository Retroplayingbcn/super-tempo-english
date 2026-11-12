import sys,numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0,'/root/st/g2'); import sptable
spr,sp,out=sys.argv[1:4]; scale=int(sys.argv[4]) if len(sys.argv)>4 else 2
e,v=sptable.entries(spr,sp)
W=1600; pages=[]; im=Image.new('RGB',(W,1600),(40,40,60)); dr=ImageDraw.Draw(im); x=y=rowh=0
pal=[(0,0,0)]+[(int(255*k/15),int(255*k/15),int(255*k/15)) for k in range(1,16)]
pal[1]=(250,250,250)
seen=set()
for i,o,off,w,h,cx,cy in e:
    if (off,w,h) in seen: continue
    seen.add((off,w,h))
    d=np.frombuffer(v[off:off+w*h//2],np.uint8); px=np.stack([d>>4,d&15],1).reshape(h,w)
    rgb=np.array(pal,np.uint8)[px]
    s=Image.fromarray(rgb).resize((w*scale,h*scale),Image.NEAREST)
    if x+w*scale>W: x=0;y+=rowh+14;rowh=0
    if y+h*scale+14>1600: pages.append(im); im=Image.new('RGB',(W,1600),(40,40,60)); dr=ImageDraw.Draw(im); x=y=rowh=0
    im.paste(s,(x,y+12)); dr.text((x,y),str(i),fill=(255,255,0)); x+=w*scale+8; rowh=max(rowh,h*scale)
pages.append(im)
for k,p in enumerate(pages): p.save(f'{out}_{k}.png')
print(len(pages))
