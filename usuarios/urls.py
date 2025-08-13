from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_usuario, name='registro'),
    # Puedes añadir más URLs específicas de usuarios aquí si las necesitas
]
