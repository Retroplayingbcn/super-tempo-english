"""Parches de gráficos (rótulos con texto japonés en sprites)."""
import os
def patch_all(get):
    """get(nombre) -> bytes actuales del fichero; devuelve {nombre: bytes nuevos}"""
    from . import common, hint, quiz, misc, extra
    out={}
    def cur(f): return out.get(f) or get(f)
    sprs=sorted(f for f in get(None) if f.startswith('SPR') and f.endswith('.BIN') and 'SP' not in f[3:])
    for f in sprs:
        sp=f[:-4]+'_SP.BIN' if f[:-4]+'_SP.BIN' in get(None) else f[:-4]+'SP.BIN'
        if sp not in get(None): continue
        a,b=common.patch(cur(f),cur(sp))
        if a!=cur(f) or b!=cur(sp): out[f],out[sp]=a,b
    out['SPR23.BIN'],out['SPR23_SP.BIN']=hint.patch(cur('SPR23.BIN'),cur('SPR23_SP.BIN'))
    out['SPR5S.BIN'],out['SPR5S_SP.BIN']=quiz.patch(cur('SPR5S.BIN'),cur('SPR5S_SP.BIN'))
    for f,data in misc.patch(cur).items(): out[f]=data
    allspr=sorted(f for f in get(None) if f.startswith('SPR') and f.endswith('.BIN') and not f.endswith('SP.BIN'))
    for f,data in extra.patch(cur,allspr).items(): out[f]=data
    return out
