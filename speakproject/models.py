from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import hashlib
import uuid


def pdf_only(instance, filename):
    if not filename.lower().endswith(".pdf"):
        raise ValidationError("Only PDF files are allowed.")
    return f"documents/{uuid.uuid4()}.pdf"


def jpg_only(value):
    if not value.name.lower().endswith((".jpg", ".jpeg")):
        raise ValidationError("Only JPG/JPEG images are allowed.")


ifsc_validator = RegexValidator(
    regex=r'^[A-Z]{4}0[A-Z0-9]{6}$',
    message="Enter a valid IFSC code"
)

upi_validator = RegexValidator(
    regex=r'^[\w.\-]{2,256}@[a-zA-Z]{2,64}$',
    message="Enter a valid UPI ID"
)


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    address = models.TextField()
    dob = models.DateField()
    profile_image = models.ImageField(upload_to="employee_images/", validators=[jpg_only], null=True, blank=True)
    image_hash = models.CharField(max_length=64, unique=True, editable=False, null=True, blank=True)
    govt_document = models.FileField(upload_to=pdf_only)
    academic_document = models.FileField(upload_to=pdf_only)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    account_holder_name = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=30, null=True, blank=True)
    ifsc_code = models.CharField(max_length=11, validators=[ifsc_validator], null=True, blank=True)
    upi_id = models.CharField(max_length=320, validators=[upi_validator], blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.profile_image:
            hasher = hashlib.sha256()
            for chunk in self.profile_image.file.chunks():
                hasher.update(chunk)
            self.image_hash = hasher.hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    medical_document = models.FileField(upload_to=pdf_only)

    def __str__(self):
        return self.user.username


class EmployeeSlot(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name="slots")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("employee", "start_time")
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.employee.name} | {self.start_time}"


class Booking(models.Model):
    booking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="bookings")
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name="bookings")
    slot = models.OneToOneField(EmployeeSlot, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=30)
    duration_minutes = models.PositiveIntegerField(default=10)
    payment_gateway = models.CharField(max_length=30)
    payment_id = models.CharField(max_length=200)
    invoice_pdf = models.FileField(upload_to="invoices/", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_cancelled = models.BooleanField(default=False)
    is_refunded = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.booking_id)