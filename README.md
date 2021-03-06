# libS9
Python library for IC Card Reader S9-BU-00-01 from Fongwah


## foreword

the library is intended to be used with `Python3` under `Linux`.
it only implements some functions from `libS8.so` around `Mifare S50 tags` (classic 1k EV1).
only the `A key` is used.
except `readUID`, all the proposed functions expect a `block number` as input.


## usage

```pycon
>>> from libS9 import Reader
>>> reader = Reader('/dev/usb/hiddev3')

>>> # get UID tag
>>> reader.readUID()
'0BDA3FF0'

>>> # read first block 
>>> reader.readBlock()
'0BDA3FF0:0:F03FDA0B1E8804000000000000000000'
>>> reader.readBlock(0)
'0BDA3FF0:0:F03FDA0B1E8804000000000000000000'
>>> reader.readBlock(0, 'FF'*6)
'0BDA3FF0:0:F03FDA0B1E8804000000000000000000'

>>> # blocks 0, 1, 2 & 3 are on the same sector 0 [012[3]][456[7]]...
>>> reader.readBlock(0)
'0BDA3FF0:0:F03FDA0B1E8804000000000000000000'
>>> reader.readBlock(1)
'0BDA3FF0:1:00000000000000000000000000000000'
>>> reader.readBlock(2)
'0BDA3FF0:2:00000000000000000000000000000000'
>>> reader.readBlock(3)
'0BDA3FF0:3:000000000000FF078000FFFFFFFFFFFF'
>>> reader.readSector(2)
['0BDA3FF0:0:F03FDA0B1E8804000000000000000000', '0BDA3FF0:1:00000000000000000000000000000000', '0BDA3FF0:2:00000000000000000000000000000000', '0BDA3FF0:3:000000000000FF078000FFFFFFFFFFFF']
>>> reader.writeBlock(2, '1234567890ABCDEF'*2)
'0BDA3FF0:2:1234567890ABCDEF1234567890ABCDEF'
>>> reader.readSector(1)
['0BDA3FF0:0:F03FDA0B1E8804000000000000000000', '0BDA3FF0:1:00000000000000000000000000000000', '0BDA3FF0:2:1234567890ABCDEF1234567890ABCDEF', '0BDA3FF0:3:000000000000FF078000FFFFFFFFFFFF']

>>> # can't use writeBlock on access control block (trailer)
>>> # block 3 is the trailer block of sector 0 [012[3]][456[7]]...
>>> reader.writeBlock(1, '11'*16)
'0BDA3FF0:1:11111111111111111111111111111111'
>>> reader.writeBlock(3, '4BAD'*4)
>>> print(reader.writeBlock(3, '4BAD'*4))
None
>>> # and of course on manufacturer block
>>> reader.writeBlock(0, '4BAD'*4)
>>> print(reader.writeBlock(0, '4BAD'*4))
None


>>> # change keyA on block 7 (trailer) of sector 1 [012[3]][456[7]]...
>>> # REMEMBER (WRITE DOWN) THE KEYS YOU INSTALL
>>> reader.changeKey(4, 'EE'*6)
'0BDA3FF0:4:[EEEEEEEEEEEE]'
>>> reader.changeKey(5, 'AA'*6, 'EE'*6)
'0BDA3FF0:5:[AAAAAAAAAAAA]'
>>> reader.resetKey(6, 'AA'*6)
'0BDA3FF0:6:[FFFFFFFFFFFF]'
>>> reader.readBlock(7)
'0BDA3FF0:7:000000000000FF078000FFFFFFFFFFFF'

>>> # key (6 bytes) can be passed as bytes, string or integer
>>> reader.readBlock(2, b'\xff'*6)
'0BDA3FF0:2:1234567890ABCDEF1234567890ABCDEF'
>>> reader.readBlock(2, 'ff'*6)
'0BDA3FF0:2:1234567890ABCDEF1234567890ABCDEF'
>>> reader.readBlock(2, 0xFFFFFFFFFFFF)
'0BDA3FF0:2:1234567890ABCDEF1234567890ABCDEF'

>>> # data (16 bytes) can be passed as bytes or string
>>> reader.writeBlock(60, b'\x01'*16)
'0BDA3FF0:60:01010101010101010101010101010101'
>>> reader.writeBlock(61, '10'*16)
'0BDA3FF0:61:10101010101010101010101010101010'
>>> reader.readSector(60)
['0BDA3FF0:60:01010101010101010101010101010101', '0BDA3FF0:61:10101010101010101010101010101010', '0BDA3FF0:62:00000000000000000000000000000000', '0BDA3FF0:63:000000000000FF078000FFFFFFFFFFFF']

>>> # "protect" sector 15 with new keyA
>>> # REMEMBER (WRITE DOWN) THE KEYS YOU INSTALL
>>> reader.changeKey(60, '102030'*2)
'0BDA3FF0:60:[102030102030]'
>>> reader.readBlock(60)
False
>>> reader.writeBlock(60, '88'*16)
False
>>> reader.readSector(60)
[False, False, False, False]
>>> reader.readSector(60, '102030102030')
['0BDA3FF0:60:01010101010101010101010101010101', '0BDA3FF0:61:10101010101010101010101010101010', '0BDA3FF0:62:00000000000000000000000000000000', '0BDA3FF0:63:000000000000FF078000FFFFFFFFFFFF']

>>> # reset a sector
>>> reader.resetSector(60, '123456'*2)
False
>>> reader.resetSector(60, '102030'*2)
['0BDA3FF0:60:00000000000000000000000000000000', '0BDA3FF0:61:00000000000000000000000000000000', '0BDA3FF0:62:00000000000000000000000000000000', '0BDA3FF0:60:[FFFFFFFFFFFF]']
>>> # reset a block
>>> reader.readBlock(2)
'0BDA3FF0:2:1234567890ABCDEF1234567890ABCDEF'
>>> reader.resetBlock(2)
'0BDA3FF0:2:00000000000000000000000000000000'
```


## S9-BU-00-01

![S9-BU-00-01](s9r.jpg)
![S9-BU-00-01](s9v.jpg)
