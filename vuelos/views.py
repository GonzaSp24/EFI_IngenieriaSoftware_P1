from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Vuelo, Avion, Asiento
from pasajeros.models import Pasajero
from reservas.models import Reserva, Boleto
from .forms import BuscarVuelosForm
from reservas.forms import ReservaForm
from datetime import datetime, date

def lista_vuelos(request):
    """Lista todos los vuelos disponibles con filtros y paginación."""
    vuelos = Vuelo.objects.filter(estado='programado').order_by('fecha_salida')
    
    origen = request.GET.get('origen')
    destino = request.GET.get('destino')
    fecha = request.GET.get('fecha')
    
    if origen:
        vuelos = vuelos.filter(origen__icontains=origen)
    if destino:
        vuelos = vuelos.filter(destino__icontains=destino)
    if fecha:
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            vuelos = vuelos.filter(fecha_salida__date=fecha_obj)
        except ValueError:
            messages.error(request, "Formato de fecha inválido. Use YYYY-MM-DD.")
    
    paginator = Paginator(vuelos, 10) # 10 vuelos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'vuelos/lista_vuelos.html', {
        'page_obj': page_obj,
        'origen': origen or '',
        'destino': destino or '',
        'fecha': fecha or '',
    })

def detalle_vuelo(request, pk):
    """Muestra los detalles de un vuelo específico y su mapa de asientos."""
    vuelo = get_object_or_404(Vuelo, pk=pk)
    asientos_con_estado = vuelo.get_asientos_con_estado_para_vuelo()
    
    # Organizar asientos por filas para la visualización
    asientos_por_fila = {}
    for item in asientos_con_estado:
        fila = item['asiento'].fila
        if fila not in asientos_por_fila:
            asientos_por_fila[fila] = []
        asientos_por_fila[fila].append(item)
    
    return render(request, 'vuelos/detalle_vuelo.html', {
        'vuelo': vuelo,
        'asientos_por_fila': dict(sorted(asientos_por_fila.items())),
    })

@login_required
def reporte_pasajeros_vuelo(request, pk):
    """Genera un reporte de pasajeros para un vuelo específico."""
    vuelo = get_object_or_404(Vuelo, pk=pk)
    reservas = Reserva.objects.filter(vuelo=vuelo, estado='confirmada').order_by('asiento__fila', 'asiento__columna')
    
    return render(request, 'vuelos/reporte_pasajeros_vuelo.html', {
        'vuelo': vuelo,
        'reservas': reservas,
    })
