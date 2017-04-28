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
from selenium.webdriver.common.proxy import *
from watson_developer_cloud import SpeechToTextV1

from keys import WATSON_USER, WATSON_PASS


#######################################
####                               ####
####   Variable Declarations       ####
####                               ####
#######################################

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIREFOX_PATH = os.path.join(BASE_DIR, 'geckodriver')



#######################################
####                               ####
####   Functions                   ####
####                               ####
#######################################

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


def automatePage(fireFoxPath, prefs):
    # Watson API Settings.
    speech_engine = SpeechToTextV1(
        username=WATSON_USER,
        password=WATSON_PASS,
        x_watson_learning_opt_out=True)

    numMap = {
        'zero': '0',
        'one': '1',
        'two': '2',
        'three': '3',
        'four': '4',
        'five': '5',
        'six': '6',
        'seven': '7',
        'eight': '8',
        'nine': '9',
    }

    keywords = numMap.keys()

    #Automate interactions with widget.
    #Webdriver creation
    br = webdriver.Firefox(executable_path=fireFoxPath, firefox_profile=prefs)
    wait = WebDriverWait(br, 5)
    br.get(url)
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

    # gets the link fo the file
    audiolink = br.find_elements_by_xpath("//a[@href]")
    for link in audiolink:
        print link.get_attribute("href")
        finalLink = link.get_attribute("href")
        print finalLink

    #Download Audio File
    urlretrieve(finalLink, BASE_DIR + "/" + fileName + ".mp3")

    #Convert file from .mp3 to .wav
    sx.build(fileName + ".mp3", fileName + ".wav")

    #Speech To Text
    with open(fileName + '.wav', 'rb') as sourceFile:
        data = speech_engine.recognize(sourceFile, content_type='audio/wav',
                                       continuous=True,
                                       model='en-UK_NarrowbandModel',
                                       inactivity_timeout=5, keywords=keywords,
                                       keywords_threshold=.25)

    results = data['results']
    numNums = []

    for result in results:
        word = str(result['alternatives'][0]['transcript'])
        word = num.strip()
        
        num = numMap.get(word, '?')
        numNums.append(str(num))

    answer = ''.join(numNums)

#######################################
####                               ####
####   Variable Declarations       ####
####                               ####
#######################################
url = raw_input("Please enter the URL: ")
sys.stdout.write("Please enter the form inputs (id:value): ")
sys.stdout.flush()
formInputs = sys.stdin.readline()

fileName = "audio"
sx = Transformer()

proxyPool = scraper()
prefs = getProfile(proxyPool)

automatePage(fireFoxPath=FIREFOX_PATH, prefs=prefs)
