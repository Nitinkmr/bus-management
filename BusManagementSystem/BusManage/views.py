from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import PassengerForm,Selectbus,getNumPassengers
from .models import Buses,Ticket,Passenger,Booking,IssuedFor,Company,OperatedBy
import json
import requests
import datetime
from django.contrib import messages
from django.contrib.messages import get_messages
from django.utils.crypto import get_random_string
from random import randint
# Create your views here.

api_key = "AIzaSyCa1Oko5VirJeqaSpC7GXGeFTU5vBzS5a8"
url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=" + api_key
headers = {'content-type': 'application/json'}
global users 
users = None

def PassengerDetails(request,numPassengers):

	#print request.method
	if request.method == "POST":
		form = PassengerForm(request.POST)
		print "form"
		print form.is_valid()

		if form.is_valid():
			formData = form.cleaned_data
			request.session["phoneNumber"] = formData["PhoneNumber"]
			print formData
			if 'passengerForm' not in request.session:
				request.session["passengerForm"] = []
				users = []
			user = {
					'Email':formData["Email"],
					'PhoneNumber':formData["PhoneNumber"],
					'FirstName':formData["FirstName"],
					'LastName':formData["LastName"],
					'Sex':formData["Sex"],
					'Age':formData["Age"]
					}
			
			global users
			if users == None:
				users = []
			users.append(user)	
			numPassengers = int(numPassengers)
			numPassengers = numPassengers - 1
			
			if numPassengers == 0:
				return HttpResponseRedirect('/BusManage/displayTicket') 
			else:
				return HttpResponseRedirect('/BusManage/passengerDetails/' + str(numPassengers))
	
		#	request.session["passengerForm"] = formData
		
		#	return HttpResponseRedirect('/BusManage/displayTicket') 
	else:
		form = PassengerForm()

	return render(request, 'passengerDetails.html', {'form': form})

def FromAndTo(request):

	if request.method == "POST":
		form = Selectbus(request.POST)
		print "form"
		print form.is_valid()
		if form.is_valid():			
			data = form.cleaned_data
			FromBusStop = data['origin']
			ToBusStop = data['destination']
			Date = data['Date']
			 
			try:
				request.session['origin'] = FromBusStop
				request.session['destination'] = ToBusStop
				request.session['date'] = Date.strftime("%Y-%m-%d")
			except Exception as e:
				print(e)

			return HttpResponseRedirect('/BusManage/displayBuses') 
		


	else:
		form = Selectbus()

	return render(request, 'index.html', {'form': form})

def displayBuses(request):
	
	'''
	if required Bus is in DB, show from there only, else proceed as follows
	'''
	origin = request.session.get('origin')
	destination = request.session.get('destination')
	date = request.session.get('date')

	buses = Buses.objects.all().filter(origin=origin,destination=destination,date=date)
	print buses
	if len(buses)>0:
		
		result = []
		for Bus in buses:
			temp = {
					"rate": Bus.price,
					"departureTime":Bus.departureTime,
					"arrivalTime":Bus.arrivalTime,
					"busNum":Bus.busNum
			}

			result.append(temp)
	else:
		params = {
			  "request": {
			    "slice": [
			      {
			        "origin": origin,
			        "destination": destination,
			        "date": date
			      }
			    ],
			    "passengers": {
			      "adultCount": 1
			    },
			    "solutions": 3,
			    "refundable": False
			  }
			}
	
		response = requests.post(url, data=json.dumps(params), headers=headers)
		data = response.json()
		data = json.dumps(data)
		


		buses = data
		buses = json.loads(buses)
		print buses
		buses = buses["trips"]
		print buses
		if 'tripOption' in buses:
			buses = buses["tripOption"]	
		else:
			print "Buses dont exist"			
			return render(request, 'displayBuses.html', {'error': "no Buses scheduled fot the given specification",'Buses':''})
		


		#print Buses
		result = []
		Companys = Company.objects.all()
		x = 0
		for Bus in buses:
			temp = {
					"rate": Bus['saleTotal'],
					"departureTime":Bus['slice'][0]['segment'][0]['leg'][0]['departureTime'],
					"arrivalTime":Bus['slice'][0]['segment'][0]['leg'][0]['arrivalTime'],
					"busNum":Bus['slice'][0]['segment'][0]['flight']['number']
			}

			print temp
			try:
				
				new_Bus = Buses(origin=request.session.get('origin'),destination=request.session.get('destination'),date=request.session.get('date'),busNum=temp['busNum'],price=temp['rate'],arrivalTime=temp['arrivalTime'],departureTime = temp['departureTime'],companyName=Companys[x])
				new_Bus.save()
				result.append(temp)
				
				form = OperatedBy(busNum=new_Bus,registrationNumber=Companys[x],dt=new_Bus)
				form.save()
				x = x+1
			except Exception as e:
				print(e)
	
	return render(request, 'displayBuses.html', {'Buses': result})
	
def displaySelectedBus(request,busNum):
	#print busNum
	Bus = Buses.objects.all().filter(busNum=busNum)
	result = {
				"rate": Bus[0].price,
				"departureTime":Bus[0].departureTime,
				"arrivalTime":Bus[0].arrivalTime,
				"busNum":Bus[0].busNum		
	}
	request.session['busNum'] = busNum
	return render(request, 'displaySelectedBus.html', {'bus': result})
	
def ticket(request):

	busNum = request.session.get('busNum')
	passengerForm = request.session.get('passengerForm')
	Bus =  Buses.objects.all().filter(busNum=busNum)
	pnr = get_random_string(length=6).upper()
	
	
	try:
		#save ticket#
		newTicket = Ticket(PNR=pnr,price=Bus[0].price)
		newTicket.save()

		#save IssuedFor#
	
		form = IssuedFor(PNR=newTicket,busNum=Bus[0])
		form.save()
		#passenger = Passenger.objects.all().filter(PhoneNumber=request.session.get("phoneNumber"))

			#save booking# 
		form = Booking(PNR=newTicket)
		form.save()
		print "users in ticket"	
		print users
		#save passenger#
		for passenger in users:

			age = passenger["Age"]
			sex = passenger["Sex"]
			firstName = passenger["FirstName"]
			lastName = passenger["LastName"]
			phoneNumber = passenger["PhoneNumber"]
			email = passenger["Email"]

			newPassenger = Passenger(Email=email,PhoneNumber=phoneNumber,FirstName=firstName,LastName=lastName,Sex=sex,Age=age,pnrNo=newTicket)	
			newPassenger.save()
		global users	
		users = []
	

		
	except Exception as e:
		print(e)
	return render(request, 'displayTicket.html', {'busNum': busNum,'pnr':pnr,'price':Bus[0].price})
	
def numPassenger(request):

	if request.method =="POST":
		form = getNumPassengers(request.POST)

		if form.is_valid():
			form = form.cleaned_data
			request.session["numPassengers"] = form["numOfPassengers"]
			return HttpResponseRedirect('/BusManage/passengerDetails/' + request.session["numPassengers"])
	else:
		form = getNumPassengers()

	return render(request, 'index.html', {'form':form})
	