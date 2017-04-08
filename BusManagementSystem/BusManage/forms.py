from django.forms import ModelForm
from django import forms
from .models import Passenger,Buses
from .BusStops import get_BusStops
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms.extras.widgets import SelectDateWidget
import datetime

def validateDate(datePassed):

	if (datePassed.month >= (datetime.date.today().month+6)) :
		raise forms.ValidationError("Bookings can not be done for dates 6 months beyind the current date")


	if (datePassed<datetime.date.today()):
		raise forms.ValidationError("Invalid date")

class PassengerForm(ModelForm):

     class Meta:
         model = Passenger
         fields = ['PhoneNumber','Email','FirstName','LastName','Sex','Age']

class Selectbus(forms.Form):

	BusStops = get_BusStops()
	choices = [(BusStop['iata'],BusStop['name']) for BusStop in BusStops]
	
	origin = forms.ChoiceField(choices)
	destination = forms.ChoiceField(choices)
	Date = forms.DateField(initial=datetime.date.today,validators=[validateDate],widget=SelectDateWidget)
	

class Buses(ModelForm):
	
	class Meta:
		model = Buses
		fields = ['origin','destination','date','busNum','price','arrivalTime','departureTime']
	
class getNumPassengers(forms.Form):

	choices = [(x,x) for x in range(1,5)]
	numOfPassengers = forms.ChoiceField(choices)
	