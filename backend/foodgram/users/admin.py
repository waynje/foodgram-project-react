from django.contrib import admin

from .models import User

EMPTY_VALUE = 'пусто'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'username', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    empty_value_display = EMPTY_VALUE
