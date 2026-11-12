# forcetxt.sh state actor msg tag [frames] [delay] [cue]
M=${M:-~/.mednafen/mcs/"Super Tempo (Japan).1f6d5d65d6b6d24e84086b60ed6429fc.mc0"}
A=$2
python3 ~/st/sh/poke.py $1 "$M" $(printf '%x' $((A+20))):${SCR:-6083dfc}:4 $(printf '%x' $((A+16))):${LOOP:-6083e00}:4 $(printf '%x' $((A+0xb6))):$3:2 $(printf '%x' $((A+0xa0))):0:2 $(printf '%x' $((A+0xa2))):0:2
source ~/st/sh/m.sh; start "${CUE:-en/Super Tempo (Japan).cue}"; sleep 3; k F7
for i in $(seq 1 ${5:-12}); do sleep ${6:-1}; shot $4_$i; k j; done
cd ~/st/shots && montage $(ls -v $4_*.png) -tile 6x -geometry 176x120+2+2 m.png
