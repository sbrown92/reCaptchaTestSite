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

		return render(request, 'home/result.html')




	
