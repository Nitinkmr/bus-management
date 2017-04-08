from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
 #   url(r'^$', views.index, name='index'),
    
    url(r'^/?$', views.FromAndTo),
    url(r'^displayBuses?$', views.displayBuses),
    url(r'^numpassenger?$', views.numPassenger),
    
    url(r'^([0-9]{1})/$', views.displaySelectedBus),
    url(r'^([0-9]{2})/$', views.displaySelectedBus),
    url(r'^([0-9]{3})/$', views.displaySelectedBus),
    url(r'^([0-9]{4})/$', views.displaySelectedBus),
    url(r'^([0-9]{5})/$', views.displaySelectedBus),
    url(r'^passengerDetails/([0-9]{1})?$', views.PassengerDetails),
    url(r'^displayTicket?$', views.ticket),
    #url(r'^/?$', views.PassengerDetails),
    url(r'^admin/', admin.site.urls),
       
]