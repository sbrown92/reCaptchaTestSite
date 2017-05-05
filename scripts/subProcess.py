"""
    I was still unable to get the recaptha widget to show up on 
    my website.  This script complies, but could'nt test it because
    recaptha widget is down.

"""
import json
import os

from sox import core as sx
from bs4 import BeautifulSoup
from sox import Transformer
from urllib2 import urlopen
from urllib import urlretrieve
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from watson_developer_cloud import SpeechToTextV1

from breaker import getInputs, scraper, getProfile, automatePage, WATSON_USER, WATSON_PASS

from dejavu import Dejavu
from dejavu.recognize import FileRecognizer
import glob
#from keys import WATSON_USER, WATSON_PASS

#######################################
####                               ####
####   Constant Variables          ####
####                               ####
#######################################

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIREFOX_PATH = os.path.join(BASE_DIR, 'geckodriver')



def downloader(fireFoxPath, prefs, address, inputList):

    fileName = "audio"
    sx = Transformer()

    # Watson API Settings.
    speech_engine = SpeechToTextV1(
        username=WATSON_USER,
        password=WATSON_PASS,
        x_watson_learning_opt_out=True)


    #Automate interactions with widget.
    #Webdriver creation
    br = webdriver.Firefox(executable_path=fireFoxPath)
    wait = WebDriverWait(br, 5)
    print "Loading page " + address
    br.get(address)

    ####################
    ### Fill in Form ###
    ####################

    print "Filling out Form"
    for input in inputList:
        br.find_element_by_id(input[0]).send_keys(input[1])


    ########################
    ### reCaptcha Widget ###
    ########################
    print "Finding reCaptcha Widget"
    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'iframe')))
    br.find_elements_by_tag_name('iframe')
    iframe = br.find_elements_by_tag_name('iframe')[0]
    iframe2 = br.find_elements_by_tag_name('iframe')[1]
    br.switch_to_frame(iframe)
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'recaptcha-checkbox-checkmark'))).click()
    br.switch_to_default_content()
    br.switch_to_frame(iframe2)
    wait.until(EC.presence_of_element_located((By.ID, 'recaptcha-audio-button')))
    sleep(2)
    wait.until(EC.element_to_be_clickable((By.ID, 'recaptcha-audio-button'))).click()
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'rc-audiochallenge-download-link')))
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'rc-audiochallenge-download-link'))).click()

    ###########################
    ### download audio file ###
    ###########################
    print "Downloading Audio File"
    audiolink = br.find_elements_by_xpath("//a[@href]")
    for link in audiolink:
        finalLink = link.get_attribute("href")
    urlretrieve(finalLink, BASE_DIR + "/" + fileName + ".mp3")


    return (fileName + ".mp3")


def split_finger_rename_delete(sFile):

    os.chdir("/Users/maxwellmackoul/Desktop/Recapture/Recapture2/reCaptchaTestSite/scripts/soundfiles")

    args = [sFile, 'outfile.wav', 'silence',
        '1', '0.1', '0.1',
        '1', '0.1', '0.1',
        ': newfile', ': restart']

    sx.sox(args)

    # Creates Watson Speech to Text Object
    speech_engine = SpeechToTextV1(username=WATSON_USER,
                                   password=WATSON_PASS,
                                   x_watson_learning_opt_out=True)

    # Makes request to Speech to Text API
    # Prints response received from API
    with open('<testFile || outfile0**>' + '.wav', 'rb') as sourceFile:
        print(json.dumps(speech_engine.recognize(sourceFile,
                                                 content_type='audio/wav',
                                                 continuous=True,
                                                 model='en-UK_NarrowbandModel',
                                                 inactivity_timeout=5, indent=2)))

    config = {
        "database": {
            "host": "127.0.0.1",
            "user": "root",
            "passwd": "Meeseeks",
            "db": "dejavu",
        },
        "database_type": "mysql",
        "fingerprint_limit": -1
    }


    djv = Dejavu(config)

    for i in range(0, 10):
        djv.fingerprint_directory("soundfiles/" + str(i) + "/", [".wav"], 5)

    sx.sox(args)

    for piece in glob.glob("out*.wav"):
        song = djv.recognize(FileRecognizer, piece)
        print piece + " -- "
        print sonG


    #os.chdir("/Users/maxwellmackoul/Desktop/Recapture/Recapture2/reCaptchaTestSite/scripts/soundfiles")
    
    # delete files 
    for aFile in glob.glob("*.mp3"):
        os.remove(aFile)




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
