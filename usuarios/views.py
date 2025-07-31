from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm

def registro_usuario(request):
    """Vista para el registro de nuevos usuarios."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Inicia sesión al usuario automáticamente
            messages.success(request, '¡Cuenta creada exitosamente! Bienvenido a AeroSystem.')
            return redirect('home') # Redirige a la página de inicio
        else:
            # Si el formulario no es válido, los errores se mostrarán en la plantilla
            pass
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})
