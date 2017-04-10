from django.shortcuts import render
from .forms import TestForm
import urllib2
import urllib
import requests
import re
# Create your views here.

def homepage(request):

	counter = 0
	if request.method == 'GET':
		form = TestForm()

		value = "Not Sent!"
		return render(request, 'home/index.html', {'form': form, 'val': value, 'count': counter})
	elif request.method == 'POST':
		form = TestForm() 
		data = request.POST
		## gets the captcha response 
		captcha_rs = data.get('g-recaptcha-response')
		url = 'https://www.google.com/recaptcha/api/siteverify'
		params = {
			'secret': '6LeyyBcUAAAAAPh-4BiU6iac2nhF_jJV3QGUX1_9',
			'response': captcha_rs
		}

		result = requests.post(url, params=params)

		verify = recaptcha(request, data)

		"""Make condition that will check to see if request is verified"""

		if verify:

			counter +=1

			print ("SUCCESS!")

		else:


			print("FAILED TO LOG")




			##	count 

		"""If verifed, count"""

		"""else: error """

		"""GET DONE BY TUESDAY """




		content = result.content


		return render(request, 'home/result.html')


def recaptcha(request, postdata):
        rc_challenge = postdata.get('recaptcha_challenge_field','')
        rc_user_input = postdata.get('recaptcha_response_field', '').encode('utf-8')
        url = 'http://www.google.com/recaptcha/api/verify'
        values = {'privatekey' : 'PRIVATE-KEY', 'remoteip': request.META['REMOTE_ADDR'], 'challenge' : rc_challenge, 'response' : rc_user_input,}
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        answer = response.read().split()[0]
        response.close()
        return answer
		



	
