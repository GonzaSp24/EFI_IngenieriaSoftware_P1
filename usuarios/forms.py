from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Requerido. Ingresa una dirección de correo válida.')
    rol = forms.ChoiceField(choices=CustomUser.rol_choices, initial='cliente', widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'rol',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            if field_name != 'password2': # No aplicar a la confirmación de contraseña si no es necesario
                field.widget.attrs['class'] = 'form-control'
            if field_name == 'email':
                field.widget.attrs['placeholder'] = 'tu.email@ejemplo.com'
            elif field_name == 'username':
                field.widget.attrs['placeholder'] = 'nombredeusuario'
