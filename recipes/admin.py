from django.contrib import admin
from .models import Recipe, Comment

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'slug', 'author', 'publish', 'status',
        'calories', 'cooking_time'  
    ]
    list_filter = ['status', 'created', 'publish', 'author']
    search_fields = ['title', 'ingredients', 'instructions']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'recipe', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']
