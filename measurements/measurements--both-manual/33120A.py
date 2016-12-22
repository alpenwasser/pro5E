#!/usr/bin/env python3

import struct





if __name__ == '__main__':
    fg = FunctionGenerator('/dev/ttyUSB0')
    #fg.set_sin(1e3, 1, 1.5)
    fg.set_dc(1.6)
