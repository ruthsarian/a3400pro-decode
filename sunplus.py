#!/usr/bin/python3

import sys
import struct
import collections
import operator

Header      = ('<I16sBB', collections.namedtuple('Header', 'mark name var1 var2'))
SunplusFF   = ('<HHHIIHBIHB', collections.namedtuple('SunplusFF', 'type orig_samplesize var3 orig_rate rate var6 var7 var8 var9 var10'))
SunplusFE   = ('<HHIIHBIHB4x', collections.namedtuple('SunplusFE', 'type orig_samplesize orig_rate rate var6 var7 var8 var9 var10'))
MiniHeader  = ('<HHH2x', collections.namedtuple('MiniHeader', 'freq type rate'))
ROMHeader   = ('<8s8x6xHI4x32sI', collections.namedtuple('ROMHeader', 'gp_spifi base group_types data group_cnt'))

# type  0x16 2    0
# var2  0x18 2    16
# var3  &param_1  2
# var4  0x1c 4    8000
# var5  0x20 4    0
# var6  0x24 2    0
# var7  0x26 1    0
# var8  0x28 4    0
# var9  0x2c 2    1
# var10	0x2e 1    0

# type
#  C_SACM3400File       0x01
#  C_ADPCM66File        0x03
#  C_S480File           0x07
#  C_S530File           0x08
#  C_S720File           0x09
#  C_S200File           0x0b
#  C_S320File           0x0c
#  C_A1800File          0x0e
#  C_A4800File          0x0f
#  C_A3600File          0x10
#  C_ADPCM34File        0x11
#  C_A6400File          0x12
#  C_ADPCM66EFile       0x13
#  C_A3400Pro4BitFile   0x20 (C_A3400ProFileBase)
#  C_A3400Pro5BitFile   0x21
#  C_A3400Pro6BitFile   0x22
#  C_A3400Pro2BitFile   0x23
#  C_A3400Pro3BitFile   0x24
#  C_A3400ProE4BitFile  0x25 (C_A3400ProEFileBase)
#  C_A3400ProE5BitFile  0x26
#  C_A3400ProFileBase?  0x27, 0x28, 0x29
#  ?                    0x2a
#  C_S880File           0x30
#  C_PCMFile            0x40
#  C_AM1100File2Bit     0x50
#  C_AM1100File3Bit     0x51 (C_AM1100FileBase)
#  C_AM1100File4Bit     0x52
#  C_AM1100File5Bit     0x53
#  C_AM1100File6Bit     0x54
#  C_A1800EFile         0x60
#  C_IMAFile            0x61
#  C_HWPCM16Bit         0x83
#  C_HWPCMGPFAFile      0x84
#  C_AdpcmVBRC74File    0x85
#  C_GeoFile            0x101 (C_GPC74GeoFile)
#  C_WavFileFormat      0x25, 0x26
#  C_A1600FileBase
#  C_A1600 
#  C_A1600File 
#  C_A1601File
#  C_DVRA1600File
#  C_A340640FileBase
#  C_340640ADPCMFile
#  C_340640PCMFile
#  C_S4872FileBase

# GPCD9T
# 16MHz (no effect)
# offset 0
# base 1
# 1 group
# 00000000  47 50 5f 53 50 49 46 49  01 01 01 00 00 00 00 00  |GP_SPIFI........|
# 00000010  00 00 00 00 00 00 01 00  a2 05 00 00 00 00 00 00  |................|
#                             ^---| base
# 00000040  01 00 00 00 48 00 00 00  01 00 00 00 54 00 00 00  |....H.......T...|
# 00000050  a2 05 00 00 31 0d 21 00  77 2b 00 00 02 00 00 00  |....1.!.w+......|
#                       ^---| freq

# val = 0x1000 - freq / 22255
# freq = (0x1000 - val) * 22255


file_types = {
    0x01: 'SACM3400',
    0x03: 'ADPCM66',
    0x07: 'S480',
    0x08: 'S530',
    0x09: 'S720',
    0x0b: 'S200',
    0x0c: 'S320',
    0x0e: 'A1800',
    0x0f: 'A4800',
    0x10: 'A3600',
    0x11: 'ADPCM34',
    0x12: 'A6400',
    0x13: 'ADPCM66E',
    0x20: 'A3400Pro4Bit',
    0x21: 'A3400Pro5Bit',
    0x22: 'A3400Pro6Bit',
    0x23: 'A3400Pro2Bit',
    0x24: 'A3400Pro3Bit',
    0x25: 'A3400ProE4Bit',
    0x26: 'A3400ProE5Bit',
    0x27: 'A3400Pro27',
    0x28: 'A3400Pro28',
    0x29: 'A3400Pro29',
    0x30: 'S880',
    0x40: 'PCM',
    0x50: 'AM1100File2Bit',
    0x51: 'AM1100File3Bit',
    0x52: 'AM1100File4Bit',
    0x53: 'AM1100File5Bit',
    0x54: 'AM1100File6Bit',
    0x60: 'A1800E',
    0x61: 'IMA',
    0x83: 'HWPCM16Bit',
    0x84: 'HWPCMGPFA',
    0x85: 'AdpcmVBRC74',
    0x101: 'Geo',
}

