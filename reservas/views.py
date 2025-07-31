from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reserva, Boleto
from vuelos.models import Vuelo, Asiento
from pasajeros.models import Pasajero
from .forms import ReservaForm

@login_required
def crear_reserva(request, vuelo_id, asiento_id):
    """Vista para crear una nueva reserva."""
    vuelo = get_object_or_404(Vuelo, pk=vuelo_id)
    asiento = get_object_or_404(Asiento, pk=asiento_id)

    # Validaciones
    if asiento.avion != vuelo.avion:
        messages.error(request, 'El asiento seleccionado no pertenece a este vuelo.')
        return redirect('detalle_vuelo', pk=vuelo_id)
    
    if asiento.estado != 'disponible':
        messages.error(request, f'El asiento {asiento.numero} ya está {asiento.get_estado_display()}.')
        return redirect('detalle_vuelo', pk=vuelo_id)
    
    # Verificar si el usuario ya tiene una reserva para este vuelo (opcional, según reglas de negocio)
    # if Reserva.objects.filter(vuelo=vuelo, pasajero__usuario=request.user).exists():
    #     messages.warning(request, 'Ya tienes una reserva para este vuelo.')
    #     return redirect('mis_reservas')

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            pasajero = form.cleaned_data['pasajero']
            
            # Verificar si el pasajero ya tiene una reserva para este vuelo
            if Reserva.objects.filter(vuelo=vuelo, pasajero=pasajero).exists():
                messages.error(request, f'El pasajero {pasajero.nombre} {pasajero.apellido} ya tiene una reserva para este vuelo.')
                return redirect('detalle_vuelo', pk=vuelo_id)

            reserva = form.save(commit=False)
            reserva.vuelo = vuelo
            reserva.asiento = asiento
            reserva.precio = vuelo.precio_base # O calcular precio según tipo de asiento, etc.
            reserva.estado = 'confirmada' # O 'pendiente' si se requiere pago
            reserva.save()
            
            # Crear boleto automáticamente
            Boleto.objects.create(reserva=reserva)
            
            messages.success(request, f'Reserva confirmada para el asiento {asiento.numero}. Código: {reserva.codigo_reserva}')
            return redirect('mis_reservas')
    else:
        form = ReservaForm()
    
    return render(request, 'reservas/crear_reserva.html', {
        'vuelo': vuelo,
        'asiento': asiento,
        'form': form
    })

@login_required
def mis_reservas(request):
    """Vista para listar las reservas del usuario actual."""
    # En un sistema real, filtrarías por el pasajero asociado al usuario logueado
    # Por simplicidad, aquí listamos todas las reservas confirmadas
    reservas = Reserva.objects.filter(estado='confirmada').order_by('-fecha_reserva')
    
    return render(request, 'reservas/mis_reservas.html', {'reservas': reservas})

@login_required
def detalle_reserva(request, codigo_reserva):
    """Vista para ver los detalles de una reserva específica."""
    reserva = get_object_or_404(Reserva, codigo_reserva=codigo_reserva)
    return render(request, 'reservas/detalle_reserva.html', {'reserva': reserva})

@login_required
def generar_boleto(request, codigo_reserva):
    """Vista para generar el boleto electrónico."""
    reserva = get_object_or_404(Reserva, codigo_reserva=codigo_reserva)
    boleto = get_object_or_404(Boleto, reserva=reserva)
    return render(request, 'reservas/boleto_electronico.html', {'boleto': boleto})

@login_required
def cancelar_reserva(request, codigo_reserva):
    """Vista para cancelar una reserva."""
    reserva = get_object_or_404(Reserva, codigo_reserva=codigo_reserva)
    
    if request.method == 'POST':
        if reserva.estado == 'confirmada':
            reserva.estado = 'cancelada'
            reserva.save()
            messages.info(request, f'La reserva {codigo_reserva} ha sido cancelada.')
        else:
            messages.warning(request, f'La reserva {codigo_reserva} no puede ser cancelada en su estado actual ({reserva.get_estado_display()}).')
        return redirect('mis_reservas')
        
    return render(request, 'reservas/cancelar_reserva.html', {'reserva': reserva})
