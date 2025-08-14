"""
Utilidades para el manejo de reservas, incluyendo generación de PDF y envío de emails
"""
import os
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.translation import gettext as _
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import qrcode
from PIL import Image as PILImage

def generar_pdf_boleto(reserva):
    """
    Genera un PDF del boleto electrónico para una reserva
    """
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0d6efd')
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#198754')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6
    )
    
    # Título
    story.append(Paragraph("RutaCeleste", title_style))
    story.append(Paragraph("Boleto Electrónico", header_style))
    story.append(Spacer(1, 20))
    
    # Información del vuelo - MODIFICAR ESTA PARTE
    flight_data = [
        ['Código de Reserva:', reserva.codigo_reserva],
        ['Pasajero:', f"{reserva.pasajero.nombre} {reserva.pasajero.apellido}"],
        ['Documento:', reserva.pasajero.documento],
        ['Vuelo:', f"{reserva.vuelo.origen} → {reserva.vuelo.destino}"],
        ['Fecha:', reserva.vuelo.fecha_salida.strftime('%d/%m/%Y')],
        ['Hora de Salida:', reserva.vuelo.fecha_salida.strftime('%H:%M')],  # Usar fecha_salida en lugar de hora_salida
        ['Asiento:', reserva.asiento.numero],
        ['Clase:', reserva.asiento.get_tipo_display()],  # Cambiado de get_clase_display a get_tipo_display
        ['Precio:', f"${reserva.precio:,.0f}"],  # Cambiado de precio_total a precio
        ['Estado:', reserva.get_estado_display()],
    ]
    
    flight_table = Table(flight_data, colWidths=[2*inch, 3*inch])
    flight_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(flight_table)
    story.append(Spacer(1, 30))
    
    # Generar código QR
    qr_data = f"RutaCeleste-{reserva.codigo_reserva}-{reserva.pasajero.documento}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    # Agregar QR al PDF
    story.append(Paragraph("Código QR del Boleto", header_style))
    qr_image = Image(qr_buffer, width=2*inch, height=2*inch)
    story.append(qr_image)
    story.append(Spacer(1, 20))
    
    # Información adicional
    story.append(Paragraph("Información Importante:", header_style))
    info_text = """
    • Presente este boleto y su documento de identidad en el aeropuerto
    • Llegue al aeropuerto al menos 1 hora antes del vuelo doméstico
    • El check-in online está disponible 24 horas antes del vuelo
    • Para cambios o cancelaciones, contacte a nuestro servicio al cliente
    """
    story.append(Paragraph(info_text, normal_style))
    
    # Construir el PDF
    doc.build(story)
    
    # Obtener el contenido del buffer
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

def enviar_boleto_email(reserva):
    """
    Envía el boleto electrónico por email al pasajero
    """
    try:
        # Generar el PDF del boleto
        pdf_content = generar_pdf_boleto(reserva)
        
        # Preparar el contexto para el template del email
        context = {
            'reserva': reserva,
            'pasajero': reserva.pasajero,
            'vuelo': reserva.vuelo,
        }
        
        # Renderizar el template del email
        html_content = render_to_string('mails/boleto_electronico.html', context)
        
        # Crear el email
        subject = f'RutaCeleste - Boleto Electrónico - Reserva {reserva.codigo_reserva}'
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reserva.pasajero.email],
        )
        
        # Configurar como HTML
        email.content_subtype = 'html'
        
        # Adjuntar el PDF
        filename = f'boleto_{reserva.codigo_reserva}.pdf'
        email.attach(filename, pdf_content, 'application/pdf')
        
        # Enviar el email
        email.send()
        
        return True, "Email enviado exitosamente"
        
    except Exception as e:
        return False, f"Error al enviar email: {str(e)}"

def generar_respuesta_pdf(reserva, filename=None):
    """
    Genera una respuesta HTTP con el PDF del boleto
    """
    if not filename:
        filename = f"boleto_{reserva.codigo_reserva}.pdf"
    
    pdf_content = generar_pdf_boleto(reserva)
    
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
