from ctypes import *
from binascii import hexlify, unhexlify

lib = cdll.LoadLibrary('./libS8.so')

# int fw_init_ex(int comType, char* szPathName, long baud);
lib.fw_init_ex.argtypes =  [c_int, c_char_p, c_long]
fw_init_ex = lib.fw_init_ex
# int fw_halt(int icdev);
lib.fw_halt.argtypes = [c_int]
fw_halt = lib.fw_halt
# int fw_exit(int icdev);
lib.fw_exit.argtypes = [c_int]
fw_exit = lib.fw_exit
# int fw_beep(int icdev, unsigned int _Msec);
lib.fw_beep.argtypes = [c_int, c_ushort]
fw_beep = lib.fw_beep
# int fw_card_hex(int icdev, unsigned char _Mode, unsigned char * Snrbuf);
lib.fw_card_hex.argtypes = [c_int, c_char, c_char_p]
fw_card_hex =lib.fw_card_hex
# int fw_load_key(int icdev, unsigned char _Mode, unsigned char _SecNr, unsigned char *_NKey);
lib.fw_load_key.argtypes = [c_int, c_char, c_char, c_char_p]
fw_load_key = lib.fw_load_key
#int fw_authentication(int icdev, unsigned char _Mode, unsigned char _SecNr);
lib.fw_authentication.argtypes = [c_int, c_char, c_char]
fw_authentication = lib.fw_authentication
# int fw_read(int icdev, unsigned char _Adr, unsigned char *_Data);
lib.fw_read.argtypes = [c_int, c_char, c_char_p]
fw_read = lib.fw_read
# int fw_write(int icdev, unsigned char _Adr, unsigned char *_Data);
lib.fw_write.argtypes = [c_int, c_char, c_char_p]
fw_write = lib.fw_write
# int fw_changeb3(int icdev, unsigned char _SecNr, unsigned char *_KeyA, unsigned char *_CtrlW, unsigned char _Bk, unsigned char *_KeyB);
lib.fw_changeb3.argtypes = [c_int, c_char, c_char_p, c_char_p, c_char, c_char_p]
fw_changeb3 = lib.fw_changeb3

default_key = (b'\xff' * 6)
default_acb = b'\xff\x07\x80\x00'

def __auth_block(reader, block=0, key=default_key):
	if (type(key) == type('')):
		key = unhexlify(key)
	elif (type(key) == type(0x0)):
		key = bytes.fromhex((('00' * 6) + hex(key)[2:])[-12:])
	if (len(key) != 6):
		return False
	sector = (block // 4)
	if (fw_load_key(reader, 0, sector, key) == 0):
		__uid = c_buffer(8)
		if (fw_card_hex(reader, 1, __uid) == 0):
			if (fw_authentication(reader, 0, sector) == 0):
				return __uid.value.decode()
	return False

def read_block(reader, block=0, key=default_key):
	__uid = __auth_block(reader, block, key)
	if __uid:
		__data = c_buffer(16)
		if (fw_read(reader, block, __data) == 0):
			if (fw_halt(reader) == 0):
				return '%s:%s:%s'%(__uid, block, hexlify(__data.raw).decode().upper())
	return False

def write_block(reader, block, data, key=default_key):
	if (type(data) == type('')):
		data = unhexlify(data)
	if (block == 0) or ((block % 4) == 3) or (len(data) != 16):
		fw_beep(reader, 1)
		return None
	__uid = __auth_block(reader, block, key)
	if __uid:
		if (fw_write(reader, block, data) == 0):
			if (fw_halt(reader) == 0):
				return '%s:%s:%s'%(__uid, block, hexlify(data).decode().upper())
	return False

def reset_block(reader, block, key=default_key):
	return write_block(reader, block, (b'\x00' * 16), key)

def read_uid(reader):
	__uid = c_buffer(8)
	if (fw_card_hex(reader, 1, __uid) == 0):
			if (fw_halt(reader) == 0):
				return __uid.value.decode()
	return False

def change_key(reader, block, newkey, key=default_key):
	if (type(newkey) == type('')):
		newkey = unhexlify(newkey)
	if (len(newkey) != 6):
		fw_beep(reader, 1)
		return None
	__uid = __auth_block(reader, block, key)
	if __uid:
		if (fw_changeb3(reader, (block // 4), newkey, default_acb, 0, default_key) == 0):
			if (fw_halt(reader) == 0):
				return '%s:%s:[%s]'%(__uid, block, hexlify(newkey).decode().upper())
	return False

def reset_key(reader, block, key):
	return change_key(reader, block, default_key, key)

def reset_sector(reader, block, key):
	__trailer = reset_key(reader, block, key)
	if __trailer:
		fw_halt(reader)
		__sector = []
		__block = ((block // 4) * 4)
		__sector.append(reset_block(reader, (__block + 0)))
		__sector.append(reset_block(reader, (__block + 1)))
		__sector.append(reset_block(reader, (__block + 2)))
		__sector.append(__trailer)
		return __sector
	return False

def read_sector(reader, block=0, key=default_key):
	__sector = []
	__block = ((block // 4) * 4)
	__sector.append(read_block(reader, (__block + 0), key))
	__sector.append(read_block(reader, (__block + 1), key))
	__sector.append(read_block(reader, (__block + 2), key))
	__sector.append(read_block(reader, (__block + 3), key))
	return __sector

class Reader:

	def __init__(self, device, contype=2, bauds=115200):
		reader = fw_init_ex(contype, device.encode(), bauds)
		if (reader == -1):
			raise IOError('initialization of %s failed' % device)
		self.__reader = reader
		self.__defaultKey = (
			(type(default_key) == type(b'')) \
			and hexlify(default_key).decode() \
			or default_key
		)
		self.__defaultACB = (
			(type(default_acb) == type(b'')) \
			and hexlify(default_acb).decode() \
			or default_acb
		)

	@property
	def reader(self):
		return self.__reader

	@property
	def defaultKey(self):
		return self.__defaultKey

	@property
	def defaultACB(self):
		return self.__defaultAccessBytes

	def __del__(self):
		fw_exit(self.__reader)

	def readUID(self):
		return read_uid(self.__reader)

	def readBlock(self, block=0, key=None):
		return read_block(self.reader, block, (key or self.defaultKey))

	def writeBlock(self, block, data, key=None):
		return write_block(self.reader, block, data, (key or self.defaultKey))

	def resetBlock(self, block, key=None):
		return write_block(self.reader, block, '00'*16, (key or self.defaultKey))

	def changeKey(self, block, newkey, key=None):
		return change_key(self.reader, block, newkey, (key or self.defaultKey))

	def resetKey(self, block, key):
		return reset_key(self.reader, block, key)

	def readSector(self, block=0, key=None):
		return read_sector(self.reader, block, (key or self.defaultKey))

	def resetSector(self, block, key):
		return reset_sector(self.reader, block, key)
