from __future__ import unicode_literals

from django.db import models

from datetime import datetime

class User(models.Model):
	# First Name of User
	first = models.CharField(max_length=20)
	# Last Name of User
	last = models.CharField(max_length=30)
	# US Cell Number of User
	number = models.CharField(max_length=20)
	# country code of user
	country_code = models.CharField(max_length=5, default='1')
	# Email Address
	email = models.CharField(max_length=255, default='')
	# Registration Date
	registration_date = models.DateTimeField(auto_now_add=True)
	# Verified User
	verified = models.BooleanField(default=False)

	def __str__(self):
		return self.first + ' ' + self.last + ', ' + self.number

class Event(models.Model):
	# Type of event. Current options:
	# * add_user
	# * remove_user
	# * send_message
	# * verify_user
	type = models.CharField(max_length=20)
	# Time of event.
	time_occurred = models.DateTimeField(auto_now_add=True)
	# User related to event
	user_id = models.IntegerField()

	def __str__(self):
		return self.type + '.' + self.user_id

