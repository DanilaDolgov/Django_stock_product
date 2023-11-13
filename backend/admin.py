from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from backend.models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями
    """
    model = User

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'position')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        })
    )
    list_display = ('email', 'first_name', 'is_staff')
    ordering = ['first_name']





@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    model = Shop
    list_display = ('name',)
    ordering = ['name']


#

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ('name',)
    ordering = ['name', 'shops']


#
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'category',)
    ordering = ['name', 'category']


#
#
@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    model = ProductInfo
    list_display = ('name', 'product', 'shop', 'quantity', 'price',
                    'price_rrc',)
    ordering = ['name', 'product', 'shop', 'quantity', 'price',
                'price_rrc']
#
#
# @admin.register(Parameter)
# class ParameterAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(ProductParameter)
# class ProductParameterAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(Contact)
# class ContactAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(ConfirmEmailToken)
# class ConfirmEmailTokenAdmin(admin.ModelAdmin):
#     list_display = ('user', 'key', 'created_at',)
