#!/usr/bin/env python3

# Max sample points: 100kS

import vxi11

instrIP='169.254.14.189'
instr=vxi11.Instrument(instrIP)
print(instr.ask('*IDN?'))
instr.write('*RST')
