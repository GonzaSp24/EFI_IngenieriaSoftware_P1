from django import forms
from datetime import date

class BuscarVuelosForm(forms.Form):
    origen = forms.CharField(
        max_length=100,
        required=False,  # Hacer opcional
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ciudad de origen (opcional)'
        })
    )
    destino = forms.CharField(
        max_length=100,
        required=False,  # Hacer opcional
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ciudad de destino (opcional)'
        })
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
    
    def clean(self):
        cleaned_data = super().clean()
        origen = cleaned_data.get('origen', '').strip()
        destino = cleaned_data.get('destino', '').strip()
        
        # Al menos uno de los campos de lugar debe tener contenido
        if not origen and not destino:
            raise forms.ValidationError("Debe especificar al menos el origen o el destino.")
        
        return cleaned_data
