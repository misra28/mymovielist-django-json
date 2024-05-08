from django.contrib import admin
from . import models
from .views import get_movie_json

# Register your models here.
@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'username']
    search_fields = ['user']

@admin.register(models.ListEntry)
class ListEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie_id', 'title', 'rating', 'date_watched', 'comments']
    autocomplete_fields = ['user']
    
    def title(self, obj):
        return get_movie_json(obj.movie_id)['title']
    
    """def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _title=get_movie_json(self.movie_id),
        )
        return queryset"""