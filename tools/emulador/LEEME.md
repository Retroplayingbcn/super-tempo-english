# Utilidades de emulador (Mednafen + Xvfb + xdotool)

- `m.sh`: funciones de shell (`start`, `k` tecla, `hold`, `ff` avance rápido, `shot` captura). Mandos: W/A/S/D cruceta, J/K/L = A/B/C, Return = Start.
- `mcs.py`: leer/escribir la RAM alta (WorkRAMH) dentro de un estado `.mc*` de Mednafen.
- `poke.py src dst ADDR:VAL:2|4 ...`: escribe en la RAM de un estado y desactiva la caché SH-2 (CCR.CE) para que el cambio se vea.
- `jump.sh R F tag`: desde un estado guardado en la intro, sustituye la escena (2,1) por la (R,F) en la tabla de escenas y termina la intro.
- Variables: ronda 0x060E7022, fase 0x060E7024, ronda siguiente 0x060E7026; tabla de escenas 0x0604439C+4*(R*10+F).

Los scripts asumen las rutas de trabajo de /root/st (disco extraído en en/, jp/, estados de partida en /root/st/*.mc*); ajústalas si cambian.
