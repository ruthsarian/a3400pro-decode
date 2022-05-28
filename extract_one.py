#!/usr/bin/python3

# extract_one.py <filename>:<group>,<index> <output filename>

import sys
import wave
import a3400pro
import collections
import operator
import sunplus

input_file, _, record = sys.argv[1].partition(':')
group, _, idx = record.partition(',')

group = int(group) if group else None
idx = int(idx) if idx else None

f = open(input_file, 'rb')

if group is None:
    try:
        sp = sunplus.sunplus(f)
    except:
        f.seek(0)
        sp = sunplus.mini(f)
else:
    rom = sunplus.rom(f)
    rom.seek(group, idx)
    sp = sunplus.mini(f)

sp.seek()

if len(sys.argv) > 2:
    if sys.argv[2] == '-':
        out = wave.open(sys.stdout.buffer, 'wb')
    else:
        out = wave.open(sys.argv[2], 'wb')
    out.setnchannels(1)
    out.setsampwidth(2)
    out.setframerate(sp.rate)
    out.writeframes(a3400pro.decode(f))
else:
    print('Sunplus %s' % (sp.file_type))