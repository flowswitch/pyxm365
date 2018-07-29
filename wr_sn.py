"""ESC activation - fixes errors 27, 35"""
from sys import exit
from struct import pack, unpack
from NBPort import NBPort

# Serial number to set. Must be 14 symbols !
# Valid combinations:
#	M1Gxyxxxxxxxxx
#	1367yxxxxxxxxx
#	1613yxxxxxxxxx
#	16057xxxxxxxxx
#	1634yxxxxxxxxx
# y=8 has some special meaning (white color?)

# This is default SN. Causes error 35:	M1GCA1601C0001
# These are TestDevice SNs found in the update package:
#	M1GCA1601C0002
#	M1GCA1601C0003

new_sn = "16133/11111111"

##############################

def CalcSnAuth(oldsn, newsn, uid3):
	s = 0
	for i in xrange(0x0E):
		s += ord(oldsn[i])
		s *= ord(newsn[i])
	s += uid3+(uid3<<4)
	if s<0:
		s = -s
	s &= 0xFFFFFFFF		

	return s % 1000000

###############################

port = NBPort(dump=True)

if not port.open():
	exit("Can't open port !")

old_sn = port.EscReadRegs(0x10, 0x0E)
print "Old S/N:", old_sn

uid3 = unpack("<L", port.EscReadRegs(0xDE, 4))[0]
print "UID3: %08X" % (uid3)

auth = CalcSnAuth(old_sn, new_sn, uid3)
print "Auth: %08X"  % (auth)

port.EscWriteSN(new_sn, auth)
print "OK"
