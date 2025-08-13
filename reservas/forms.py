from django import forms
from .models import Reserva
from pasajeros.models import Pasajero

class ReservaForm(forms.ModelForm):
    # El pasajero se selecciona aquí, el vuelo y asiento se asignan en la vista
    pasajero = forms.ModelChoiceField(
        queryset=Pasajero.objects.all().order_by('apellido', 'nombre'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="--- Seleccione un pasajero ---"
    )

    class Meta:
        model = Reserva
        fields = ['pasajero'] # Solo necesitamos el pasajero del formulario
