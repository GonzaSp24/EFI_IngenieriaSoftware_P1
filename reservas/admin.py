from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Reserva, Boleto

admin.site.register(Reserva)
admin.site.register(Boleto)
