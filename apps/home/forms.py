from django import forms

class TestForm(forms.Form):
	answer = forms.CharField(label='testAnswer', max_length=15)