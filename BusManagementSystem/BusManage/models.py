from __future__ import unicode_literals
from django.contrib import admin
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator,validate_email
from random import randint
import datetime
from django.utils.crypto import get_random_string
import re
# Create your models here.


def validate_age(age):
	if age <= 3 and age>=0:
		raise ValidationError(
           _('Ticket not required for this age range'),
           params={'value': age},
    )


	if age<0:
		raise ValidationError(
           _('Invalid age'),
           params={'value': age},
    )
def verify_email(email):
	try:
	    validate_email(email)
	except ValidationError as e:
		raise ValidationError(
           _('invalid Email'),
           params={'value': email},
    )
	else:
	    print "hooray! email is validators"
		
	

def verifyPhoneNo(phoneNo):

	condition = (len(phoneNo)<10)

	if len(phoneNo)!= 10:
		raise ValidationError(
           _('invalid Phone Number'),
           params={'value': phoneNo},
    )

def validateName(name):
	
	condition = bool(re.match("^[a-zA-Z]+$", name))
	
	
	'''
	^ : start of string
	[ : beginning of character group
	a-z : any lowercase letter
	A-Z : any uppercase letter
	0-9 : any digit
	_ : underscore
	] : end of character group
	+ : one or more of the given characters - this will not allow empty string
	$ : end of string

	'''
	if not condition:
		raise ValidationError(
           _('invalid name'),
           params={'value': name},
    )


class Ticket(models.Model):
	PNR =  models.CharField(max_length=6,default=get_random_string(length=6),blank=True)
	price = models.CharField(max_length=10,default=randint(1,1000),blank=False)

class Passenger(models.Model):
	
	SEX = [("M","Male"),
			("F","Female"),
			("O","Other")]

	Email = models.CharField(max_length=30,blank=False,validators=[verify_email])
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be of 10 digits")

	'''
	The unique constraint for PhoneNumber is implemented by some checking if a user exists with the provided 
	phone number in our DB.

	'''

	PhoneNumber = models.CharField(max_length=10,validators=[phone_regex],blank=False) 
	
	'''
	add validation to first and last name
	'''
	FirstName = models.CharField(max_length=30,blank=False,validators=[validateName])
	LastName = models.CharField(max_length=30,blank=True,validators=[validateName])
	Sex = models.CharField(max_length=1,choices=SEX,blank=True)
	Age = models.IntegerField(validators=[validate_age],blank=False)
	pnrNo = models.ForeignKey(Ticket,unique=False)
	

class Booking(models.Model):

	PNR = models.ForeignKey(Ticket)
	#PNR = models.CharField(max_length=6,blank=False,default=randint(100000,999999),unique=True)
class Company(models.Model):
	modelNo = models.CharField(max_length=15,default="Volvo",blank=True)
	capacity = models.IntegerField(blank=True,default=180)
	registrationNumber = models.CharField(max_length=6,default=randint(1000,999999),blank=True,unique=True)
	companyName = models.CharField(max_length=20,blank=False)

class Buses(models.Model):	

	origin = models.CharField(max_length=50,blank=False)
	destination = models.CharField(max_length=50,blank=False)
	date = models.DateField(_("Date"),blank=False)
	busNum = models.CharField(max_length=50,blank=False)
	price = models.CharField(max_length=10,blank=False)
	arrivalTime = models.CharField(max_length=10,blank=False)
	departureTime = models.CharField(max_length=10,blank=False)
	seatsAvailable = models.IntegerField(default=180)
	companyName = models.ForeignKey(Company)

	class Meta:
		unique_together = (("busNum","date"))

class OperatedBy(models.Model):
	busNum = models.ForeignKey(Buses,related_name='BusManage_Buses_busNum')
	registrationNumber = models.ForeignKey(Company)
	dt = models.ForeignKey(Buses,blank=False,related_name='BusManage_Buses_date')

	class Meta:
		unique_together = (("busNum","dt"))

class IssuedFor(models.Model):
	PNR = models.ForeignKey(Ticket,unique=True)
	busNum = models.ForeignKey(Buses)