#!/usr/bin/python3

# for %f in *.bin do dump.py %f
# dump.py <filename>

import os
import sys
import wave
import a3400pro
import collections
import operator
import sunplus

chip_ids = {
	0x03: 'blue',
	0x04: 'gray',
	0x05: 'red',
	0x06: 'orange',
	0x07: 'purple',
	0x08: 'black',
	0x09: 'cb-23',
	0x0A: 'yellow'
}

affiliation_ids = {
	0x01: 'scoundrel',
	0x05: 'resistance',
	0x09: 'first order',
}

if (len(sys.argv) < 2):
	sys.exit()

input_file = sys.argv[1]
f = open(input_file, 'rb')

rom = sunplus.rom(f)

chip = rom.user_data[6]
if chip in chip_ids:
	print("%s rom" % chip_ids[chip])
	chip_name = chip_ids[chip]
else:
	print("Unknown rom")
	chip_name = "unknown"
	
affiliation = rom.user_data[8]
if affiliation in affiliation_ids:
	print("%s affiliation" % affiliation_ids[affiliation])
else:
	print("Unknown affiliation.")

print("Dumping...")

for group in range(0, rom.group_cnt):
	for idx, file in enumerate(rom.group_files[group]):
		out_filename = "%s_%02d-%02d.wav" % (chip_name,group+1,idx+1)
		rom.seek(group, idx)
		sp = sunplus.mini(f)
		sp.seek()
		out = wave.open(out_filename, 'wb')
		out.setnchannels(1)
		out.setsampwidth(2)
		out.setframerate(sp.rate)
		end_data = []
		print("  %s" % out_filename,end="")
		try:
			out.writeframes(a3400pro.decode(f, end_data))
			out.close()
			print()
		except:
			out.close()
			os.remove(out_filename)
			print(" - ERROR")
