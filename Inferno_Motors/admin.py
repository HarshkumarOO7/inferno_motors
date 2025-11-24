from django.contrib import admin
from django.utils.html import format_html
from .models import *

# Register userdetails model
@admin.register(userdetails)
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact')
    search_fields = ('name', 'email', 'contact')


@admin.register(CarCompany)
class CarCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_tag')
    search_fields = ('name',)

    def image_tag(self, obj):
        if getattr(obj, 'image', None):
            return format_html('<img src="{}" width="100" height="100" style="border-radius:5px;"/>', obj.image.url)
        return "-"
    image_tag.short_description = 'Company Logo'


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'image_tag')
    list_filter = ('company',)
    search_fields = ('name', 'company__name')

    def image_tag(self, obj):
        if getattr(obj, 'image', None):
            return format_html('<img src="{}" width="100" height="100" style="border-radius:5px;"/>', obj.image.url)
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
    is_available.short_description = 'Available'

    def image_tag(self, obj):
        if getattr(obj, 'image', None):
            return format_html('<img src="{}" width="100" height="100" style="border-radius:5px;"/>', obj.image.url)
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
    date_hierarchy = 'created_at'
    list_per_page = 20
    list_editable = ('is_sold',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('seller', 'make', 'model', 'year', 'price', 'mileage')
        }),
        ('Technical Details', {
            'fields': ('fuel_type', 'transmission', 'color', 'engine_capacity')
        }),
        ('Additional Information', {
            'fields': ('description', 'location', 'contact_number')
        }),
        ('Status & Dates', {
            'fields': ('is_sold', 'created_at', 'updated_at')
        }),
    )


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('car', 'image_tag', 'is_primary')
    list_filter = ('car__make', 'car__model', 'is_primary')
    search_fields = ('car__make', 'car__model')
    readonly_fields = ('image_tag',)
    list_editable = ('is_primary',)

    def image_tag(self, obj):
        if getattr(obj, 'image', None):
            return format_html('<img src="{}" width="150" height="100" style="object-fit: cover;"/>', obj.image.url)
        return "-"
    image_tag.short_description = 'Image Preview'

    fieldsets = (
        (None, {
            'fields': ('car', 'image', 'image_tag', 'is_primary')
        }),
    )


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer_name', 'car', 'offer_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer_name', 'buyer_email', 'car__make', 'car__model')
    readonly_fields = ('created_at', 'updated_at')

    def buyer_info(self, obj):
        return f"{obj.buyer_name} ({obj.buyer_email})"
    buyer_info.short_description = 'Buyer'
