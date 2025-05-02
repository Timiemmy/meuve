
import qrcode
import random
import string
from io import BytesIO
from django.core.files.base import ContentFile

def generate_booking_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_qr_code(data):
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())
