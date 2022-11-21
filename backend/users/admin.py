from django.contrib import admin

from .models import User


@admin.register(User)
class UserClass(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_superuser'
    )
    list_filter = ('is_superuser',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    empty_value_display = '-empty-'