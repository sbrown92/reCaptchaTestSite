from dejavu.dejavu import Dejavu
from dejavu.dejavu.recognize import FileRecognizer
import glob
from sox import core as sx

config = {
    "database": {
        "host": "127.0.0.1",
        "user": "root",
        "passwd": "Ilikepie9",
        "db": "dejavu",
    },
    "database_type": "mysql",
    "fingerprint_limit": -1
}


djv = Dejavu(config)

fileName = "audio.mp3"

args = [fileName, 'out.wav', 'silence',
                '1', '0.1', '0.1',
                '1', '0.1', '0.1',
                ': newfile', ': restart']


for i in range(0, 10):
    djv.fingerprint_directory("example_files/" + str(i) + "/", [".wav"], 5)

sx.sox(args)

for piece in glob.glob("out*.wav"):
    song = djv.recognize(FileRecognizer, piece)
    print piece + " -- "
    print song


