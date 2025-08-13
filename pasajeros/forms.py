from django import forms
from .models import Pasajero
from datetime import date

class PasajeroForm(forms.ModelForm):
    class Meta:
        model = Pasajero
        fields = ['nombre', 'apellido', 'tipo_documento', 'documento', 'email', 'telefono', 'fecha_nacimiento']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +5491112345678'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data['fecha_nacimiento']
        if fecha > date.today():
            raise forms.ValidationError("La fecha de nacimiento no puede ser futura.")
        return fecha
