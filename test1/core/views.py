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
from .forms import SubmitNewUser, RemoveUser, SendMessage

import logging
import xmltodict
import test1.core.utils as utils

logger = logging.getLogger('core.views.logger')

def contactus(request):
	return render(request, 'contactus.html')

def history(request):
	return render(request, 'history.html')

def home(request):
	"""This function renders the landing page."""
	return render(request, 'index.html')

@transaction.atomic # guarantee atomicity of the database
def register(request):
	"""Renders the registration page."""
	# maybe handle add_user here as well
	form = SubmitNewUser()
	if request.method == "POST":
		utils.add_user(request, logger)
	return render(request, 'register.html', {'form': form})

def remove(request):
	"""Renders the removal page and handles user removal requests."""
	if request.method == "POST":
		utils.remove_user(request, logger)
	else:
		form = RemoveUser()
	return render(request, 'remove.html', {'form': form})

def outbound_message(request):
	"""Renders the outbound message page and handles sending a message to the
	users.
	"""
	if request.method == "POST":
		form = SendMessage(request.POST)
		if form.is_valid():
			# Get the phone numbers to use
			users = User.objects.filter(verified=True)
			# get message from form
			message = form.cleaned_data['message']
			# pass the users and message to the send function
			utils.send_to_users(users, message, is_public=True)
			messages.success(request, "Message sent!")
	else:
		form = SendMessage()
	return render(request, 'send_message.html', {'form': form})

@csrf_exempt # Necessary to allow external POST requests
@transaction.atomic
def handle_inbound(request):
	""" handle_inbound is called when a POST request is made to the /inbound
	url from an external source (CURRENTLY MOZEO). The request received will 
	contain XML data including a static keyword, and the request will be handled
	correspondingly.
	"""
	if request.method == "POST":
		dict = xmltodict.parse(request.POST.get("XMLDATA"))
		message = dict["IncomingRequest"]["IncomingMessage"]["Message"]
		number = dict["IncomingRequest"]["IncomingMessage"]["Phonenumber"]
		logger.info("Received Message from number '%s'. \nMessage is: '%s'"
					% (number, message))
		utils.save_inbound_to_db(message, number)
		if "harmony" in message.lower():
			u = User.objects.filter(number=number)
			try:
				u = u.get()
			except DoesNotExist:
				logger.warning("Received inbound verify from unlisted number: %s." % number)
				return HttpResponseRedirect('/')
			except MultipleObjectsReturned:
				logger.error("The number " + number + " has multiple User listings.")
				return HttpResponseRedirect('/')
			u.verified = True
			u.save()
			e = Event(type="verify_user",
				time_occurred=datetime.now(),
				user_id=u.id)
			e.save()
	return HttpResponseRedirect('/')
