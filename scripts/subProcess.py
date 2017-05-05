import os
from audio import splitFile
from breaker import getInputs, scraper, getProfile, automatePage, getAnswer, FIREFOX_PATH
from Fingerprinter import fingerprintFile
import shutil
import glob


BASE_DIR = os.path.dirname(os.path.abspath(__file__))



def downloader(fireFoxPath, prefs, address, inputList):

    automatePage(fireFoxPath=fireFoxPath, prefs=prefs, address=address, inputList=inputList)
    return ("audio.mp3")

def split_finger_rename_delete(sFile):

    try:
        os.stat(os.path.join(BASE_DIR, "unsorted_files"))
    except:
        os.mkdir(os.path.join(BASE_DIR, "unsorted_files"))

    count = 0
    splitFile(sFile)


    for piece in glob.glob("outfile*.wav"):
        if os.stat(piece).st_size >100:
            answer = getAnswer(piece)
            if answer != '?':
                os.rename(piece, answer + ".wav")
                fingerprintFile(answer)
                os.remove(answer + ".wav")
            else:
                os.rename(piece, str(count) + ".wav")
                shutil.move(str(count) + ".wav", "unsorted_files/" + str(count) + ".wav")
                count += 1

    for file in glob.glob("*.wav"):
        print file

def main():
    running = True
    while(running):
        proxyPool = scraper()
        prefs = getProfile(proxyPool)
        urlAddr, inputs = getInputs()
        sFile = downloader(fireFoxPath=FIREFOX_PATH, prefs=prefs, address=urlAddr, inputList=inputs)
    
        # splits, fingerprints, and renames file
        split_finger_rename_delete(sFile)


if __name__ == "__main__":
    main()
