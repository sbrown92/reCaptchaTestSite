import os.path
import sys
import json

from bs4 import BeautifulSoup
from sox import Transformer
from urllib2 import urlopen
from urllib import urlretrieve
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from watson_developer_cloud import SpeechToTextV1


#######################################
####                               ####
####   Constant Variables          ####
####                               ####
#######################################

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIREFOX_PATH = os.path.join(BASE_DIR, 'geckodriver')
WATSON_USER = 'd136174d-690a-4baa-911d-1e759af84124'
WATSON_PASS = 'ODA1VLDPfRX4'


#######################################
####                               ####
####   Functions                   ####
####                               ####
#######################################

#Get the URL and the form inputs from the user.
def getInputs():
    inputs = list()
    urlAddress = raw_input("Please enter the page's URL: ")
    sys.stdout.write("Please enter the form's inputs (formatted ID:VALUE with spaces): ")
    sys.stdout.flush()
    line = sys.stdin.readline()
    for pair in line.split():
        values = pair.split(":")
        #TODO: Check if the id has already been set or not.
        inputs.append((values[0], values[1]))

    return urlAddress, inputs

#Web Scraper to pull proxy server addresses and port numbers.
def scraper():
    source = urlopen('http://proxydb.net/?protocol=https&country=US&availability=75&response_time=10')

    bs = BeautifulSoup(source, "html.parser")
    proxies = list()

    for cell in  bs.find_all('td'):
        for anchor in cell.find_all('a'):
            proxies.append(anchor.text.split(':'))
    return proxies


### Set the web browser's proxy settings.
def getProfile(pool):
    prefs = FirefoxProfile()

    pool.pop()
    server, host = pool.pop()
    prefs.set_preference('network.proxy.type', 1)
    prefs.set_preference('network.proxy.share_proxy_settings', True)
    prefs.set_preference('network.http.use-cache', False)
    prefs.set_preference('network.proxy.http', server)
    prefs.set_preference('network.proxy.http_port', int(host))
    prefs.set_preference('network.proxy.ssl', server)
    prefs.set_preference('network.proxy.ssl_port', int(host))
    prefs.set_preference('network.proxy.socks', server)
    prefs.set_preference('network.proxy.socks_port', int(host))

    return prefs


def automatePage(fireFoxPath, prefs, address, inputList):

    fileName = "audio"
    sx = Transformer()

    # Watson API Settings.
    speech_engine = SpeechToTextV1(
        username=WATSON_USER,
        password=WATSON_PASS,
        x_watson_learning_opt_out=True)
    keywords = [
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine"
    ]

    #Automate interactions with widget.
    #Webdriver creation
    br = webdriver.Firefox(executable_path=fireFoxPath, firefox_profile=prefs,)
    wait = WebDriverWait(br, 5)
    br.get(address)

    ####################
    ### Fill in Form ###
    ####################

    for input in inputList:
        br.find_element_by_id(input[0]).send_keys(input[1])


    ########################
    ### reCaptcha Widget ###
    ########################
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
    audiolink = br.find_elements_by_xpath("//a[@href]")
    for link in audiolink:
        print link.get_attribute("href")
        finalLink = link.get_attribute("href")
        print finalLink
    urlretrieve(finalLink, BASE_DIR + "/" + fileName + ".mp3")

    ######################
    ### Speech to Text ###
    ######################
    sx.build(fileName + ".mp3", fileName + ".wav")

    with open(fileName + '.wav', 'rb') as sourceFile:
        print(json.dumps(speech_engine.recognize(sourceFile,
                                     content_type='audio/wav',
                                     continuous=True,
                                     model='en-UK_NarrowbandModel',
                                     inactivity_timeout=5,
                                     keywords=keywords,
                                     keywords_threshold=.25)))





#######################################
####                               ####
####   Main Function               ####
####                               ####
#######################################
def main():
    proxyPool = scraper()
    prefs = getProfile(proxyPool)
    urlAddr, inputs = getInputs()
    automatePage(fireFoxPath=FIREFOX_PATH, prefs=prefs, address=urlAddr, inputList=inputs)



if __name__ == "__main__":
    print "here"
    main()