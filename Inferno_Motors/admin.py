# Inferno_Motors/admin.py
from django import forms
from django.contrib import admin, messages
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db import IntegrityError, transaction

from .models import (
    userdetails, CarCompany, CarModel, CarPart,
    CarPartsPurchase, Car, CarImage, PurchaseRequest
)

def safe_delete_selected(modeladmin, request, queryset):
    current_user = request.user
    if queryset.model == current_user.__class__:
        if queryset.filter(pk=current_user.pk).exists():
            queryset = queryset.exclude(pk=current_user.pk)
            messages.warning(request, "Your own admin account was excluded from deletion.")
    if not queryset.exists():
        messages.info(request, "Nothing to delete.")
        return
    count = queryset.count()
    try:
        with transaction.atomic():
            queryset.delete()
        messages.success(request, f"Successfully deleted {count} item(s).")
    except IntegrityError as e:
        messages.error(request, f"Delete failed due to database constraints: {e}")

safe_delete_selected.short_description = "Delete selected (SAFE — no admin log)"

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = userdetails
        fields = ("email", "name", "contact")

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if not p1:
            raise forms.ValidationError("Password required")
        if p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label="Password (hashed)")
    password1 = forms.CharField(label="New password", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label="Confirm new password", widget=forms.PasswordInput, required=False)

    class Meta:
        model = userdetails
        fields = ("email", "name", "contact", "password", "is_active", "is_staff", "is_superuser")

    def clean_password(self):
        return self.initial.get("password")

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("New passwords do not match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        new_pass = self.cleaned_data.get("password1")
        if new_pass:
            user.set_password(new_pass)
        if commit:
            user.save()
        return user

@admin.register(userdetails)
class UserDetailsAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ("id", "email", "name", "contact", "is_staff", "is_active", "superuser_label")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "name", "contact")
    ordering = ("id",)
    readonly_fields = ("last_login",)
    actions = [safe_delete_selected]

    fieldsets = (
        ("Login & Identity", {"fields": ("email", "name", "contact", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "contact", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )

    list_editable = ("is_active", "is_staff")

    def superuser_label(self, obj):
        if obj.is_superuser:
            return format_html('<strong style="color:green">ADMIN — ID:{}</strong>', obj.pk)
        return "-"
    superuser_label.short_description = "Superuser"

@admin.register(CarCompany)
class CarCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_tag')
    search_fields = ('name',)
    def image_tag(self, obj):
        if getattr(obj, 'image', None):
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Company Logo'

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'image_tag')
    list_filter = ('company',)
    search_fields = ('name', 'company__name')
    def image_tag(self, obj):
        if getattr(obj, 'image', None):
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Model Image'

@admin.register(CarPart)
class CarPartAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_model', 'price', 'quantity', 'is_available', 'image_tag')
    list_filter = ('car_model__company', 'car_model')
    search_fields = ('name', 'car_model__name')
    def is_available(self, obj):
        return obj.quantity > 0
    is_available.boolean = True
    def image_tag(self, obj):
        if getattr(obj, 'image', None):
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Part Image'

@admin.register(CarPartsPurchase)
class CarPartsPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'part', 'quantity', 'purchase_date', 'total_price', 'payment_status')
    list_filter = ('payment_status', 'purchase_date')
    search_fields = ('user__email', 'part__name')
    readonly_fields = ('purchase_date', 'total_price')
    date_hierarchy = 'purchase_date'

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'price', 'mileage', 'fuel_type', 'is_sold', 'created_at')
    list_filter = ('make', 'year', 'fuel_type', 'transmission', 'is_sold', 'created_at')
    search_fields = ('make', 'model', 'seller__name', 'location', 'contact_number')
    readonly_fields = ('created_at', 'updated_at', 'seller')
    list_editable = ('is_sold',)
    date_hierarchy = 'created_at'

@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('car', 'image_tag', 'is_primary')
    list_filter = ('car__make', 'car__model', 'is_primary')
    list_editable = ('is_primary',)
    readonly_fields = ('image_tag',)
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="100" />', obj.image.url)
        return "-"
    image_tag.short_description = "Preview"

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer_name', 'car', 'offer_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer_name', 'buyer_email', 'car__make', 'car__model')
    readonly_fields = ('created_at', 'updated_at')

