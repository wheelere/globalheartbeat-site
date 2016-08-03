# views.py

from datetime import datetime
from django.shortcuts import render, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from django.db import transaction
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from test1.core.models import User, Event
from .forms import SubmitNewUser, RemoveUser

import requests
import logging

logger = logging.getLogger('core.views.logger')

def send_to_users(users, message):
	""" send_to_users takes a list of User models and a message to send. It
	constructs a url with parameters to make a GET request in order to have that
	message be sent to the phone numbers corresponding to the list of users.
	Currently, this function is configured for use with the Mozeo API. 
	Note that 'settings.MOZEO_*_URL' determines whether the GET request is sent to
	a dummy URL or a Production URL. In the first case, the sent messages will only
	appear in the API Report section of Mozeo's dashboard. In the second case,
	a text message will actually be sent to all numbers.
	"""
	gen_params = '?companykey=%s&username=%s&password=%s&messagebody=%sstop=no' % (settings.MOZEO_COMPANY_KEY, settings.MOZEO_USERNAME, settings.MOZEO_PASSWORD, message)
	for user in users:
		param_str = gen_params + '&to=' + user.number
		requests.get(settings.MOZEO_DEV_URL + param_str)

def verify_user(user):
	verify_str = ("Hello! Your number has been signed up to receive messages "
				  "from Global Heartbeat! To confirm that you would like to "
				  "receive these messages, reply 'SJBKXG' to this number.")
	send_to_users([user], verify_str)

def home(request):
	""" This function renders the index.html page with the SubmitNewUser form
	specified in forms.py.
	"""
	# Grab the forms here
	new_form = SubmitNewUser()
	remove_form = RemoveUser()
	# Create a context for the request, and add the forms to it as well
	context = { 'new_form': new_form, 'remove_form': remove_form }
	# render our template
	return render(request, 'index.html', context=context)

def send_sms(request):
	""" This function is called at the /send url extension (see urls.py).
	If it was accessed via POST, it collects a list of users from the database
	and prepares a message. It passes this information to the send_to_users to
	be processed with an external texting service (CURRENTLY: MOZEO).
	Regardless, it completes by redirecting to the root url.
	"""
	if request.method == "POST":
		# Get the phone numbers to use
		users = User.objects.all()
		# dummy message for now
		message = "Hello, World!"
		# pass the users and message to the send function
		send_to_users(users, message)
		messages.success(request, "Message sent!")
		
	# For now, return to the home page
	return HttpResponseRedirect('/')

@transaction.atomic # guarantee atomicity of the database
def add_user(request):
	""" add_user is called when the /adduser url is landed on.
	It collects the form data from a SubmitNewUser form to add a user to the
	database. It first checks if the number provided is already listed in the
	database, and adds the user if it is not.
	Finally, it redirects to the root url.
	"""
	if request.method == "POST":
		form = SubmitNewUser(request.POST)
		if form.is_valid():
			# Create a new User based on form data
			first = form.cleaned_data['first_name']
			last = form.cleaned_data['last_name']
			number = form.cleaned_data['number']
			email = form.cleaned_data['email']
			u = User(first=first, last=last, number=number)
			# Handle email address
			if email:
				if form.cleaned_data['confirm_email'] == email:
					# TODO: validate email addresses
					u.email = email;

			# Check that there isn't already a copy of that number in the DB
			existing = User.objects.filter(number=number)
			if not existing:
				u.save()
				e = Event(type="add_user",
					time_occurred=datetime.now(),
					user_id=u.id)
				logger.info("New user added to database (" + u + ").")
				messages.success(request, "User added!")
			else:
				logger.info("")
				messages.warning(request, "That number is already in our system.")
		else:
			messages.error(request, "Please fill out the required fields.")
	# For now, return to the home page
	return HttpResponseRedirect('/')

@transaction.atomic
def remove_user(request):
	""" remove_user is invoked when the /removeuser url is landed on.
	It collects and validates the form data from the RemoveUser form, then
	attempts to remove that number from our database.
	"""
	if request.method == "POST":
		form = RemoveUser(request.POST)
		if form.is_valid():
			user_to_remove = User.objects.filter(number=form.cleaned_data['number'])
			if user_to_remove:
				user_to_remove.delete()
				messages.success(request, "You have been removed from our database.")
			else:
				messages.warning(request, "Sorry, we do not have a listing for that number.")
	# TODO: interact with user: alert regarding results or errors
	return HttpResponseRedirect('/')

@csrf_exempt
@transaction.atomic
def handle_inbound(request):
	""" handle_inbound is called when a POST request is made to the /inbound
	url from an external source (CURRENTLY MOZEO). The request received will 
	contain XML data including a static keyword, and the request will be handled
	correspondingly.
	"""
	logger.info("Received Inbound Request.")
	if request.method == "POST":
		for key, value in request.POST.iteritems():
			logger.info( "%s %s" % (key, value) )
		# message = request.POST.get("IncomingMessage")
		# number = request.POST.get("Phonenumber")
		# if "SJBKXG" in message:
		# 	u = User.objects.filter(number=number)
		# 	try:
		# 		u = u.get()
		# 	except DoesNotExist:
		# 		logger.warning("Received inbound verify from an unlisted number.")
		# 		return HttpResponseRedirect('/')
		# 	except MultipleObjectsReturned:
		# 		logger.error("The number " + number + " has multiple User listings.")
		# 		return HttpResponseRedirect('/')
		# 	u.verified = True
		# 	u.save()
		# 	e = Event(type="verify_user",
		# 		time_occurred=datetime.now(),
		# 		user_id=u.id)
		# 	e.save()
	return HttpResponseRedirect('/')
