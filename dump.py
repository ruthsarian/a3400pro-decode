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
	0x01: 'R2-D2',							# hardcoded; no personality chip
	0x02: 'BB-8',								# hardcoded; no personality chip
	0x03: 'blue_resistance',
	0x04: 'gray_scoundrel',
	0x05: 'red_firstorder',
	0x06: 'orange_resistance',
	0x07: 'purple_scoundrel',
	0x08: 'black_firstorder',
	0x09: 'CB-23',							# red_resistance and CB-23 are the same 
	0x0A: 'yellow_resistance',	# possibly CH-33P
	0x0B: 'C1-10P_resistance', 	# hardcoded; no personality chip
	0x0C:	'D-O_resistance',			# hardcoded; no personality chip
	0x0D: 'blue_scoundrel',			# R2-D2
	0x0E:	'BD-1_resistance',		# hardcoded; no personality chip
	0x0F: 'Unknown',
	0x10: 'Drum-Kit_scoundrel'	# white, comes with drum kit
}

affiliation_ids = {
	0x01: 'Scoundrel',
	0x05: 'Resistance',
	0x09: 'First Order',
}

if (len(sys.argv) < 2):
	sys.exit()

input_file = sys.argv[1]
f = open(input_file, 'rb')

rom = sunplus.rom(f)

print("ROM Details")

chip = rom.user_data[6]
if chip in chip_ids:
	print("  %s ROM" % chip_ids[chip])
	chip_name = chip_ids[chip]
else:
	print("  Unknown ROM")
	chip_name = "unknown"

affiliation = rom.user_data[8]
if affiliation in affiliation_ids:
	print("  %s affiliation" % affiliation_ids[affiliation])
else:
	print("  Unknown affiliation.")

print("\n  %s groups in ROM" % rom.group_cnt)
for group in range(0, rom.group_cnt):
  print("    group %d has %d sounds" % (group, len(rom.group_files[group])))

print("\nDumping...")

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
