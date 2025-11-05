from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views import View
from home.forms import LoginForm, RegisterForm
from airline.models import Vuelo
from django.utils import timezone

def home(request):
    """Vista principal del sistema"""
    # Obtener algunos vuelos próximos para mostrar en el home
    vuelos_proximos = Vuelo.objects.filter(
        estado='programado',
        fecha_salida__gte=timezone.now()
    ).order_by('fecha_salida')[:3]
    
    context = {
        'vuelos_proximos': vuelos_proximos,
    }
    
    return render(request, 'home/home.html', context)

class HomeView(View):
    def get(self, request):
        return home(request)
        
class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "Sesión cerrada correctamente")
        return redirect('home')  # Redirigir al home de aerolínea
    
    def post(self, request):  # Agregar soporte para POST
        logout(request)
        messages.success(request, "Sesión cerrada correctamente")
        return redirect('home')

class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(
            request,
            'accounts/register.html',
            {"form": form}
        )

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )

            # Email opcional - comentar si no tienes configurado SMTP
            try:
                subject = "Registro exitoso en RutaCeleste"
                message = render_to_string(
                    'mails/welcome.html',
                    {'email': user.email, 'username': user.username}
                )
                email = EmailMessage(
                    subject=subject,
                    body=message,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[user.email]
                )
                email.content_subtype = 'html'
                email.send(fail_silently=True)
            except:
                pass  # Si falla el email, continuar

            messages.success(
                request,
                f"Usuario {user.username} registrado correctamente. ¡Ya puedes iniciar sesión!"
            )
            return redirect('login')
            
        return render(
            request,
            'accounts/register.html',
            {"form": form}
        )

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(
            request,
            'accounts/login.html',
            {"form": form}
        )

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(
                request, 
                username=username, 
                password=password
            )

            if user is not None: 
                login(request, user)
                messages.success(request, f"¡Bienvenido {user.username}!")
                return redirect("home")  # Redirigir al home de aerolínea
            else:
                messages.error(request, "El usuario o contraseña no coinciden")
                
        return render(
            request, 
            "accounts/login.html", 
            {'form': form}
        )
