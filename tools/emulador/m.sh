export DISPLAY=:99 PATH=$PATH:/usr/games
W(){ xdotool search --name "Super Tempo" | head -1; }
start(){ pkill -x mednafen; sleep 0.5; (cd ~/st && mednafen -sound ${SND:-0} "${1:-en/Super Tempo (Japan).cue}" >~/st/mlog.txt 2>&1 &); sleep 3; }
k(){ for x in "$@"; do w=$(W); xdotool windowactivate --sync $w 2>/dev/null; xdotool keydown --window $w $x; sleep 0.12; xdotool keyup --window $w $x; sleep 0.25; done; }
hold(){ w=$(W); xdotool keydown --window $w $1; sleep $2; xdotool keyup --window $w $1; }
ff(){ k grave; }
shot(){ import -window $(W) ~/st/shots/$1.png; }
