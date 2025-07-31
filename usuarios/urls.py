from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_usuario, name='registro_usuario'),
    # Puedes añadir más URLs para gestión de usuarios aquí si es necesario
]
