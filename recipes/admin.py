from django.contrib import admin
from .models import Recipe, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("name", "email", "body", "active")
    readonly_fields = ("created", "updated")

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    def tag_list(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())

    list_display = [
        'title', 'slug', 'author', 'publish', 'status',
        'calories', 'cooking_time', 'tag_list'
    ]
    list_filter = ['status', 'created', 'publish', 'author']
    search_fields = ['title', 'ingredients', 'instructions']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['-publish']
    inlines = [CommentInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'recipe', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']