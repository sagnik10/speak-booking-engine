from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
import io


def generate_invoice(booking):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica", 12)
    p.drawString(50, 800, "Session Invoice")
    p.drawString(50, 770, f"Booking ID: {booking.booking_id}")
    p.drawString(50, 740, f"User: {booking.user.name}")
    p.drawString(50, 710, f"Employee: {booking.employee.name}")
    p.drawString(50, 680, f"Session Time: {booking.slot.start_time}")
    p.drawString(50, 650, f"Duration: {booking.duration_minutes} minutes")
    p.drawString(50, 620, f"Amount Paid: ₹{booking.amount}")

    p.showPage()
    p.save()

    buffer.seek(0)
    return ContentFile(buffer.read())