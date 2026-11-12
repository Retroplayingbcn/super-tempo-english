"""Rótulos del bloque común de sprites (están en cada SPRxx con su propio SPRxx_SP): pausa y fin de partida."""
from .relabel import Relabel, objects, records
PAUSE_W=[40,8,24,32,16,16,16,16]
TEXTS={0:dict(text='PAUSE',h=30,ref='A'),           # ポーズなのだ
       1:dict(text='NORMAL SOUND',h=18,w=140,ref='A'), # ノーマルのおと
       2:dict(text='VOICE SOUND',h=18,w=120,ref='A'),  # こえのおと
       3:dict(text='CONTINUE',h=20,w=110,ref='A'),     # つづける
       4:dict(text='QUIT',h=20,ref='A')}               # やめる
def find_obj(t):
    for k,fr in objects(t).items():
        if fr and [r[3] for r in records(t,fr[0])]==PAUSE_W: return k
def patch(spr,sp):
    k=find_obj(sp)
    if k is None: return spr,sp
    R=Relabel(spr,sp); R.apply(k,TEXTS)
    return R.result()
