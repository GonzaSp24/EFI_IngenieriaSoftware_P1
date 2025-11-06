"""
Vistas web de la aplicación airline.
Estas son las vistas que renderizan HTML (no la API REST).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from datetime import datetime

from airline.models import Vuelo, Pasajero, Reserva, Boleto, Avion, Asiento


def lista_vuelos(request):
    """
    Vista para listar todos los vuelos disponibles.
    Permite filtrar por origen, destino y fecha.
    """
    vuelos = Vuelo.objects.all().order_by("fecha_salida")

    # Filtros
    origen = request.GET.get("origen")
    destino = request.GET.get("destino")
    fecha = request.GET.get("fecha")

    if origen:
        vuelos = vuelos.filter(origen__icontains=origen)
    if destino:
        vuelos = vuelos.filter(destino__icontains=destino)
    if fecha:
        vuelos = vuelos.filter(fecha_salida__date=fecha)

    context = {
        "vuelos": vuelos,
        "origen": origen,
        "destino": destino,
        "fecha": fecha,
    }
    return render(request, "vuelos/lista_vuelos.html", context)


def detalle_vuelo(request, vuelo_id):
    """
    Vista para ver el detalle de un vuelo específico.
    Muestra información del vuelo y asientos disponibles.
    """
    vuelo = get_object_or_404(Vuelo, id=vuelo_id)
    asientos_disponibles = Asiento.objects.filter(avion=vuelo.avion, disponible=True)

    context = {
        "vuelo": vuelo,
        "asientos_disponibles": asientos_disponibles,
    }
    return render(request, "vuelos/detalle_vuelo.html", context)


@login_required
def registrar_pasajero(request):
    """
    Crea (o completa) el perfil de pasajero para el usuario autenticado.
    GET  -> muestra formulario
    POST -> crea/actualiza y redirige al perfil
    """
    # Si ya existe, podés prellenar el form y permitir actualizar
    pasajero = Pasajero.objects.filter(usuario=request.user).first()

    if request.method == "POST":
        # Campos básicos esperados desde el form
        campos = {
            "nombre": request.POST.get("nombre", "").strip(),
            "apellido": request.POST.get("apellido", "").strip(),
            "dni": request.POST.get("dni", "").strip(),
            "telefono": request.POST.get("telefono", "").strip(),
        }

        if not pasajero:
            pasajero = Pasajero(usuario=request.user)

        # Setear solo los campos que existan en el modelo
        for k, v in campos.items():
            if hasattr(pasajero, k):
                setattr(pasajero, k, v)

        pasajero.save()
        messages.success(request, "¡Perfil de pasajero guardado correctamente!")
        return redirect("mi_perfil")  # tu URL ya mapea al perfil

    # GET
    context = {"pasajero": pasajero}
    return render(request, "pasajeros/registrar_pasajero.html", context)


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def lista_pasajeros(request):
    """
    Muestra la lista completa de pasajeros registrados en el sistema.
    Solo accesible por personal administrativo o administradores.
    """
    pasajeros = Pasajero.objects.all().order_by("apellido", "nombre")

    # Si querés agregar búsqueda por nombre o documento
    query = request.GET.get("q")
    if query:
        pasajeros = (
            pasajeros.filter(nombre__icontains=query)
            | pasajeros.filter(apellido__icontains=query)
            | pasajeros.filter(documento__icontains=query)
        )

    context = {
        "pasajeros": pasajeros,
        "total": pasajeros.count(),
    }
    return render(request, "pasajeros/lista_pasajeros.html", context)


@login_required
def reporte_pasajeros_vuelo(request, pk):
    """
    Reporte de pasajeros por vuelo (HTML).
    Lista los pasajeros que tienen reserva en el vuelo indicado.
    """
    vuelo = get_object_or_404(Vuelo, pk=pk)
    reservas = (
        Reserva.objects.filter(vuelo=vuelo)
        .select_related("pasajero")
        .order_by("pasajero__id")
    )
    pasajeros = [r.pasajero for r in reservas]

    context = {
        "vuelo": vuelo,
        "reservas": reservas,
        "pasajeros": pasajeros,
        "total_pasajeros": len(pasajeros),
    }
    return render(request, "vuelos/reporte_pasajeros_vuelo.html", context)


@login_required
def mi_perfil(request):
    """
    Vista del perfil del pasajero.
    Muestra información personal y reservas del usuario.
    """
    try:
        pasajero = Pasajero.objects.get(usuario=request.user)
        reservas = Reserva.objects.filter(pasajero=pasajero).order_by("-fecha_reserva")
    except Pasajero.DoesNotExist:
        pasajero = None
        reservas = []

    context = {
        "pasajero": pasajero,
        "reservas": reservas,
    }
    return render(request, "pasajeros/mi_perfil.html", context)


@login_required
def editar_mi_perfil(request):
    """
    Edita el perfil de pasajero existente. Si no existe, manda a registrar.
    """
    pasajero = Pasajero.objects.filter(usuario=request.user).first()
    if not pasajero:
        messages.info(request, "Primero tenés que crear tu perfil de pasajero.")
        return redirect("registrar_pasajero")

    if request.method == "POST":
        campos = {
            "nombre": request.POST.get("nombre", "").strip(),
            "apellido": request.POST.get("apellido", "").strip(),
            "dni": request.POST.get("dni", "").strip(),
            "telefono": request.POST.get("telefono", "").strip(),
        }

        for k, v in campos.items():
            if hasattr(pasajero, k):
                setattr(pasajero, k, v)

        pasajero.save()
        messages.success(request, "Perfil actualizado.")
        return redirect("mi_perfil")

    context = {"pasajero": pasajero}
    return render(request, "pasajeros/editar_perfil.html", context)


@login_required
def crear_reserva(request, vuelo_id):
    """
    Vista para crear una nueva reserva.
    Permite al pasajero seleccionar asiento y confirmar la reserva.
    """
    vuelo = get_object_or_404(Vuelo, id=vuelo_id)

    if request.method == "POST":
        asiento_id = request.POST.get("asiento_id")
        asiento = get_object_or_404(Asiento, id=asiento_id)

        try:
            pasajero = Pasajero.objects.get(usuario=request.user)
        except Pasajero.DoesNotExist:
            messages.error(request, "Debes completar tu perfil de pasajero primero.")
            return redirect("mi_perfil")

        # Crear reserva
        reserva = Reserva.objects.create(
            vuelo=vuelo, pasajero=pasajero, asiento=asiento, estado="confirmada"
        )

        # Marcar asiento como no disponible
        asiento.disponible = False
        asiento.save()

        messages.success(
            request, f"Reserva creada exitosamente. Código: {reserva.codigo_reserva}"
        )
        return redirect("detalle_reserva", reserva_id=reserva.id)

    asientos_disponibles = Asiento.objects.filter(avion=vuelo.avion, disponible=True)

    context = {
        "vuelo": vuelo,
        "asientos_disponibles": asientos_disponibles,
    }
    return render(request, "reservas/crear_reserva.html", context)


@login_required
def detalle_reserva(request, reserva_id):
    """
    Vista para ver el detalle de una reserva específica.
    Muestra información completa de la reserva y permite generar boleto.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Verificar que el usuario sea el dueño de la reserva
    if reserva.pasajero.usuario != request.user:
        messages.error(request, "No tienes permiso para ver esta reserva.")
        return redirect("mi_perfil")

    try:
        boleto = Boleto.objects.get(reserva=reserva)
    except Boleto.DoesNotExist:
        boleto = None

    context = {
        "reserva": reserva,
        "boleto": boleto,
    }
    return render(request, "reservas/detalle_reserva.html", context)


