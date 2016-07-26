from django import forms

class SubmitNewUser(forms.Form):
	first_name = forms.CharField(max_length=20)
	last_name = forms.CharField(max_length=30, required=False)
	number = forms.CharField(max_length=20)
	email = forms.CharField(max_length=255, required=False)
	confirm_email = forms.CharField(max_length=255, required=False)

class RemoveUser(forms.Form):
	number = forms.CharField(max_length=20,
							 label='Remove a number from our database')