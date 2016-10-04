#!test1/core/utils.py

from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.db import transaction
import requests

from test1.core.forms import SubmitNewUser, RemoveUser, SendMessage
from test1.core.models import User, Event, Broadcast, InboundMessage

@transaction.atomic
def add_user(request, logger):
	""" add_user is called by the registration page via POST request.
	It collects the form data from a SubmitNewUser form to add a user to the
	database. It first checks if the number provided is already listed in the
	database, and adds the user if it is not.
	"""
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
			e.save()
			logger.info("New user added to database: (%s)." % u)
			messages.success(request, "User added! You will receive a verification message shortly!")
			# Prepare and send a message to confirm the new user's number
			verify_user(u)
		else:
			logger.info("Attempt to add existing user")
			messages.warning(request, "That number is already in our system.")
	else:
		messages.error(request, "Please fill out the required fields.")

@transaction.atomic
def remove_user(request, logger):
	form = RemoveUser(request.POST)
	if form.is_valid():
		# validate the form and check if there's a matching user
		number = form.cleaned_data['number']
		user_to_remove = User.objects.filter(number=number).get()
		if user_to_remove:
			logger.info("Removing user from database: (%s)." % user_to_remove)
			u_id = user_to_remove.id
			user_to_remove.delete()
			messages.success(request, "You have been removed from our database.")
			e = Event(type="remove_user",
				time_occurred=datetime.now(),
				user_id=u_id)
			e.save()
		else:
			messages.warning(request, "Sorry, we do not have a listing for that number.")


def save_outbound_to_db(message):
	"""Save a message to the core_broadcast table."""
	om = Broadcast(content=message)
	om.save()

def save_inbound_to_db(message, number, logger):
	"""Save a message to the core_inboundmessage table."""
	u = User.objects.filter(number=number)
	uid = None
	if u:
		u = u.get()
		uid = u.id
	im = InboundMessage(content=message, sender_num=number,
						sender_id=uid)
	im.save()


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
	gen_params = ('?companykey=%s&username=%s&password=%s&stop=no&messagebody=%s'
				 % (settings.MOZEO_COMPANY_KEY, settings.MOZEO_USERNAME,
				 	settings.MOZEO_PASSWORD, message) )
	now = datetime.now()
	for user in users:
		param_str = gen_params + '&to=' + user.number
		requests.get(settings.MOZEO_PROD_URL + param_str)
		e = Event(type="send_message",
			time_occurred=now,
			user_id=user.id,)
		e.save()

def verify_user(user):
	verify_str = ("Hello! Your number has been signed up to receive messages "
				  "from Global Heartbeat! To confirm, include 'Heartbeat' in your reply!")
	send_to_users([user], verify_str)