group_ids = {
    0xff: 'unknown',
    0x00: 'speech',
    0x01: 'melody',
    0x02: 'image',
    0x03: 'movie',
    0x80: 'equation',
}

def unpack(t, data):
    return t[1](*struct.unpack(t[0], data))

class sunplus(object):
    def __init__(self, f):
        self.f = f
        data = self.f.read(struct.calcsize(Header[0]))
        self.hdr = unpack(Header, data)
        if self.hdr.mark != 0xff00ff00:
            raise Exception('Mark not present')
        if self.hdr.name not in (b'SUNPLUS SPEECH\x00\x00', b'GENERALPLUS SP\x00\x00'):
            raise Exception('Invalid name')
        if self.hdr.var2 != 0x02:
            raise Exception('Unknown var2')
        if self.hdr.var1 == 0xff:
            data = self.f.read(struct.calcsize(SunplusFF[0]))
            self.sp = unpack(SunplusFF, data)
        elif self.hdr.var1 == 0xfe:
            data = f.read(struct.calcsize(SunplusFE[0]))
            self.sp = unpack(SunplusFE, data)
        else:
            raise Exception('Unknown subtype')
        self.type_id = self.sp.type
        if self.sp.type in file_types:
            self.file_type = file_types[self.sp.type]
        else:
            self.file_type = '%04x' % self.sp.type
        self.header_end = self.f.tell()
        self.rate = self.sp.orig_rate
        self.freq = None

    def seek(self):
        self.f.seek(self.header_end)

class mini(sunplus):
    def __init__(self, f):
        self.f = f
        data = self.f.read(struct.calcsize(MiniHeader[0]))
        self.hdr = unpack(MiniHeader, data)
        self.type_id = self.hdr.type
        self.freq_raw = self.hdr.freq
        self.freq = (0x1000 - self.freq_raw) * 22255
        if self.hdr.type in file_types:
            self.file_type = file_types[self.hdr.type]
        else:
            self.file_type = '%04x' % self.hdr.type
        self.header_end = self.f.tell()
        self.rate = self.hdr.rate

class rom(object):
    def __init__(self, f):
        self.f = f

        self.offset = self.f.tell()
        data = self.f.read(struct.calcsize(ROMHeader[0]))
        self.hdr = unpack(ROMHeader, data)
        self.user_data = self.hdr.data
        if self.hdr.gp_spifi != b'GP_SPIFI':
            raise Exception('Mark not present %08x' % self.hdr.gp_spifi)

        group_offsets = struct.unpack('<%dI' % self.hdr.group_cnt, f.read(self.hdr.group_cnt * 4))
        self.group_cnt = self.hdr.group_cnt
        self.f.seek(self.hdr.group_types)
        data = self.f.read(self.hdr.group_cnt * 4)
        self.group_types = [struct.unpack('<B3x', data[i*4:(i+1)*4])[0] for i in range(0, self.hdr.group_cnt)]
        self.group_files = []
        self.group_strs = []
        for t, offset in zip(self.group_types, group_offsets):
            self.group_strs.append(group_ids[t] if t in group_ids else '0x%02x' % t)
            self.f.seek(offset)
            file_cnt = struct.unpack('<I', self.f.read(4))[0]
            data = f.read((file_cnt + 1) * 4)
            file_offsets = struct.unpack('<%dI' % (file_cnt + 1), data)
            file_sizes = map(operator.sub, file_offsets[1:], file_offsets[:-1])
            self.group_files.append([(a, b) for a, b in zip(file_offsets[:-1], file_sizes)])

    def seek(self, group, idx):
        offset, sz = self.group_files[group][idx]
        self.f.seek(self.offset + offset)

    def read(self, group, idx):
        offset, sz = self.group_files[group][idx]
        self.f.seek(self.offset + offset)
        return f.read(sz)

if __name__ == "__main__":
    with open(sys.argv[1], 'rb') as f:
        try:
            f.seek(0)
            sp = sunplus(f)
            print('Type: %s' % sp.file_type)
            print(sp.sp)
        except:
            f.seek(0)
            m = rom(f)
            if len(sys.argv) <= 2:
                for i in range(0, m.group_cnt):
                    print('Group %d - type %s, files %u' % (i, m.group_strs[i], len(m.group_files[i])))
                    for n, file in enumerate(m.group_files[i]):
                        o, s = file
                        print('File %d - offset 0x%04x, size 0x%04x' % (n, o, s))
            else:
                group, file = sys.argv[2].split(':')
                group, file = int(group), int(file)
                data = m.read(group, file)
                sys.stdout.buffer.write(data)

