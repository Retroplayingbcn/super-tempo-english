# Historial de versiones / Changelog

(En español; resumen en inglés en el README.)

## v0.9.1 (correcciones tras la prueba en Saturn)
- **Texto roto en la historia**: los subtítulos de la historia inicial (la demo que sale al esperar en el título:
  Marchen Ginza, Kanteimaru, Technotch, Music World…) y la tarjeta negra antes de la Techno Mask
  (ブオポスのへやのなかで / テンポとケイティはおやつのじかん) los pinta otra rutina que el parche no tocaba. Como la fuente
  ya tiene letras latinas en lugar de algunas kana, salían en japonés con letras sueltas mezcladas. Ahora están traducidos
  ("In Buopos's room, / Tempo and Katy were having a snack.") y esa rutina lee texto de 8 bits con avance de 8 px.
  La historia inicial está comprobada en Mednafen de principio a fin ; la tarjeta, en el simulador SH-2.
- **Cartel 入る / べからず** de la fase nocturna de Bremen: KEEP / OUT!
- **Cuelgue tras el jefe final**: no reproducido. En esa fase el parche solo cambia el gráfico del menú de pausa (mismo
  tamaño, el mismo cambio que en todas las demás fases); el código de la fase es el original.

## v0.9
- **Bocadillos del jefe gallo-robot** (ヅーーッ / コケッ / ケッコー): ZZZT! / CLUCK! / BAWK!
- **Canción de las ranas** (カエルノウタガ キコエテクルヨ): cada bocadillo lleva su sílaba en romaji
  (KA-E-RU-NO-U-TA-GA / KI-KO-E-TE-KU-RU-YO), en las dos fases donde sale.
- **Carteles de la mansión**: ぢ → PILES (el chiste japonés de las almorranas) y マース → MARS, en todos los ficheros que los repiten.
- **Pintada de los músicos de Bremen** (ぶれ〜めんば): BREMEN BAND, en trazo de tiza.

## v0.3
- **Gráficos traducidos** (sprites redibujados en inglés):
  - Pausa en todas las fases: PAUSE / NORMAL SOUND / VOICE SOUND, y CONTINUE / QUIT (comparten gráfico en los 33 ficheros de sprites).
  - Pista del jefe 1: "Beat the tadpoles!" / "Turn into Muscle Tempo, tweet!".
  - Concurso de la ronda 5: las 28 respuestas (DO MI, SAX, PANDA, BEETHOVEN, TWINKLE STAR…).
  - Bocadillos CROAK! / RIBBIT! de las ranas y los rótulos LO~VE.
- **Guion pulido**: 9 frases revisadas en contexto (visita de Major Minor en la intro, "To think you beat the Frog King!",
  saludo "Dear Tempo," de la carta final y de la tasación, "And now, my verdict..."), sin cambiar el sentido.

## v0.2
- **Tiendas** (A_R8S5, tienda del pájaro, y A_R8S6, tienda de los Mussies): frases del tendero y categorías
  ("Time to pay up, tweet!", "Pick one, tweet.", "Comics, tweet!!"…). La rutina pasa a leer 8 bits y avanzar 8 px.
- **Final** (A_R9S2): carta de Major Minor, los 12 rangos del 長者番付 (Super/–/Kinda + Billionaire, Millionaire,
  Rich Kid, Well-Off Kid), los mensajes "It's "…"-chu~!!", la narración final ("And so, / Tempo and Katy /
  became "…" / or so the story goes. / Happily ever after. The end."), "T H E  E N D" y la pantalla del
  selector de ronda ("At the first ROUND START, hold Y, Z and R and press L…").
- **Créditos**: siguen en inglés como en el original, pero pasados a la fuente estrecha (8 px) porque comparten
  rutina con la carta. Se mantiene el mismo ritmo de aparición, así que quedan algo más espaciados.
- **Veredictos de la tasación** (estantería de A_R9S5: Junk / So-so / Nice / Superb / Great!! / !!!!!).
  En la v0.1 salían corruptos: los dibuja la rutina que ya leía 8 bits y seguían en 16 bits. Ahora se ven
  con el color normal del texto (el original los marcaba con un bit de color que no cabe en 8 bits).


## v0.1
- Primera versión: diálogos (intro de Major Minor, Kanteimaru, Techno Mask, tasación), menú del título, HEAR/SKIP.
