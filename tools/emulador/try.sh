# usage: try.sh round stage tag  -> loads roundstart state with vars changed, captures frames
source ~/st/sh/m.sh
M=${M:-~/.mednafen/mcs/"Super Tempo (Japan).1f6d5d65d6b6d24e84086b60ed6429fc.mc0"}
S=${S:-/root/st/state_roundstart.mc0}
python3 -c "
import sys;sys.path.insert(0,'/root/st/sh');import mcs
d=mcs.load(sys.argv[2]);mcs.w16(d,0x060e7022,$1);mcs.w16(d,0x060e7024,$2);mcs.save(sys.argv[1],d)" "$M" "$S"
start "${CUE:-en/Super Tempo (Japan).cue}"; sleep 3; k F7; sleep 1
for i in $(seq 1 ${4:-12}); do sleep ${5:-1}; shot $3_$i; k j; done
cd ~/st/shots && montage $(ls -v $3_*.png) -tile 6x -geometry 176x120+2+2 m.png
