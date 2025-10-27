from django.contrib import admin
from .models import User, Payment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email")
    list_filter = list_display
    search_fields = ("email",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "payment_date", "course", "lesson", "amount", "payment_method")
    search_fields = ("user",)
    list_filter = list_display
    ordering = ['-payment_date']
