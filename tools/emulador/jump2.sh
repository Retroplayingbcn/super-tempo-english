# jump2.sh round stage tag [frames] [delay]: intro state, next-round=round, table(round,1)->(round,stage)
source ~/st/sh/m.sh
M=${M:-~/.mednafen/mcs/"Super Tempo (Japan).1f6d5d65d6b6d24e84086b60ed6429fc.mc0"}
python3 -c "
import sys;sys.path.insert(0,'/root/st/sh');import mcs
d=mcs.load('${S:-/root/st/state_intro_map.mc1}')
T=0x604439c; s=T+4*($1*10+$2); t=T+4*($1*10+1)
for k in (0,2): mcs.w16(d,t+k,mcs.r16(d,s+k))
mcs.w16(d,0x60e7026,$1)
mcs.save(sys.argv[1],d)" "$M"
start "${CUE:-en/Super Tempo (Japan).cue}"; sleep 3; k F7; sleep 1; ff; for i in $(seq 1 ${N:-55}); do k j; done; ff
for i in $(seq 1 ${4:-12}); do sleep ${5:-2}; shot $3_$i; k j; done
cd ~/st/shots && montage $(ls -v $3_*.png) -tile 6x -geometry 176x120+2+2 m.png
