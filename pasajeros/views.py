from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Define aquí tus funciones de vista para pasajeros
def registrar_pasajero(request):
    return render(request, 'pasajeros/registrar_pasajero.html', {})

def historial_vuelos_pasajero(request, pk):
    return render(request, 'pasajeros/historial_vuelos_pasajero.html', {})
