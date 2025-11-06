"""
Formularios para la aplicación airline.
"""

from django import forms
from django.contrib.auth.models import User
from airline.models import Pasajero, Reserva, Vuelo


class PasajeroForm(forms.ModelForm):
    """
    Formulario para crear/editar información de pasajero.
    """

    class Meta:
        model = Pasajero
        fields = ["nombre", "apellido", "dni", "email", "telefono", "fecha_nacimiento"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre"}
            ),
            "apellido": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Apellido"}
            ),
            "dni": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "DNI"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
            "telefono": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Teléfono"}
            ),
            "fecha_nacimiento": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }


class BuscarVueloForm(forms.Form):
    """
    Formulario para buscar vuelos disponibles.
    """

    origen = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ciudad de origen"}
        ),
    )
    destino = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ciudad de destino"}
        ),
    )
    fecha = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )


class ReservaForm(forms.ModelForm):
    """
    Formulario para crear una reserva.
    """

    class Meta:
        model = Reserva
        fields = ["asiento"]
        widgets = {
            "asiento": forms.Select(attrs={"class": "form-control"}),
        }
