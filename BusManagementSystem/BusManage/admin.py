from django.contrib import admin
from .models import Passenger,Buses,Company,OperatedBy,Ticket,Booking,IssuedFor
# Register your models here.
admin.site.register(Passenger)
admin.site.register(Buses)
admin.site.register(Company)
admin.site.register(OperatedBy)
admin.site.register(Ticket)
admin.site.register(Booking)
admin.site.register(IssuedFor)
