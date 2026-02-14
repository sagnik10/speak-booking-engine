from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),

    path("dashboard/", views.dashboard),
    path("employee/dashboard/", views.employee_dashboard),

    path("login/user/", views.user_login),
    path("login/employee/", views.employee_login),

    path("register/user/", views.user_register),
    path("register/employee/", views.employee_register),

    path("checkout/<int:slot_id>/", views.checkout),
    path("payment/verify/", views.verify_payment),

    path("booking/cancel/<uuid:booking_id>/", views.cancel_booking),

    path("logout/", views.logout_view),
]