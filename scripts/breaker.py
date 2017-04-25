import os.path
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


#Web Scraper to pull proxy server addresses and port numbers.
def scraper():
    source = urlopen('http://proxydb.net/?protocol=https&country=US&availability=75&response_time=10')

    bs = BeautifulSoup(source, "html.parser")
    proxies = list()

    for cell in  bs.find_all('td'):
        for anchor in cell.find_all('a'):
            proxies.append(anchor.text.split(':'))

    return proxies

Base_Dir = os.path.dirname(os.path.abspath(__file__))


#Watson API Settings.
speech_engine = SpeechToTextV1(
    username=WATSON_USER,
    password=WATSON_PASS,
    x_watson_learning_opt_out=True
)

#Webdriver settings.
fireFoxPath = '/Users/sam/Selenium/geckodriver'
prefs = FirefoxProfile()
prefs.set_preference("browser.altClickSave", True)

fileName = "audio"
sx = Transformer()
proxyList = scraper()
br = webdriver.Firefox(firefox_profile=prefs, executable_path=fireFoxPath)

#Automate interactions with widget. 
wait = WebDriverWait(br, 5)
br.get('http://127.0.0.1:8000')
br.find_elements_by_tag_name('iframe')
iframe = br.find_elements_by_tag_name('iframe')[0]
iframe2 = br.find_elements_by_tag_name('iframe')[1]
br.switch_to_frame(iframe)
wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'recaptcha-checkbox-checkmark'))).click()
br.switch_to_default_content()
br.switch_to_frame(iframe2)
wait.until(EC.presence_of_element_located((By.ID, 'recaptcha-audio-button')))
sleep(1)
wait.until(EC.element_to_be_clickable((By.ID, 'recaptcha-audio-button'))).click()
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'rc-audiochallenge-download-link')))
wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'rc-audiochallenge-download-link'))).click()

# gets the link fo the file
audiolink = br.find_elements_by_xpath("//a[@href]")
for link in audiolink:
	#print link.get_attribute("href")
	finalLink = link.get_attribute("href")
	print finalLink

#Download Audio File
urlretrieve(finalLink, Base_Dir + "/" + fileName + ".mp3")

#Convert file from .mp3 to .wav
sx.build(fileName + ".mp3", fileName + ".wav")

#Speech To Text
with open(fileName + '.wav', 'rb') as sourceFile:
    print(json.dumps(speech_engine.recognize(sourceFile,
                                             content_type='audio/wav',
                                             continuous=True,
                                             model='en-UK_NarrowbandModel',
                                             inactivity_timeout=5),
                                             indent=2))

