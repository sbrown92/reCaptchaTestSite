from sox import core as sx

fileName = '99526.mp3'  # For testing
args = [fileName, 'outfile.wav', 'silence', '1', '0.1', '0.1', '1',
        '0.1', '0.1', ': newfile', ': restart']

# Calls the silence argument to `sox`
#   - args is a list of arguments passed
#   - Will create set of wav files in working directory sequentially
#   called outfile (outfile001, outfile002, ...)
#   - Starts splitting audio when .1 seconds of 1% of volume is detected
#   - Stops splitting audio after .1 seconds of 1% of voume is detected
sx.sox(args)
