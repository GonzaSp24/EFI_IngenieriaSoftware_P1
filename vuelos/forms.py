from django import forms
from datetime import date

class BuscarVuelosForm(forms.Form):
    origen = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad de origen'})
    )
    destino = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad de destino'})
    )
    fecha_salida = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=date.today()
    )
    
    def clean_fecha_salida(self):
        fecha = self.cleaned_data['fecha_salida']
        if fecha < date.today():
            raise forms.ValidationError("La fecha de salida no puede ser en el pasado.")
        return fecha
