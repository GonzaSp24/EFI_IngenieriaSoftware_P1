from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Define aquí tus funciones de vista para reservas
def crear_reserva(request, vuelo_id):
    return render(request, 'reservas/crear_reserva.html', {})

def detalle_reserva(request, codigo_reserva):
    return render(request, 'reservas/detalle_reserva.html', {})

def generar_boleto(request, codigo_reserva):
    return render(request, 'reservas/boleto_electronico.html', {})

def mis_reservas(request):
    return render(request, 'reservas/mis_reservas.html', {})
