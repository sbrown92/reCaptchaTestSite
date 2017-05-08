import os.path
import sys
import json
import threading

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

from keys import WATSON_USER, WATSON_PASS


#######################################
####                               ####
####   Constant Variables          ####
####                               ####
#######################################

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIREFOX_PATH = os.path.join(BASE_DIR, 'geckodriver')



class browserThread(threading.Thread):
    def __init__(self, threadID, threadName, counter, url, inputs, proxyPool):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = threadName
        self.counter = counter
        self.prefs = getProfile(proxyPool)
        self.addr = url
        self.input_list = inputs
        self.fileName = threadName

    def run(self):
        print "starting thread"
        automatePage(prefs=self.prefs, address=self.addr, inputList=self.input_list, fileName=self.fileName)
        print "End of thread"




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
    print "Scraping for proxies"
    source = urlopen('http://www.proxydb.net/?protocol=https&country=US&availability=75&response_time=10')

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


def getAnswer(fileName):
    # Watson API Settings.
    speech_engine = SpeechToTextV1(
        username=WATSON_USER,
        password=WATSON_PASS,
        x_watson_learning_opt_out=True)

    numMap = {
        'zero': '0',
        'one': '1',
        'worn': '1',
        'two': '2',
        'to': '2',
        'who': '2',
        'do': '2',
        'three': '3',
        'four': '4',
        'for': '4',
        'hello': '4',
        'five': '5',
        'by': '5',
        'hi': '5',
        'I': '5',
        'six': '6',
        'fix': '6',
        'thanks': '6',
        'see': '6',
        'seven': '7',
        'eight': '8',
        'hey': '8',
        'a': '8',
        'nine': '9',
        'none': '9'
    }




    print "Sending to API..."
    with open(fileName + ".wav", 'rb') as sourceFile:
        data = speech_engine.recognize(sourceFile, content_type='audio/wav',
                                       continuous=True,
                                       model='en-US_NarrowbandModel',
                                       inactivity_timeout=5)
    print "Parsing Results..."
    results = data['results']
    answer = ""

    for result in results:
        word = str(result['alternatives'][0]['transcript'])
        word = word.strip()

        num = numMap.get(word, '?')
        answer += num


    return answer


def DownloadAudioFile(br):
    wait = WebDriverWait(br, 5)
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
    urlretrieve(finalLink, BASE_DIR + "/audio.mp3")

    return br

def submitAnswer(br, answer):
    ##########################
    ### Parse API Output   ###
    ##########################
    wait = WebDriverWait(br, 15)
    print "Answer - " + answer
    sleep(15)
    for c in answer:
        print type(c)
        br.find_element_by_id('audio-response').send_keys(c)
        sleep(1)


    sleep(2)
    wait.until(EC.element_to_be_clickable((By.ID, 'recaptcha-verify-button')))
    br.find_element_by_id('recaptcha-verify-button').click()
    sleep(3)
    br.close()
    br.quit()


def convertAudio(fileName):
    sx = Transformer()
    ##########################
    ### Convert Audio File ###
    ##########################
    print "Converting Audio File"
    sx.build(fileName + ".mp3", fileName + ".wav")

    return


def automatePage(prefs, address, inputList, fileName):
    # Automate interactions with widget.
    # Webdriver creation
    br = webdriver.Firefox(executable_path=FIREFOX_PATH, firefox_profile=prefs)
    fileName = "audio"
    print "Loading page " + address
    br.get(address)

    ####################
    ### Fill in Form ###
    ####################

    print "Filling out Form"
    for input in inputList:
        br.find_element_by_id(input[0]).send_keys(input[1])

    DownloadAudioFile(br)
    convertAudio(fileName)
    answer = getAnswer(fileName)
    submitAnswer(br, answer)





#######################################
####                               ####
####   Main Function               ####
####                               ####
#######################################

def main():

    proxyPool = scraper()
    url, list = getInputs()

    thread1 = browserThread(1, 'thread-1', 1, url, list, proxyPool)

    thread1.start()

    print "exiting main"


    '''
    prefs = getProfile(proxyPool)
    urlAddr, inputs = getInputs()
    automatePage(prefs=prefs, address=urlAddr, inputList=inputs)
    '''



if __name__ == "__main__":
    main()
