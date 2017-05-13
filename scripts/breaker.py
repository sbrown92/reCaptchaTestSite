import os
import sys
import json
import requests
from StringIO import StringIO
import re
import random
from datetime import datetime as dt

from sox import Transformer
from urllib import urlretrieve
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from watson_developer_cloud import SpeechToTextV1

from keys import WATSON_USER, WATSON_PASS


'''
Class Definition for Proxy handler
- Hold address and port
- Bool variable that denotes if proxy has failed before
'''
class Proxy(object):
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.hasFailed = False

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.address == other.address and self.port == other.port

#######################################
####                               ####
####   Constant Variables          ####
####                               ####
#######################################

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIREFOX_PATH = os.path.join(BASE_DIR, 'geckodriver')


#######################################
####                               ####
####   Functions                   ####
####                               ####
#######################################

#Get the URL and the form inputs from the user.
def getInputs():
    inputs = list()
    #urlAddress = raw_input("Please enter the page's URL: ")
    urlAddress = 'http://127.0.0.1:8000/'
    '''
    sys.stdout.write("Please enter the form's inputs (formatted ID:VALUE with spaces): ")
    sys.stdout.flush()
    line = sys.stdin.readline()
    for pair in line.split():
        values = pair.split(":")
        #TODO: Check if the id has already been set or not.
        inputs.append((values[0], values[1]))
    '''
    return urlAddress, inputs

#Web Scraper to pull proxy server addresses and port numbers.
def scraper():
    proxies = []

    print "Scraping for proxies"
    response = requests.get('http://spys.me/proxy.txt')
    response.raise_for_status()

    # Prep text file to be read
    f = response.text
    text = StringIO(f)

    # Regular Expressions to find data from text file
    proxyPattern = r'\d*.\d*.\d*.\d*:\d*'
    countryPattern = r'\D{2}-'

    for line in text:
        address = re.match(proxyPattern, line)
        country = re.search(countryPattern, line)

        if address:
            address, port = address.group().split(':')

            if 'US' in country.group():
                # Check if Google Passed
                if '+' in line:
                    port = int(port)  # Since we typecast it when we set prefs
                    proxy = Proxy(address=address, port=port)
                    proxies.append(proxy)

    text.close()

    print('Got {} workable proxies'.format(len(proxies)))
    return proxies


### Set the web browser's proxy settings.
def getProfile(pool):
    prefs = FirefoxProfile()
    random.shuffle(pool)
    i = 0
    proxy = pool[i]
    while proxy.hasFailed:
        i += 1
        proxy = pool[i]

    print('Server: {0}\nPort: {1}'.format(proxy.address, proxy.port))

    # Write proxy info to log file
    with open('WatsonResponse.txt', 'a') as logFile:
        time = dt.now().strftime('%b %d, %Y @ %H:%M:%S')
        logFile.write('--------------Pass at {}--------------\n'.format(time))
        logFile.write('Address: {0}\nPort: {1}\n'.format(proxy.address,
                                                         proxy.port))

    prefs.set_preference('network.proxy.type', 1)
    prefs.set_preference('network.proxy.share_proxy_settings', True)
    prefs.set_preference('network.http.use-cache', False)
    prefs.set_preference('network.proxy.http', proxy.address)
    prefs.set_preference('network.proxy.http_port', proxy.port)
    prefs.set_preference('network.proxy.ssl', proxy.address)
    prefs.set_preference('network.proxy.ssl_port', proxy.port)
    prefs.set_preference('network.proxy.socks', proxy.address)
    prefs.set_preference('network.proxy.socks_port', proxy.port)

    return prefs, proxy


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

    # Write API response document to a text file for logging
    with open('WatsonResponse.txt', 'a') as logFile:
        i = 0
        for result in results:
            log = str(result['alternatives'])
            logFile.write('{0}. {1}\n'.format(i, log))
            i += 1

        answer = ''

        for result in results:
            word = str(result['alternatives'][0]['transcript'])
            word = word.strip()

            num = numMap.get(word, '?')
            answer += num

        logFile.write('Answer: {}\n'.format(answer))

    return answer


def automatePage(fireFoxPath, prefs, address, inputList):



    #Automate interactions with widget.
    #Webdriver creation
    br = webdriver.Firefox(executable_path=fireFoxPath, firefox_profile=prefs)
    wait = WebDriverWait(br, 15)
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
    urlretrieve(finalLink, BASE_DIR + "/audio.mp3")

    return br

def submitAnswer(br, answer):
    ##########################
    ### Parse API Output   ###
    ##########################
    wait = WebDriverWait(br, 15)
    print "Answer - " + answer
    sleep(10)
    for c in answer:
        br.find_element_by_id('audio-response').send_keys(c)
        sleep(1)


    sleep(2)
    wait.until(EC.element_to_be_clickable((By.ID, 'recaptcha-verify-button')))
    br.find_element_by_id('recaptcha-verify-button').click()
    sleep(3)


#######################################
####                               ####
####   Main Function               ####
####                               ####
#######################################

def main():
    numCorrect = 0;
    trials = 1;
    proxyPool = scraper()
    while trials <= 100:
        try:
            fileName = "audio"
            sx = Transformer()
            prefs, curProxy = getProfile(proxyPool)
            urlAddr, inputs = getInputs()
            browser = automatePage(fireFoxPath=FIREFOX_PATH, prefs=prefs, address=urlAddr, inputList=inputs)

            ##########################
            ### Convert Audio File ###
            ##########################
            print "Converting Audio File"
            sx.build(fileName + ".mp3", fileName + ".wav")

            answer = getAnswer(fileName)

            if answer == '?':
                for proxy in proxyPool:
                    if proxy == curProxy:
                        proxy.hasFailed = True

            else:
                submitAnswer(browser, answer)

        except Exception as e:
            print "Error: " + str(e)

        wait = WebDriverWait(browser, 15)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[text()='Multiple correct solutions required - please solve more.']")))
            print "Fail."
        except:
            print "Pass."
            numCorrect += 1

        try:
            browser.close()
        except Exception as e:
            print "Error " + str(e)

        print "current correct - " + str(numCorrect)
        trials += 1

    print "Final Correct -- " + str(numCorrect)
if __name__ == "__main__":
    main()
