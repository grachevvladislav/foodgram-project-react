from django.contrib import admin

from .models import User, Follow


@admin.register(User)
class UserClass(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
        'is_superuser'
    )
    list_filter = ('is_superuser',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    empty_value_display = '-empty-'


@admin.register(Follow)
class FollowClass(admin.ModelAdmin):
    list_display = (
        'user', 'author',
    )
    search_fields = ('user', 'author',)
    empty_value_display = '-empty-'
