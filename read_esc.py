"""Read ESC config to file"""
from sys import exit
from NBPort import NBPort

port = NBPort(dump=True)

if not port.open():
	exit("Can't open port !")

hfo = open("esc_config.bin", "wb")
for i in xrange(0, 0x200, 0x80):
	hfo.write(port.EscReadRegs(i>>1, 0x80))
hfo.close()
