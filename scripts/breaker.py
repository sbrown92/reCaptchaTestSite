from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
Base_Dir = os.path.dirname(os.path.abspath(__file__))
chromePath = '/Users/Sam/Selenium/chromedriver'
chromeOptions = Options()

chromeOptions.add_argument("--disable-extensions")


br = webdriver.Chrome(chromePath, chrome_options=chromeOptions)

br.get('http://127.0.0.1:8000')
br.find_elements_by_tag_name('iframe')
iframe = br.find_elements_by_tag_name('iframe')[0]

br.switch_to_frame(iframe)
br.find_element_by_class_name('recaptcha-checkbox-checkmark').click()
br.switch_to_default_content()
br.switch_to_frame(br.find_elements_by_tag_name('iframe')[1])
br.implicitly_wait(10)
br.find_element_by_id('recaptcha-audio-button').click()
br.find_elements_by_class_name('rc-audiochallenge-download-link')[0].click()
#br.close()