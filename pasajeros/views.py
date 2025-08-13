from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Pasajero
from .forms import PasajeroForm
from reservas.models import Reserva

@login_required
def registrar_pasajero(request):
    """Vista para registrar un nuevo pasajero."""
    # Si el usuario no es admin y ya tiene un pasajero asociado, redirigir
    if not (request.user.is_staff or request.user.is_superuser):
        if hasattr(request.user, 'pasajero'):
            messages.info(request, 'Ya tienes un perfil de pasajero registrado.')
            return redirect('mi_perfil_pasajero')
    
    if request.method == 'POST':
        form = PasajeroForm(request.POST)
        if form.is_valid():
            pasajero = form.save(commit=False)
            
            # Verificar email solo para usuarios normales
            if not (request.user.is_staff or request.user.is_superuser):
                if pasajero.email != request.user.email:
                    messages.error(request, f'El email debe coincidir con el de tu cuenta: {request.user.email}')
                    return render(request, 'pasajeros/registrar_pasajero.html', {'form': form})
                
                # Vincular el pasajero con el usuario actual
                pasajero.usuario = request.user
                pasajero.save()
                messages.success(request, 'Tu perfil de pasajero ha sido creado exitosamente. ¡Ya puedes reservar vuelos!')
                return redirect('mi_perfil_pasajero')
            else:
                # Para admin, guardar sin vincular usuario
                pasajero.save()
                messages.success(request, f'Pasajero {pasajero.nombre} {pasajero.apellido} registrado exitosamente.')
                return redirect('lista_pasajeros')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
    else:
        # Pre-llenar el email solo para usuarios normales
        if request.user.is_staff or request.user.is_superuser:
            form = PasajeroForm()
        else:
            form = PasajeroForm(initial={'email': request.user.email})
    
    return render(request, 'pasajeros/registrar_pasajero.html', {'form': form})

@login_required
def mi_perfil_pasajero(request):
    """Vista para ver y editar el perfil del pasajero del usuario actual."""
    try:
        pasajero = request.user.pasajero
    except Pasajero.DoesNotExist:
        messages.info(request, 'Primero debes registrar tu perfil de pasajero.')
        return redirect('registrar_pasajero')
    
    # Obtener reservas del pasajero
    reservas = Reserva.objects.filter(pasajero=pasajero).order_by('-fecha_reserva')
    
    return render(request, 'pasajeros/mi_perfil.html', {
        'pasajero': pasajero,
        'reservas': reservas,
    })

@login_required
def editar_mi_perfil(request):
    """Vista para editar el perfil del pasajero del usuario actual."""
    try:
        pasajero = request.user.pasajero
    except Pasajero.DoesNotExist:
        messages.error(request, 'Primero debes registrar tu perfil de pasajero.')
        return redirect('registrar_pasajero')
    
    if request.method == 'POST':
        form = PasajeroForm(request.POST, instance=pasajero)
        if form.is_valid():
            pasajero_actualizado = form.save(commit=False)
            
            # Verificar que el email coincida con el del usuario
            if pasajero_actualizado.email != request.user.email:
                messages.error(request, f'El email debe coincidir con el de tu cuenta: {request.user.email}')
                return render(request, 'pasajeros/editar_perfil.html', {'form': form, 'pasajero': pasajero})
            
            pasajero_actualizado.save()
            messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
            return redirect('mi_perfil_pasajero')
    else:
        form = PasajeroForm(instance=pasajero)
    
    return render(request, 'pasajeros/editar_perfil.html', {'form': form, 'pasajero': pasajero})

@login_required
def lista_pasajeros(request):
    """Lista todos los pasajeros con búsqueda y paginación - Solo para admin."""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'No tienes permisos para ver la lista de pasajeros.')
        return redirect('home')
    
    pasajeros = Pasajero.objects.all().order_by('apellido', 'nombre')
    
    busqueda = request.GET.get('busqueda')
    if busqueda:
        pasajeros = pasajeros.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellido__icontains=busqueda) |
            Q(documento__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )
    
    paginator = Paginator(pasajeros, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pasajeros/lista_pasajeros.html', {
        'page_obj': page_obj,
        'busqueda': busqueda or '',
    })

@login_required
def detalle_pasajero(request, pk):
    """Muestra el detalle de un pasajero y su historial de vuelos - Solo para admin."""
    pasajero = get_object_or_404(Pasajero, pk=pk)
    
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'No tienes permisos para ver este pasajero.')
        return redirect('home')
    
    reservas = Reserva.objects.filter(pasajero=pasajero).order_by('-fecha_reserva')
    
    return render(request, 'pasajeros/historial_vuelos_pasajero.html', {
        'pasajero': pasajero,
        'reservas': reservas,
    })
