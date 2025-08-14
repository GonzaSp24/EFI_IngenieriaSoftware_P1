from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Reserva, Boleto
from vuelos.models import Vuelo, Asiento
from pasajeros.models import Pasajero
from .forms import ReservaForm
from .utils import enviar_boleto_email, generar_respuesta_pdf

@login_required
def crear_reserva(request, vuelo_id, asiento_id):
    """Permite al usuario crear una reserva para un vuelo y asiento específicos."""
    vuelo = get_object_or_404(Vuelo, pk=vuelo_id)
    asiento = get_object_or_404(Asiento, pk=asiento_id)
    
    # Verificar que el usuario tenga un perfil de pasajero
    try:
        mi_pasajero = request.user.pasajero
    except Pasajero.DoesNotExist:
        messages.error(request, 'Primero debes completar tu perfil de pasajero para poder reservar.')
        return redirect('registrar_pasajero')
    
    # Validaciones iniciales
    if asiento.avion != vuelo.avion:
        messages.error(request, 'El asiento seleccionado no pertenece al avión de este vuelo.')
        return redirect('detalle_vuelo', pk=vuelo.pk)
    
    if Reserva.objects.filter(vuelo=vuelo, asiento=asiento, estado='confirmada').exists():
        messages.error(request, 'Este asiento ya está ocupado para este vuelo.')
        return redirect('detalle_vuelo', pk=vuelo.pk)
    
    # Verificar si el usuario ya tiene una reserva para este vuelo
    if Reserva.objects.filter(vuelo=vuelo, pasajero=mi_pasajero, estado='confirmada').exists():
        messages.error(request, 'Ya tienes una reserva confirmada para este vuelo.')
        return redirect('detalle_vuelo', pk=vuelo.pk)
    
    if request.method == 'POST':
        # Para usuarios normales, siempre reservar para sí mismos
        if request.user.is_staff or request.user.is_superuser:
            # Los admin pueden elegir pasajero
            form = ReservaForm(request.POST)
            if form.is_valid():
                pasajero = form.cleaned_data['pasajero']
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en {field}: {error}")
                return render(request, 'reservas/crear_reserva.html', {
                    'vuelo': vuelo,
                    'asiento': asiento,
                    'form': form,
                    'es_admin': True,
                })
        else:
            # Usuario normal: reservar para sí mismo
            pasajero = mi_pasajero
        
        try:
            reserva = Reserva.objects.create(
                vuelo=vuelo,
                pasajero=pasajero,
                asiento=asiento,
                precio=vuelo.precio_base,
                estado='confirmada'
            )
            boleto = Boleto.objects.create(reserva=reserva)
            
            # 📧 AQUÍ ES DONDE SE ENVÍA EL EMAIL AUTOMÁTICAMENTE
            success, message = enviar_boleto_email(reserva)
            if success:
                messages.success(request, f'¡Reserva confirmada exitosamente! Código: {reserva.codigo_reserva}. {message}')
            else:
                messages.success(request, f'¡Reserva confirmada exitosamente! Código: {reserva.codigo_reserva}')
                messages.warning(request, f'Advertencia: {message}')
            
            return redirect('detalle_reserva', codigo_reserva=reserva.codigo_reserva)
        except Exception as e:
            messages.error(request, f'Error al crear la reserva: {e}')
            return redirect('detalle_vuelo', pk=vuelo.pk)
    else:
        if request.user.is_staff or request.user.is_superuser:
            form = ReservaForm()
            es_admin = True
        else:
            form = None
            es_admin = False
    
    return render(request, 'reservas/crear_reserva.html', {
        'vuelo': vuelo,
        'asiento': asiento,
        'form': form,
        'mi_pasajero': mi_pasajero,
        'es_admin': es_admin,
    })

@login_required
def detalle_reserva(request, codigo_reserva):
    """Muestra los detalles de una reserva específica."""
    reserva = get_object_or_404(Reserva, codigo_reserva=codigo_reserva)
    
    # Verificar permisos: solo el dueño de la reserva o admin pueden verla
    if not (request.user.is_staff or request.user.is_superuser):
        if not hasattr(request.user, 'pasajero') or reserva.pasajero != request.user.pasajero:
            messages.error(request, 'No tienes permisos para ver esta reserva.')
            return redirect('mis_reservas')
    
    return render(request, 'reservas/detalle_reserva.html', {'reserva': reserva})

