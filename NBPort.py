"""Protocol implementation"""
from struct import pack, unpack
import serial
import serial.tools.list_ports as lp
from binascii import hexlify


def checksum(data):
	s = 0
	for c in data:
		s += ord(c)
	return (s & 0xFFFF) ^ 0xFFFF


class NBPort(object):
	HEAD2ESC = 0x20
	ESC2HEAD = 0x23
	HEAD2BMS = 0x22
	BMS2HEAD = 0x25

	def __init__(self, dump=False):
		self.com = None
		self.vid = 0
		self.pid = 0
		self.dump = dump

	def open(self, port=None, mask=""):
		if not port: # no port given
			try: # try getting it from config.py
				from config import port_path
				port = port_path
			except: # no config.py, try gettin by mask
				ports = lp.grep(mask)
				p = next(ports, None)
				port = p[0]
		self.com = serial.Serial(port, 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)		
		return self.com!=None
	
	def wait_pre(self):
		while True:
			while True:
				c = self.com.read(1)
				if c=="\x55":
					break
			while True:
				c = self.com.read(1)
				if c=="\xAA":
					return True 
				if c!="\x55":
					break # start waiting 55 again, else - this is 55, so wait for AA


	def rx(self):
		self.wait_pre()
		pkt = self.com.read(1)
		l = ord(pkt)+3
		for i in xrange(l):
			pkt += self.com.read(1)
		if self.dump:
			print "<", hexlify("\x55\xAA"+pkt)
		ck_calc = checksum(pkt[0:-2])
		ck_pkt = unpack("<H", pkt[-2:])[0]
		if ck_pkt!=ck_calc:
			print "Checksum mismatch !"
			return (0, 0, 0, "")
		return ord(pkt[1]), ord(pkt[2]), ord(pkt[3]), pkt[4:-2] # addr, cmd, param, data

	
	def tx(self, dev, cmd, param, data=""):
		pkt = pack("<BBBB", len(data)+2, dev, cmd, param)+data
		pkt = "\x55\xAA" + pkt + pack("<H", checksum(pkt))
		if self.dump:
			print ">", hexlify(pkt)
		self.com.write(pkt)

	################# ESC commands ############################

	# read config ram. addr is in words, size is in bytes
	def EscReadRegs(self, addr, size):
		self.tx(self.HEAD2ESC, 0x01, addr, chr(size))
		dev, cmd, param, data = self.rx()
		if dev!=self.ESC2HEAD or cmd!=0x01 or param!=addr:
			raise Exception("EscReadRegs: invalid response")
		return data


	def EscWriteSN(self, sn, auth):
		self.tx(self.HEAD2ESC, 0x18, 0x10, pack("<14sL", sn, auth))
		dev, cmd, param, data = self.rx()
		if dev!=self.ESC2HEAD or cmd!=0x18 or param!=1:
			raise Exception("EscWriteSN: invalid response")

	################# DEV01 commands ########################

	def DEV01ReadRegs(self, addr, size):
		self.tx(0x01, 0x01, addr, chr(size))
		dev, cmd, param, data = self.rx()
		if dev!=0x01 or cmd!=0x01 or param!=addr:
			raise Exception("DEV01ReadRegs: invalid response")
		return data


__all__ = ["NBPort"]
