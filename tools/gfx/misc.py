"""Rótulos de una sola pieza que se redibujan en su sitio."""
from .relabel import Relabel
def _one(spr,sp,items):
    R=Relabel(spr,sp)
    for k,txt,box,fill,out,bg,font,shade in items: R.redraw(k,R.text(txt,box[0],box[1],fill,out,font=font,shade=shade),bg=bg)
    return R.result()
def patch(cur):
    out={}
    # croar del jefe rana (ゲロー / モゲー), texto sobre el bocadillo (fondo 5)
    out['SPR23.BIN'],out['SPR23_SP.BIN']=_one(cur('SPR23.BIN'),cur('SPR23_SP.BIN'),
        [(1824,'CROAK!',(100,30),3,7,5,'black',4),(1825,'RIBBIT!',(132,30),3,7,5,'black',4)])
    # ラ～ブ
    for f,k in (('SPR22',769),('SPR41',635)):
        out[f+'.BIN'],out[f+'_SP.BIN']=_one(cur(f+'.BIN'),cur(f+'_SP.BIN'),[(k,'LO~VE',(196,56),10,3,0,'bold',None)])
    return out
