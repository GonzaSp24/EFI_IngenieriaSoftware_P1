from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Define aquí tus funciones de vista para vuelos
def lista_vuelos(request):
    return render(request, 'vuelos/lista_vuelos.html', {})

def detalle_vuelo(request, pk):
    return render(request, 'vuelos/detalle_vuelo.html', {})
