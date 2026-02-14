from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.conf import settings

import json
import razorpay

from .models import EmployeeProfile, UserProfile, EmployeeSlot, Booking
from .payments import razorpay_client
from .utils import generate_invoice


def home(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "employeeprofile"):
            return redirect("/employee/dashboard/")
        return redirect("/dashboard/")
    return render(request, "speakproject/home.html")


@login_required(login_url="/")
def dashboard(request):
    if hasattr(request.user, "employeeprofile"):
        return redirect("/employee/dashboard/")

    user_profile = request.user.userprofile

    employees = EmployeeProfile.objects.filter(
        is_approved=True
    ).prefetch_related("slots")

    bookings = user_profile.bookings.select_related(
        "employee", "slot"
    ).order_by("-created_at")

    context = {
        "employees": employees,
        "bookings": bookings,
        "price": 30,
        "duration": 10,
    }

    return render(request, "speakproject/dashboard.html", context)


@login_required(login_url="/")
def employee_dashboard(request):
    if not hasattr(request.user, "employeeprofile"):
        return redirect("/dashboard/")

    profile = request.user.employeeprofile

    slots = profile.slots.all()

    bookings = profile.bookings.filter(
        is_cancelled=False
    ).select_related("user", "slot").order_by("-created_at")

    total_sessions = bookings.count()
    total_earnings = total_sessions * 30

    context = {
        "is_approved": profile.is_approved,
        "employee_name": profile.name,
        "slots": slots,
        "bookings": bookings,
        "total_sessions": total_sessions,
        "total_earnings": total_earnings,
    }

    return render(request, "speakproject/employee_dashboard.html", context)


def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out safely.")
    return redirect("/")


def user_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user and hasattr(user, "userprofile"):
            login(request, user)
            request.session.set_expiry(
                None if request.POST.get("remember") else 0
            )
            return redirect("/dashboard/")
        messages.error(request, "Invalid credentials.")
    return render(request, "speakproject/user_login.html")


def employee_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user and hasattr(user, "employeeprofile"):
            login(request, user)
            request.session.set_expiry(
                None if request.POST.get("remember") else 0
            )
            return redirect("/employee/dashboard/")
        messages.error(request, "Invalid credentials.")
    return render(request, "speakproject/employee_login.html")


def user_register(request):
    if request.method == "POST":
        if User.objects.filter(username=request.POST["username"]).exists():
            messages.error(request, "Username already exists.")
            return redirect("/register/user/")

        user = User.objects.create_user(
            username=request.POST["username"],
            password=request.POST["password"],
            email=request.POST["email"],
        )

        UserProfile.objects.create(
            user=user,
            name=request.POST["name"],
            phone=request.POST["phone"],
            address=request.POST["address"],
            medical_document=request.FILES.get("medical_document"),
        )

        messages.success(request, "Account created successfully.")
        return redirect("/login/user/")

    return render(request, "speakproject/user_register.html")


def employee_register(request):
    if request.method == "POST":
        if User.objects.filter(username=request.POST["username"]).exists():
            messages.error(request, "Username already exists.")
            return redirect("/register/employee/")

        try:
            user = User.objects.create_user(
                username=request.POST["username"],
                password=request.POST["password"],
                email=request.POST["email"],
            )

            EmployeeProfile.objects.create(
                user=user,
                name=request.POST["name"],
                description=request.POST.get("description"),
                address=request.POST["address"],
                dob=request.POST["dob"],
                profile_image=request.FILES.get("profile_image"),
                govt_document=request.FILES.get("govt_document"),
                academic_document=request.FILES.get("academic_document"),
                bank_name=request.POST.get("bank_name"),
                account_holder_name=request.POST.get("account_holder_name"),
                account_number=request.POST.get("account_number"),
                ifsc_code=request.POST.get("ifsc_code"),
                upi_id=request.POST.get("upi_id"),
            )

            messages.success(request, "Application submitted successfully.")
            return redirect("/login/employee/")

        except IntegrityError:
            user.delete()
            messages.error(request, "Registration failed.")
            return redirect("/register/employee/")

    return render(request, "speakproject/employee_register.html")


@login_required(login_url="/")
def checkout(request, slot_id):
    slot = get_object_or_404(
        EmployeeSlot,
        id=slot_id,
        is_booked=False
    )

    amount = 30

    order = razorpay_client.order.create({
        "amount": amount * 100,
        "currency": "INR",
        "payment_capture": 1,
    })

    request.session["slot_id"] = slot.id

    context = {
        "slot": slot,
        "amount": amount,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": order["id"],
    }

    return render(request, "speakproject/checkout.html", context)


@login_required(login_url="/")
@transaction.atomic
def verify_payment(request):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=400)

    data = json.loads(request.body)

    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_payment_id": data["payment_id"],
            "razorpay_order_id": data["order_id"],
            "razorpay_signature": data["signature"],
        })
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"status": "error"})

    slot = get_object_or_404(
        EmployeeSlot.objects.select_for_update(),
        id=request.session.get("slot_id"),
        is_booked=False,
    )

    booking = Booking.objects.create(
        user=request.user.userprofile,
        employee=slot.employee,
        slot=slot,
        payment_gateway="razorpay",
        payment_id=data["payment_id"],
    )

    booking.invoice_pdf.save(
        f"{booking.booking_id}.pdf",
        generate_invoice(booking)
    )

    slot.is_booked = True
    slot.save()

    return JsonResponse({"status": "success"})


@login_required(login_url="/")
@transaction.atomic
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_for_update(),
        booking_id=booking_id,
        user=request.user.userprofile,
        is_cancelled=False,
    )

    razorpay_client.payment.refund(booking.payment_id)

    booking.is_cancelled = True
    booking.is_refunded = True

    booking.slot.is_booked = False
    booking.slot.save()
    booking.save()

    messages.success(request, "Booking cancelled and refunded.")
    return redirect("/dashboard/")