@login_required
def generar_boleto(request, codigo_reserva):
    """Genera y muestra el boleto electrónico para una reserva."""
    reserva = get_object_or_404(Reserva, codigo_reserva=codigo_reserva)
    
    # Verificar permisos: solo el dueño de la reserva o admin pueden ver el boleto
    if not (request.user.is_staff or request.user.is_superuser):
        if not hasattr(request.user, 'pasajero') or reserva.pasajero != request.user.pasajero:
            messages.error(request, 'No tienes permisos para ver este boleto.')
            return redirect('mis_reservas')
    
    boleto = get_object_or_404(Boleto, reserva=reserva)
    return render(request, 'reservas/boleto_electronico.html', {'boleto': boleto})

@login_required
def descargar_boleto_pdf(request, codigo_reserva):
    """Descarga el boleto como PDF"""
    reserva = get_object_or_404(Reserva, codigo_reserva=codigo_reserva)
    
    # Verificar permisos
    if not (request.user.is_staff or request.user.is_superuser):
        if not hasattr(request.user, 'pasajero') or reserva.pasajero != request.user.pasajero:
            messages.error(request, 'No tienes permisos para descargar este boleto.')
            return redirect('mis_reservas')
    
    return generar_respuesta_pdf(reserva)

@login_required
def reenviar_boleto_email(request, codigo_reserva):
    """Reenvía el boleto por email"""
    reserva = get_object_or_404(Reserva, codigo_reserva=codigo_reserva)
    
    # Verificar permisos
    if not (request.user.is_staff or request.user.is_superuser):
        if not hasattr(request.user, 'pasajero') or reserva.pasajero != request.user.pasajero:
            messages.error(request, 'No tienes permisos para reenviar este boleto.')
            return redirect('mis_reservas')
    
    # 📧 AQUÍ ES DONDE SE REENVÍA EL EMAIL MANUALMENTE
    success, message = enviar_boleto_email(reserva)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('detalle_reserva', codigo_reserva=codigo_reserva)

@login_required
def mis_reservas(request):
    """Muestra las reservas del usuario logueado."""
    if request.user.is_staff or request.user.is_superuser:
        # Admin ve todas las reservas
        reservas = Reserva.objects.filter(estado='confirmada').order_by('-fecha_reserva')
        es_admin = True
        messages.info(request, 'Mostrando todas las reservas (vista de administrador)')
    else:
        # Usuario normal ve solo sus reservas
        try:
            mi_pasajero = request.user.pasajero
            reservas = Reserva.objects.filter(pasajero=mi_pasajero).order_by('-fecha_reserva')
            es_admin = False
        except Pasajero.DoesNotExist:
            reservas = Reserva.objects.none()
            es_admin = False
            messages.info(request, 'Primero debes completar tu perfil de pasajero para ver tus reservas.')
    
    return render(request, 'reservas/mis_reservas.html', {
        'reservas': reservas,
        'es_admin': es_admin,
    })

@login_required
def cancelar_reserva(request, pk):
    """Permite cancelar una reserva."""
    reserva = get_object_or_404(Reserva, pk=pk)
    
    # Verificar permisos
    puede_cancelar = False
    if request.user.is_staff or request.user.is_superuser:
        puede_cancelar = True
    elif hasattr(request.user, 'pasajero') and reserva.pasajero == request.user.pasajero:
        puede_cancelar = True
    
    if not puede_cancelar:
        messages.error(request, 'No tienes permisos para cancelar esta reserva.')
        return redirect('mis_reservas')
    
    if request.method == 'POST':
        if reserva.estado == 'confirmada':
            reserva.estado = 'cancelada'
            reserva.save()
            
            # Anular boleto si existe
            try:
                boleto = Boleto.objects.get(reserva=reserva)
                boleto.estado = 'anulado'
                boleto.save()
            except Boleto.DoesNotExist:
                pass
            
            # Mensaje personalizado
            messages.success(request, f'Tu reserva {reserva.codigo_reserva} ha sido cancelada exitosamente. Si necesitas ayuda, contáctanos.')
        else:
            messages.warning(request, f'La reserva {reserva.codigo_reserva} no puede ser cancelada porque ya está en estado {reserva.get_estado_display()}.')
        
        return redirect('mis_reservas')
    
    # Contexto adicional para el template
    context = {
        'reserva': reserva,
        'puede_cancelar': puede_cancelar,
        'titulo': 'Confirmar cancelación',
        'mensaje': f'¿Estás seguro de que deseas cancelar tu reserva {reserva.codigo_reserva}?',
    }
    return render(request, 'reservas/cancelar_reserva.html', context)