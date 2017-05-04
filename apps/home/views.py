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


		return render(request, 'home/result.html')


	