@login_required
def mis_reservas(request):
    """
    Lista de reservas del pasajero autenticado (ordenadas por fecha desc).
    """
    try:
        pasajero = Pasajero.objects.get(usuario=request.user)
        # Igual que en tu vista de perfil: filtrar por pasajero logueado
        reservas = Reserva.objects.filter(pasajero=pasajero).order_by("-fecha_reserva")
        #        ↑ mismo patrón que mi_perfil para traer reservas
    except Pasajero.DoesNotExist:
        messages.info(
            request, "Aún no tenés perfil de pasajero, crealo para ver tus reservas."
        )
        return redirect("registrar_pasajero")

    context = {
        "pasajero": pasajero,
        "reservas": reservas,
    }
    return render(request, "reservas/mis_reservas.html", context)


@login_required
def cancelar_reserva(request, reserva_id):
    """
    Vista para cancelar una reserva.
    Libera el asiento y cambia el estado de la reserva.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)

    # Verificar que el usuario sea el dueño de la reserva
    if reserva.pasajero.usuario != request.user:
        messages.error(request, "No tienes permiso para cancelar esta reserva.")
        return redirect("mi_perfil")

    if request.method == "POST":
        # Liberar asiento
        if reserva.asiento:
            reserva.asiento.disponible = True
            reserva.asiento.save()

        # Cambiar estado de reserva
        reserva.estado = "cancelada"
        reserva.save()

        messages.success(request, "Reserva cancelada exitosamente.")
        return redirect("mi_perfil")

    context = {
        "reserva": reserva,
    }
    return render(request, "reservas/cancelar_reserva.html", context)
