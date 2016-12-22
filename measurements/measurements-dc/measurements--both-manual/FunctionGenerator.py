import serial


class FunctionGenerator(object):
    def __init__(self, device):
        self.__open_port(device)
        self.__configure_device()

    def __open_port(self, device):
        self.__gen = serial.Serial(
            port=device,
            baudrate=9600,
            timeout=1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS
        )

    def __configure_device(self):
        self.__gen.write(b'OUTP:LOAD INF\n')

    def set_dc(self, voltage):
        self.__gen.write(bytes('APPL:SQU 1E-4 HZ, {} VPP, {} V\n'.format(voltage, voltage/2), 'ascii'))

    def set_sin(self, frequency, vpp, offset):
        self.__gen.write(bytes('APPL:SIN {} HZ, {} VPP, {} V\n'.format(frequency, vpp, offset), 'ascii'))
