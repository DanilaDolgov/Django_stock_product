fieldsets = (
    (None, {'fields': ('email', 'password')}),
    ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'position')}),
    ('Permissions', {
        'fields': ('is_active', 'is_staff', 'is_superuser'),
    }),
    ('Important dates', {'fields': ('date_joined')}),
)
list_display = ('email', 'first_name', 'is_staff')
from django.test import TestCase

# Create your tests here.


print(fieldsets[3][1])