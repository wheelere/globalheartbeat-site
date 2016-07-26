from django import forms

class SubmitNewUser(forms.Form):
	first_name = forms.CharField(max_length=20)
	last_name = forms.CharField(max_length=30)
	number = forms.CharField(max_length=10)
	email = forms.CharField(max_length=255)
	confirm_email = forms.CharField(max_length=255)