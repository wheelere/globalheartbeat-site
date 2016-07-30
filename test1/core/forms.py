from django import forms

class SubmitNewUser(forms.Form):
	# see http://stackoverflow.com/questions/1254046/how-to-render-form-field-with-information-that-it-is-required
	# for an example of how to the 'required' tag with CSS
	required_css_class = 'required'
	first_name = forms.CharField(max_length=20, required=True)
	last_name = forms.CharField(max_length=30, required=False)
	number = forms.CharField(max_length=20, required=True)
	email = forms.CharField(max_length=255, required=False)
	confirm_email = forms.CharField(max_length=255, required=False)

class RemoveUser(forms.Form):
	number = forms.CharField(max_length=20,
							 label='Remove a number from our database')