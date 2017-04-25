import urllib
import sox
import os.path
import time
import json
from bs4 import BeautifulSoup, SoupStrainer

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from watson_developer_cloud import SpeechToTextV1



Base_Dir = os.path.dirname(os.path.abspath(__file__))


fileName = "audio"
sx = sox.Transformer()

speech_engine = SpeechToTextV1(
    username=WATSON_USER,
    password=WATSON_PASS,
    x_watson_learning_opt_out=True
)

fireFoxPath = '/Users/sam/Selenium/geckodriver'
prefs = FirefoxProfile()
prefs.set_preference("browser.altClickSave", True)

br = webdriver.Firefox(firefox_profile=prefs, executable_path=fireFoxPath)
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
time.sleep(1)
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
urllib.urlretrieve(finalLink, Base_Dir + "/" + fileName + ".mp3")

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


