from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'username']
    search_fields = ['user']

@admin.register(models.ListEntry)
class ListEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie_id', 'rating', 'date_watched', 'comments']
    autocomplete_fields = ['movie_id', 'user']