import os
import glob
import re
import shutil
from sox import core as sx

'''
    Run this script in a directory with .wav files with 
    their answers as their name. The script will test to 
    see if there are directories set up for 0-9, and make 
    them if not. 
'''

Base_Dir = os.path.dirname(os.path.abspath(__file__))


counter = 0
while counter < 10:
    try:
        os.stat(os.path.join(Base_Dir, str(counter)))
    except:
        os.mkdir(os.path.join(Base_Dir, str(counter)))

    counter += 1


counter = 0
for file in glob.glob("*.wav"):
    if os.path.getsize(file) > 100:
        args = [file, 'out.wav', 'silence',
                '1', '0.1', '0.1',
                '1', '0.1', '0.1',
                ': newfile', ': restart']

        sx.sox(args)
        pos = 0
        for c in os.path.splitext(file)[0]:
            if pos < 9:
                out = "out00" + str(pos + 1) + ".wav"
            else:
                out = "out0" + str(pos + 1) + ".wav"
            new = str(counter) + ".wav"
            oldLoc = os.path.join(Base_Dir, new)
            newLoc = os.path.join(os.path.join(Base_Dir, str(c)), new)

            print "Old - " + out
            print "New - " + new
            os.rename(out, new)
            shutil.move(oldLoc, newLoc)
            pos += 1
            counter += 1




