from django import forms
from .models import Reserva
from pasajeros.models import Pasajero

class ReservaForm(forms.ModelForm):
    # El campo pasajero se puede filtrar o preseleccionar en la vista
    pasajero = forms.ModelChoiceField(
        queryset=Pasajero.objects.all().order_by('apellido', 'nombre'),
        empty_label="Seleccione un pasajero existente",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Reserva
        fields = ['pasajero'] # Vuelo, asiento y precio se asignan en la vista
