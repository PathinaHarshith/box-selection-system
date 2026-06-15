from django.contrib import admin
from .models import Box, Product, Order, OrderItem

@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'length', 'width', 'height', 'max_weight_capacity', 'cost')
    search_fields = ('name',)
    list_filter = ('cost', 'max_weight_capacity')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku', 'name', 'length', 'width', 'height', 'weight')
    search_fields = ('sku', 'name')
    list_filter = ('weight',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'reference', 'created_at')
    search_fields = ('reference',)
    list_filter = ('created_at',)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity')
    search_fields = ('order__reference', 'product__sku')
    list_filter = ('quantity',)
