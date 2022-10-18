# a3400pro-decode
This is a set of python scripts that can be used to decode audio stored on droid personality chips from Droid Depot at Galaxy's Edge.

This code was originally developed by [russdill](https://github.com/russdill/a3400pro) and has been modified slightly to help with ease-of-use.

To use this code you must first extract the contents of a personality chip's flash memory to a file then execute the following command:

`dump.py <CHIP.BIN>`

This will extract the audio files from the flash memory dump and decode them to WAV format.
