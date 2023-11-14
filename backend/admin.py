from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from backend.models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ("email", "first_name", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'position')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),

    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
         ),
    )
    ordering = ['email']
    search_fields = ("email",)


admin.site.register(User, CustomUserAdmin)


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
