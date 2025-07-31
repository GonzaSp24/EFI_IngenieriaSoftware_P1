from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Pasajero
from .forms import PasajeroForm
from reservas.models import Reserva # Importar Reserva para historial

def registrar_pasajero(request):
    """Vista para registrar un nuevo pasajero."""
    if request.method == 'POST':
        form = PasajeroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pasajero registrado exitosamente.')
            return redirect('lista_pasajeros')
    else:
        form = PasajeroForm()
    return render(request, 'pasajeros/registrar_pasajero.html', {'form': form})

def lista_pasajeros(request):
    """Vista para listar todos los pasajeros."""
    pasajeros_list = Pasajero.objects.all()
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        pasajeros_list = pasajeros_list.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(documento__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Paginación
    paginator = Paginator(pasajeros_list, 10) # 10 pasajeros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pasajeros/lista_pasajeros.html', {
        'page_obj': page_obj,
        'query': query
    })

def detalle_pasajero(request, pk):
    """Vista para ver los detalles de un pasajero."""
    pasajero = get_object_or_404(Pasajero, pk=pk)
    return render(request, 'pasajeros/detalle_pasajero.html', {'pasajero': pasajero})

def historial_vuelos_pasajero(request, pk):
    """Vista para ver el historial de vuelos de un pasajero."""
    pasajero = get_object_or_404(Pasajero, pk=pk)
    reservas = Reserva.objects.filter(pasajero=pasajero).order_by('-fecha_reserva')
    
    # Paginación
    paginator = Paginator(reservas, 10) # 10 reservas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pasajeros/historial_vuelos_pasajero.html', {
        'pasajero': pasajero,
        'page_obj': page_obj
    })
