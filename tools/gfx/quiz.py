"""Concurso musical de la ronda 5 (SPR5S, objeto 42): respuestas con flecha."""
from .relabel import Relabel
Q={6:'DO MI',7:'TI RE',8:'ZU RA',9:'DO SO',10:'LA DO',11:'MI SO',12:'SAX',13:'HORN',14:'BANJO',15:'GUITAR',16:'BONGO',
   17:'TIMPANI',18:'PANDA',19:'HUMAN',20:'GIRAFFE',21:'ANTELOPE',22:'BEETHOVEN',23:'BACH',24:'WAGNER',25:'TWINKLE STAR',
   26:'GLARING STAR',27:'ELEPHANT SONG',28:'ELEPHANT RAG',29:'TROIKA',30:'SQUID TORO',31:'DO',32:'MI',33:'SO'}
OBJ=42; ARROW={660,661}
def patch(spr,sp):
    R=Relabel(spr,sp); R.apply(OBJ,Q,keep=ARROW,height=16,sx=0.85,align='after',gap=4,ref='AOQ')
    return R.result()
