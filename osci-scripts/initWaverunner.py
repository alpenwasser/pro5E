#!/usr/bin/env python3

# Max sample points: 100kS

import vxi11

instrIP='169.254.14.189'
instr=vxi11.Instrument(instrIP)
print(instr.ask('*IDN?'))
instr.write('*RST')
instr.write('TRIG_MODE NORM')
instr.write('TRIG_SELECT EDGE')
instr.write('C1:TRIG_SLOPE POS')
instr.write('C1:TRIG_LEVEL 1V')
instr.write('TIME_DIV 5US')
instr.write('C1:TRACE OFF')
instr.write('C2:TRACE OFF')
instr.write('C3:TRACE ON')
instr.write('C1:COUPLING D1M')
instr.write('C2:COUPLING D1M')
instr.write('C3:COUPLING D1M')
instr.write('C4:COUPLING D1M')
