from django.shortcuts import render
from vuelos.forms import BuscarVuelosForm
from vuelos.models import Vuelo
from datetime import datetime, timedelta

def home(request):
    """Vista principal con búsqueda de vuelos flexible"""
    form = BuscarVuelosForm()
    vuelos = []
    vuelos_alternativos = []
    busqueda_realizada = False
    
    if request.method == 'POST':
        form = BuscarVuelosForm(request.POST)
        if form.is_valid():
            busqueda_realizada = True
            origen = form.cleaned_data['origen'].strip()
            destino = form.cleaned_data['destino'].strip()
            fecha_salida = form.cleaned_data['fecha_salida']
            
            # Construir filtros dinámicamente
            filtros = {
                'fecha_salida__date': fecha_salida,
                'estado': 'programado'
            }
            
            # Solo agregar filtros si hay texto (búsqueda flexible)
            if origen:
                filtros['origen__icontains'] = origen
            if destino:
                filtros['destino__icontains'] = destino
            
            # Búsqueda exacta por fecha
            vuelos = Vuelo.objects.filter(**filtros).order_by('fecha_salida')
            
            # Si no hay vuelos exactos, buscar en fechas cercanas (±3 días)
            if not vuelos.exists():
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
    
    return render(request, 'core/home.html', {
        'form': form,
        'vuelos': vuelos,
        'vuelos_alternativos': vuelos_alternativos,
        'busqueda_realizada': busqueda_realizada,
    })
