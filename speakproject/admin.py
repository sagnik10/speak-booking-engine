from django.contrib import admin
from django.utils.html import format_html
from .models import (
    EmployeeProfile,
    UserProfile,
    EmployeeSlot,
    Booking,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "phone")
    search_fields = ("user__username", "name", "phone")
    ordering = ("user__username",)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "is_approved",
        "image_preview",
    )
    search_fields = ("user__username", "name", "bank_name", "upi_id")
    list_filter = ("is_approved",)
    readonly_fields = ("image_hash", "image_preview")

    fieldsets = (
        (None, {
            "fields": (
                "user",
                "name",
                "description",
                "profile_image",
                "image_preview",
                "dob",
                "address",
                "is_approved",
            )
        }),
        ("Verification Documents", {
            "fields": (
                "govt_document",
                "academic_document",
            )
        }),
        ("Bank & Payout Details", {
            "fields": (
                "bank_name",
                "account_holder_name",
                "account_number",
                "ifsc_code",
                "upi_id",
            )
        }),
        ("System", {
            "fields": ("image_hash",)
        }),
    )

    def image_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" style="height:80px;border-radius:6px;" />',
                obj.profile_image.url
            )
        return "—"

    image_preview.short_description = "Profile Image"


@admin.register(EmployeeSlot)
class EmployeeSlotAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "start_time",
        "end_time",
        "is_booked",
    )
    list_filter = ("employee", "is_booked")
    search_fields = ("employee__name", "employee__user__username")
    ordering = ("start_time",)
    readonly_fields = ()

    fieldsets = (
        (None, {
            "fields": (
                "employee",
                "start_time",
                "end_time",
                "is_booked",
            )
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "booking_id",
        "user",
        "employee",
        "amount",
        "duration_minutes",
        "payment_gateway",
        "created_at",
        "is_cancelled",
        "is_refunded",
    )
    list_filter = (
        "payment_gateway",
        "is_cancelled",
        "is_refunded",
        "created_at",
    )
    search_fields = (
        "booking_id",
        "payment_id",
        "user__user__username",
        "employee__user__username",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "booking_id",
        "payment_id",
        "payment_gateway",
        "invoice_pdf",
        "created_at",
    )

    fieldsets = (
        ("Booking", {
            "fields": (
                "booking_id",
                "user",
                "employee",
                "slot",
            )
        }),
        ("Payment", {
            "fields": (
                "amount",
                "duration_minutes",
                "payment_gateway",
                "payment_id",
                "invoice_pdf",
            )
        }),
        ("Status", {
            "fields": (
                "is_cancelled",
                "is_refunded",
            )
        }),
        ("System", {
            "fields": ("created_at",)
        }),
    )