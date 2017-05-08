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

from keys import WATSON_USER, WATSON_PASS


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
    proxies = []

    print "Scraping for proxies"
    source = urlopen('http://proxydb.net/?protocol=https&country=US&\
                      availability=75&response_time=10')

    bs = BeautifulSoup(source, "html.parser")

    # Get the table of proxies from the HTML
    table = bs.select('tbody tr')

    # Parse through rows to find information
    for row in table:
        # Get Country information
        country = row.find_all('img')[0].get('title')

        # We only wants proxies from the US
        if 'US' not in country:
            print('Not working with {}...'.format(country))
            continue

        else:
            # Get Proxy Information
            data = row.find_all('a')[0].getText().split(':')
            proxies.append(data)

            print('-----Got a live one!-----\n\
                   Country: {0}\n\
                   Host: {1}\n\
                   Port: {2}\n'.format(country, data[0], data[1]))

    return proxies


### Set the web browser's proxy settings.
def getProfile(pool):
    prefs = FirefoxProfile()

    pool.pop()
    server, host = pool.pop()
    print('Server: {0}\nHost: {1}'.format(server, host))
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


def automatePage(fireFoxPath, prefs, address, inputList):



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
    urlretrieve(finalLink, BASE_DIR + "/audio.mp3")

    return br

def submitAnswer(br, answer):
    ##########################
    ### Parse API Output   ###
    ##########################
    print "Answer - " + answer
    sleep(15)
    for c in answer:
        br.find_element_by_id('audio-response').send_keys(c)
        sleep(1)


    sleep(2)
    wait.until(EC.element_to_be_clickable((By.ID, 'recaptcha-verify-button')))
    br.find_element_by_id('recaptcha-verify-button').click()
    sleep(3)
    br.close()
    br.quit()


#######################################
####                               ####
####   Main Function               ####
####                               ####
#######################################

def main():
    fileName = "audio"
    sx = Transformer()
    proxyPool = scraper()
    prefs = getProfile(proxyPool)
    urlAddr, inputs = getInputs()
    browser = automatePage(fireFoxPath=FIREFOX_PATH, prefs=prefs, address=urlAddr, inputList=inputs)
    ##########################
    ### Convert Audio File ###
    ##########################
    print "Converting Audio File"
    sx.build(fileName + ".mp3", fileName + ".wav")


    answer = getAnswer(fileName)

    submitAnswer(browser, answer)


if __name__ == "__main__":
    main()
