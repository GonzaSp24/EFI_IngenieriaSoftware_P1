from django.shortcuts import render
from django.utils import timezone
from vuelos.models import Vuelo
from vuelos.forms import BuscarVuelosForm
from datetime import timedelta

def home(request):
    """Vista principal del sistema con buscador de vuelos"""
    form = BuscarVuelosForm()
    vuelos = []
    vuelos_alternativos = []
    busqueda_realizada = False
    
    # Obtener algunos vuelos próximos para mostrar en el home
    vuelos_proximos = Vuelo.objects.filter(
        estado='programado',
        fecha_salida__gte=timezone.now()
    ).order_by('fecha_salida')[:3]
    
    if request.method == 'POST':
        form = BuscarVuelosForm(request.POST)
        busqueda_realizada = True
        
        if form.is_valid():
            origen = form.cleaned_data.get('origen', '').strip()
            destino = form.cleaned_data.get('destino', '').strip()
            fecha_salida = form.cleaned_data.get('fecha_salida')
            
            # Construir filtros dinámicamente
            filtros = {
                'estado': 'programado'
            }
            
            # Solo agregar filtros si hay texto (búsqueda flexible)
            if origen:
                filtros['origen__icontains'] = origen
            if destino:
                filtros['destino__icontains'] = destino
            if fecha_salida:
                filtros['fecha_salida__date'] = fecha_salida
            
            # Búsqueda exacta por fecha
            vuelos = Vuelo.objects.filter(**filtros).order_by('fecha_salida')
            
            # Si no hay vuelos exactos, buscar en fechas cercanas (±3 días)
            if not vuelos.exists() and fecha_salida:
                fecha_inicio = fecha_salida - timedelta(days=3)
                fecha_fin = fecha_salida + timedelta(days=3)
                
                # Filtros para fechas alternativas
                filtros_alternativos = {
                    'fecha_salida__date__range': [fecha_inicio, fecha_fin],
                    'estado': 'programado'
                }
                
                # Solo agregar filtros de lugar si hay texto
                if origen:
                    filtros_alternativos['origen__icontains'] = origen
                if destino:
                    filtros_alternativos['destino__icontains'] = destino
                
                vuelos_alternativos = Vuelo.objects.filter(**filtros_alternativos).order_by('fecha_salida')
    
    context = {
        'form': form,
        'vuelos': vuelos,
        'vuelos_alternativos': vuelos_alternativos,
        'busqueda_realizada': busqueda_realizada,
        'vuelos_proximos': vuelos_proximos,
    }
    
    return render(request, 'core/home.html', context)
