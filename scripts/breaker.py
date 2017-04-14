from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import os
Base_Dir = os.path.dirname(os.path.abspath(__file__))
import time 


fireFoxPath = '/Users/maxwellmackoul/Selenium/geckodriver'
prefs = FirefoxProfile()
prefs.set_preference("browser.altClickSave", True)

#br = webdriver.Chrome(chromePath)
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
time.sleep(5)
wait.until(EC.element_to_be_clickable((By.ID, 'recaptcha-audio-button'))).click()

wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'rc-audiochallenge-download-link')))
wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'rc-audiochallenge-download-link'))).click()

