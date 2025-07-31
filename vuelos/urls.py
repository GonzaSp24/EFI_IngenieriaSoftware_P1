from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_vuelos, name='lista_vuelos'),
    path('<int:pk>/', views.detalle_vuelo, name='detalle_vuelo'),
    path('<int:pk>/reporte/', views.reporte_pasajeros_vuelo, name='reporte_pasajeros_vuelo'),
]
